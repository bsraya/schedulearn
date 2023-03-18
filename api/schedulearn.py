import uuid
import datetime
import database as db
from lib import get_docker_client, get_gpus
from scheduler import FIFO
from sqlmodel import Session, select, col
from fastapi import BackgroundTasks

def migrate_job(job_id: int):
    with Session(db.engine) as session:
        job = session.exec(
            select(db.Job).where(col(db.Job.id) == job_id)
        ).one()
        kill_job(job_id)
        job.status = "Migrating"
        job.no_of_migrations += 1
        session.commit()
        session.refresh(job)

def scale_out_job(job_id: int):
    with Session(db.engine) as session:
        job = session.exec(
            select(db.Job).where(col(db.Job.id) == job_id)
        ).one()
        migrate_job(job_id)
        job.status = "ScalingOut"

        # get the server with the most free gpus
        flag = {"server": "", "gpus": []}
        for server in ['gpu3', 'gpu4', 'gpu5']:
            gpus = get_gpus()
            available = [gpu for gpu in gpus if gpu.server == server and gpu.utilization < 90]
            if len(available) > len(flag['gpus']):
                flag['server'] = server
                flag['gpus'] = [gpu.id for gpu in available]

        job.trained_at = flag['server']
        job.at_gpus = ','.join(flag['gpus'])
        session.commit()
        session.refresh(job)
        run_job(job_id, BackgroundTasks())

def run_job(new_job_id: int, background_tasks: BackgroundTasks):
    with Session(db.engine) as session:
        scheduling_algorithm = session.exec(
            select(db.Schedulearn)
            .where(col(db.Schedulearn.configuration) == "scheduling_algorithm")
        ).first()

        job = session.exec(
            select(db.Job).where(col(db.Job.id) == new_job_id)
        ).one()
        
        if job.no_of_migrations == 0 or scheduling_algorithm == "FIFO":
            available_resources = {"server": None, "gpus": []}
            while available_resources['server'] is None or len(available_resources['gpus']) < job.required_gpus:
                found = FIFO(job.required_gpus)
                if found['server'] and found['gpus']:
                    available_resources["server"] = found['server']
                    available_resources["gpus"] = found['gpus']
                    break
            job.trained_at = available_resources['server']
            job.at_gpus = ','.join(available_resources['gpus'])
            session.commit()
            session.refresh(job)

        job.container_name = f"{job.name.lower().replace(' ', '-')}-{uuid.uuid4()}"
        docker_client = get_docker_client(job.trained_at)
        container = docker_client.containers.run(
            name = job.container_name,
            image = job.container_image, 
            command = f"horovodrun -np {job.required_gpus} -H localhost:{job.required_gpus} {job.command}",
            shm_size = "1G",
            detach = True,
            environment = {
                "NVIDIA_VISIBLE_DEVICES": f"{job.at_gpus}",
            }
        )
        job.status = "Running"
        job.started_at = datetime.datetime.now()
        session.commit()
        session.refresh(job)

        status = container.wait()

        if status.get('StatusCode') == 0:
            job.completed_at = datetime.datetime.now()
            job.status = "Completed"
            session.commit()
            session.refresh(job)
            with open(f"output/{(job.type).lower()}/{job.container_name}.txt", "w") as f:
                f.write(container.logs().decode("utf-8"))
            
            if scheduling_algorithm == "ElasticFIFO":
                slowest_job = session.exec(
                    select(db.Job)
                    .where(col(db.Job.status) == "Running")
                    .where(col(db.Job.started_at) < datetime.datetime.now() - datetime.timedelta(minutes=2))
                    .order_by(col(db.Job.started_at).desc())
                ).first()

                # if doesnt exist, return
                if slowest_job:
                    scale_out_job(slowest_job.id)
                else:
                    return
        elif status.get('StatusCode') == 1 or status.get('StatusCode') == 2:
            container = docker_client.containers.get(job.container_name)

            if container:
                container.stop()
                container.remove()

            job.container_name = None
            job.completed_at = None
            job.status = "Error"
            session.commit()
            session.refresh(job)
            background_tasks.add_task(run_job, job.id, background_tasks)


def kill_job(id):
    with Session(db.engine) as session:
        job = session.exec(
            select(db.Job)
            .where(col(db.Job.id) == id)
        ).one()
        docker_client = get_docker_client(job.trained_at)
        container = docker_client.containers.get(job.container_name)

        if container:
            container.stop()
            container.remove()
            
        job.container_name = None
        job.completed_at = None
        job.status = "Suspended"
        session.commit()
        session.refresh(job)


def remove_job(id):
    with Session(db.engine) as session:
        job = session.exec(
            select(db.Job)
            .where(col(db.Job.id) == id)
        ).one()

    docker_client = get_docker_client(job.trained_at)
    container = docker_client.containers.get(job.container_name)

    if container: 
        container.remove()
    else:
        return

    session.delete(job)
    session.commit()