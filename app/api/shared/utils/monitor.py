import csv
import subprocess
from datetime import datetime
from dataclasses import dataclass
from functools import total_ordering
from sqlmodel import Session, select
from app.api.models.system import System


@total_ordering
@dataclass(frozen=True, order=True)
class Gpu:
    machine_id: int
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
        return f"{self.machine_id},{self.server},{self.uuid},{self.id},{self.name},{self.utilization},{self.memory_free},{self.memory_used},{self.memory_total},{self.timestamp}"


def get_scheduler(engine) -> str:
    with Session(engine) as session:
        return session.exec(select(System).where(System.configuration == "scheduler")).first().value


def get_gpus() -> list[Gpu]:
    """
        Iterate through each server and returns a list of all graphics cards across all servers.
        Args:
            None
        
        Return:
            A list containing object of GPU class with the following structure.
    """
    gpus: list[Gpu] = []
    for server_index, server in enumerate(['gpu3', 'gpu4', 'gpu5']):
        result = subprocess.run(
            f"ssh {server} nvidia-smi --query-gpu=uuid,gpu_name,utilization.gpu,memory.free,memory.used,memory.total --format=csv,noheader,nounits".split(' '), 
            stdout = subprocess.PIPE
        ).stdout.decode('utf-8').splitlines()
        
        for stat_index, stat in enumerate(csv.reader(result, delimiter=',')):
            gpus.append(
                Gpu(
                    machine_id=server_index+1,
                    server=server, 
                    uuid=stat[0], 
                    id=f"{stat_index}",
                    name=stat[1], 
                    utilization=float(stat[2].strip('%')), 
                    memory_free=int(stat[3]),
                    memory_used=int(stat[4]),
                    memory_total=int(stat[5]),
                    timestamp=datetime.now()
                )
            )
    return gpus

if __name__ == "__main__":
    gpus = get_gpus()
    for gpu in gpus:
        print(gpu)