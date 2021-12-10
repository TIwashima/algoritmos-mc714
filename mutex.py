import mpi_service as mpi
import threading, queue

COORD_RANK = 1

receiving = False
queue = queue.Queue()
busy = False

def receive(timestamp):
    message = None
    while receiving:
        mpi.receiveMessage(message, mpi.MPI.ANY_SOURCE, timestamp)
        
        if message ==  mpi.MessageType.MUTEX_REQUEST:
            if not busy:
                busy = True
                mpi.sendMessage(message, mpi.MPI.Status.MPI_SOURCE, timestamp)
            else:
                queue.put(mpi.MPI.Status.MPI_SOURCE)
        elif message == mpi.MessageType.MUTEX_FREE:
            if queue.empty():
                busy = True
            else:
                mpi.sendMessage(mpi.MessageType.MUTEX_REQUEST, queue.get(), timestamp)
        elif message == mpi.MessageType.STOP_RECEIVING:
            if queue.empty() and not busy:
                receiving = False

def startReceiving(timestamp):
    receiving = True
    receive(timestamp)

def stopReceiving(timestamp):
    mpi.sendMessage(mpi.MessageType.STOP_RECEIVING, COORD_RANK, timestamp)

def request(timestamp, sync):
    mpi.sendMessage(mpi.MessageType.MUTEX_REQUEST, COORD_RANK, timestamp)
    message = None
    mpi.receiveMessage(message, COORD_RANK, sync)
    return message

def free(timestamp):
    sendMessage(mpi.MessageType.MUTEX_FREE, COORD_RANK, timestamp)