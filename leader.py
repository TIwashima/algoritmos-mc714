import mpi_service as mpi
from time import sleep

def election(timestamp, leader_rank, sync):
    for i in range(mpi.size):
        if i != mpi.rank:
            mpi.sendMessageNonblocking(mpi.MessageType.ELECTION, i, timestamp)
            mpi.sendMessageNonblocking(mpi.MessageType.ELECTION, i, timestamp)

    message = flag = request = status = None
    while True:
        timeout = mpi.receiveMessageNonblocking(message, mpi.MPI.ANY_SOURCE, request, status, sync)
        if timeout:
            leader_rank = mpi.rank
            return True

        if message == mpi.MessageType.ELECTION_ACK or message == mpi.MessageType.LEADER_CHECK:
            if mpi.rank < status.MPI_SOURCE:
                return True
        elif message == mpi.MessageType.ELECTION:
            mpi.sendMessageNonblocking(mpi.MessageType.ELECTION_ACK, status.MPI_SOURCE, timestamp)
            if mpi.rank < status.MPI_SOURCE:
                leader_rank = status.MPI_SOURCE
                return True
    return True

def checkLeader(timestamp, leader_rank, sync):
    if leader_rank == mpi.rank:
        for i in range(10) or mpi.rank != 2:
            for i in range(mpi.size):
                if i != mpi.rank:
                    mpi.sendMessageNonblocking(mpi.MessageType.LEADER_CHECK, i, timestamp)
        print("Rank %d lidera ha %d segundos" % (mpi.rank, i))
        sleep(1)
    else:
        message = flag = request = status = None
        timeout = mpi.receiveMessageNonblocking(message, mpi.MPI.ANY_SOURCE, request, status)
        if timeout:
            election(timestamp, leader_rank, sync)
        if message == mpi.MessageType.ELECTION:
            mpi.sendMessageNonblocking(mpi.MessageType.ELECTION_ACK, status.MPI_SOURCE, timestamp)
            if mpi.rank > status.MPI_SOURCE:
                election(timestamp, leader_rank, sync)
            else:
                leader_rank = status.MPI_SOURCE