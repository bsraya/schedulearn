import csv
import config
import docker
import subprocess
from datetime import datetime
from dataclasses import dataclass
import concurrent.futures

@dataclass(frozen=True)
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


def get_docker_client(server: str) -> docker.DockerClient:
    if server == "gpu3":
        return config.GPU3_DOCKER_CLIENT
    elif server == "gpu4":
        return config.GPU4_DOCKER_CLIENT
    elif server == "gpu5":
        return config.GPU5_DOCKER_CLIENT


def get_gpus() -> list[Gpu]:
    gpus = []
    servers = ['gpu3', 'gpu4', 'gpu5']
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit SSH requests for all servers asynchronously
        futures = {executor.submit(get_gpu_stats, server): server for server in servers}

        # Wait for all SSH requests to complete and process results
        for future in concurrent.futures.as_completed(futures):
            server = futures[future]
            result = future.result()
            
            for i, stat in enumerate(csv.reader(result, delimiter=',')):
                gpus.append(
                    Gpu(
                        server=server, 
                        uuid=stat[0], 
                        id=f"{i}",
                        name=stat[1][1:],
                        utilization=float(stat[2].strip('%')), 
                        memory_free=int(stat[3]),
                        memory_used=int(stat[4]),
                        memory_total=int(stat[5]),
                        timestamp=datetime.now()
                    )
                )
    return gpus


def get_gpu_stats(server):
    return subprocess.run(
        f"ssh {server} nvidia-smi --query-gpu=uuid,gpu_name,utilization.gpu,memory.free,memory.used,memory.total --format=csv,noheader,nounits".split(' '), 
        stdout=subprocess.PIPE
    ).stdout.decode('utf-8').splitlines()


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

if __name__ == "__main__":
    print(get_gpus())