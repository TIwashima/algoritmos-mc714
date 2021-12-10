import mpi_service as mpi
import mutex
import leader

def tick(timestamp, increment):
    timestamp += increment

def sync(timestamp, increment, time):
    timestamp = timestamp if timestamp > time else time
    timestamp += 1

def join(timestamp):
    if mpi.rank == 0:
        input()
        mpi.sendMessage(mpi.MessageType.JOIN, 1, timestamp)
        mpi.sendMessage(mpi.MessageType.JOIN, 1, timestamp)
    else:
        message = None
        while True:
            mpi.receiveMessage(message, 0)
            if message == mpi.JOIN:
                break

if __name__ == "__main__":
    timestamp = 0
    increment = 1 << mpi.rank
    leader_rank = mpi.size - 1
    tick(timestamp, increment)
    
    # Lamport
    print("Rank %s timestamp %d" % (mpi.rank, timestamp))
    for i in range(2):
        if mpi.rank == 0:
            message = None
            mpi.sendMessage(mpi.MessageType.SYNC, 1, timestamp)
            mpi.receiveMessage(message, 2, sync)
        if mpi.rank == 1:
            message = None
            mpi.receiveMessage(message, 0, sync)
            mpi.sendMessage(mpi.MessageType.SYNC, 2, timestamp)
        if mpi.rank == 2:
            message = None
            mpi.receiveMessage(message, 1, sync)
            mpi.sendMessage(mpi.MessageType.SYNC, 0, timestamp)
    print("Rank %s timestamp %d" % (mpi.rank, timestamp))
    join(timestamp)

    # Mutex
    tick(timestamp, increment)
    if mpi.rank == mutex.COORD_RANK:
        mutex.startReceiving(timestamp)
    else:
        mutex.request(timestamp, sync)
        for i in range(10):
            print("Rank %d possui o mutex" % mpi.rank)
        mutex.free(timestamp)
        mutex.stopReceiving(timestamp)
    join(timestamp)
    
    # Leader
    while True:
        leader.checkLeader(timestamp, leader_rank, sync)
        if mpi.rank == 2:
            print("Encerrando rank 2")
            break
    join()