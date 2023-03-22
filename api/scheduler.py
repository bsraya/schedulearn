import heapq
import logging
import database as db
from lib import get_gpus
from sqlmodel import Session, select, col

def OASiS(required_gpus: int, strategy: str = "best_fit") -> dict | None:
    gpus = get_gpus()
    if not gpus:
        return {'server': None, 'gpus': []}
    result = {'server': None, 'gpus': []}
    
    if strategy == "best_fit":
        for server in ['gpu3', 'gpu4', 'gpu5']:
            result = {'server': None, 'gpus': []}
            available_gpus = [gpu for gpu in gpus if gpu.server == server and gpu.utilization < 90]
            if len(available_gpus) > len(result['gpus']):
                result['server'] = server
                for gpu in available_gpus[:required_gpus]:
                    result['gpus'].append(gpu.id)
        if len(result['gpus']) >= required_gpus:
            return result
    elif strategy == "first_fit":
        for server in ['gpu3', 'gpu4', 'gpu5']:
            available_gpus = [gpu for gpu in gpus if gpu.server == server and gpu.utilization < 90]
            if len(available_gpus) >= required_gpus:
                result['server'] = server
                for gpu in available_gpus[:required_gpus]:
                    result['gpus'].append(gpu.id)
                return result
    else:
        raise ValueError("Invalid strategy")
    
    return {'server': None, 'gpus': []}

def Optimus(required_gpus: int) -> dict | None:
    server = 'gpu3'
    gpus = get_gpus()

    if not gpus:
        return {'server': None, 'gpus': []}

    heap = [(gpu.memory_free, gpu) for gpu in gpus if gpu.utilization < 90 and gpu.server == server]
    heapq.heapify(heap)

    # check if the heap has enough gpus
    if len(heap) < required_gpus:
        return {'server': None, 'gpus': []}

    result = {'server': server, 'gpus': []}
    for _ in range(required_gpus):
        _, gpu = heapq.heappop(heap)
        result['gpus'].append(gpu.id)

    return result


def FIFO(required_gpus: int) -> dict | None:
    for server in ['gpu3', 'gpu4', 'gpu5']:
        gpus = get_gpus()
        available = [gpu for gpu in gpus if gpu.server == server and gpu.utilization < 90]
        if len(available) >= required_gpus:
            result = {'server': server, 'gpus': []}
            for gpu in available[:required_gpus]:
                result['gpus'].append(gpu.id)
            return result
    return {'server': None, 'gpus': []}


def RoundRobin(required_gpus: int) -> dict | None:
    result = {"server": "", "gpus": []}
    with Session(db.engine) as session:
        last_server = session.exec(
            select(db.Schedulearn)
            .where(col(db.Schedulearn.configuration) == "last_server")
        ).first()

    result['server'] = last_server.value
    gpus = get_gpus()

    available = [gpu for gpu in gpus if gpu.server == result['server']]

    for gpu in available[:required_gpus]:
        result['gpus'].append(gpu.id)

    with Session(db.engine) as session:
        last_server = session.exec(
            select(db.Schedulearn)
            .where(col(db.Schedulearn.configuration) == "last_server")
        ).first()
        next_server = session.exec(
            select(db.Schedulearn)
            .where(col(db.Schedulearn.configuration) == "next_server")
        ).first()

        last_server.value = next_server.value
        if next_server.value == 'gpu3':
            next_server.value = 'gpu4'
        elif next_server.value == 'gpu4':
            next_server.value = 'gpu5'
        elif next_server.value == 'gpu5':
            next_server.value = 'gpu3'
        session.commit()

    # if there are enough gpus, return the server and the gpus
    if len(available) >= required_gpus:
        logging.info(f"RoundRobin: {result}")
        return result
    else:
        return None