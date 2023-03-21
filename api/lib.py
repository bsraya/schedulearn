import csv
import config
import docker
import subprocess
from datetime import datetime
from dataclasses import dataclass
from functools import total_ordering

@total_ordering
@dataclass(frozen=True, order=True)
class Gpu:
    server: str
    uuid: str
    id: int
    name: str
    utilization: float
    memory_free: int
    memory_used: int
    memory_total: int
    timestamp: datetime

    def __str__(self):
        return f"{self.server},{self.uuid},{self.id},{self.name},{self.utilization},{self.memory_free},{self.memory_used},{self.memory_total},{self.timestamp}"

@dataclass
class Destination:
    server: str
    gpus: list[Gpu]

def get_docker_client(server: str) -> docker.DockerClient:
    if server == "gpu3":
        return config.GPU3_DOCKER_CLIENT
    elif server == "gpu4":
        return config.GPU4_DOCKER_CLIENT
    elif server == "gpu5":
        return config.GPU5_DOCKER_CLIENT


def get_gpus() -> list[Gpu]:
    """
        Iterate through each server and returns a list of all graphics cards across all servers.
        Args:
            None
        
        Return:
            A list containing object of GPU class with the following structure.
    """
    gpus: list[Gpu] = []
    for server in ['gpu3', 'gpu4', 'gpu5']:
        result = subprocess.run(
            f"ssh {server} nvidia-smi --query-gpu=uuid,gpu_name,utilization.gpu,memory.free,memory.used,memory.total --format=csv,noheader,nounits".split(' '), 
            stdout = subprocess.PIPE
        ).stdout.decode('utf-8').splitlines()
        
        for i, stat in enumerate(csv.reader(result, delimiter=',')):
            gpus.append(
                Gpu(
                    server=server, 
                    uuid=stat[0], 
                    id=f"{i}",
                    name=stat[1], 
                    utilization=float(stat[2].strip('%')), 
                    memory_free=int(stat[3]),
                    memory_used=int(stat[4]),
                    memory_total=int(stat[5]),
                    timestamp=datetime.now()
                )
            )
    return gpus


def get_available_gpus_at(destination_server: str, required_gpus: int | None) -> Destination:
    """
        Acquire a list of available GPUs at the specified destination server.
        Args:
            destination_server (str): The name of the destination server
            required_gpus (int | None): The number of GPUs required for the job
        
        Return:
            Destination: An object of Destination class
            Destination.server: The name of the destination server
            Destination.gpus: A list of IDs of available GPUs at the destination server
    """
    destination = Destination(server=destination_server, gpus=[])
    for gpu in get_gpus():
        if gpu.server == destination_server and gpu.memory_usage < 50 and len(destination.gpus) < required_gpus:
            destination.gpus.append(gpu.id)
    return destination


def log_system_status(filename: str) -> None:
    with open(filename, 'a') as f:
        gpus = get_gpus()
        if f.tell() == 0:
            f.write(
                f"time,{','.join([gpu.id for gpu in gpus])}\n"
            )
        else: 
            f.write(
                f"{datetime.now()},{','.join([str(gpu.memory_usage) for gpu in gpus])}\n"
            )