from mpi4py import MPI
from time import sleep

class MessageType:
    SYNC = 0
    MUTEX_REQUEST = 1
    MUTEX_FREE = 2
    STOP_RECEIVING = 3
    LEADER_CHECK = 4
    ELECTION = 5
    ELECTION_ACK = 6
    JOIN = 7

TIMEOUT = 5
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def sendMessage(message, dest, timestamp):
    if (dest >= size):
        return "Error: destination unknown"
    msg = [message, timestamp]
    return comm.Isend(msg, 2, MPI.INT, dest, 1, comm)

def sendMessageNonblocking(message, dest, timestamp):
    if (dest >= size):
        return "Error: destination unknown"
    request = None
    msg = [message, timestamp]
    return comm.Isend(msg, 2, MPI.INT, dest, 1, comm, request)

def receiveMessage(ret, src, sync):
    message = None
    fail = comm.recv(message, 2)
    if not fail:
        ret = message[0]
        timestamp = message[1]
        sync(timestamp)
    return fail

def receiveMessageNonblocking(ret, src, request, status, sync):
    message = []
    fail = comm.Irecv(message, 2, MPI.INT, src, 1, MPI.COMM_WORLD, request)
    flag = 0
    timeout = false
    
    i = 0
    while True:
        MPI.Test(request, flag, status)
        sleep(1)
        if (i+1 == TIMEOUT):
            timeout = True
            break
    if timeout:
        return "Error, timeout"

    if not fail:
        ret = message[0]
        timestamp = message[1]
        sync(timestamp)

    return fail


