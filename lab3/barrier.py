import time
from threading import Semaphore

class Barrier:
    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = Semaphore(1)
        self.barrier = Semaphore(0)
        self.recycle = True

    def wait(self):
        self.mutex.acquire()
        if not self.recycle:
            return False
        self.count = self.count + 1
        if self.count == self.n: 
            for i in range(self.n):
                self.barrier.release()
                self.count = 0
        self.mutex.release()
        self.barrier.acquire()
        return self.recycle

    def stop(self):
        self.recycle = False
