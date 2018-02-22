import time
from process import Process
from message import RequestMessage
from utils import Command
from timing import Timing


class Client(Process):
    def __init__(self, env, id, replicas, max_requests=10):
        Process.__init__(self, env, id)
        self.replicas = replicas
        self.max_requests = max_requests
        self.env.addProc(self)

    def body(self):
        print(f"Here I am:  {self.id}")
        i = 1
        while i < self.max_requests:
            cmd = Command(str(self), i, f"operation {self.id}")

            with Timing("Time for a single proposal to go through"):
                for replica in self.replicas:
                    self.sendMessage(replica, RequestMessage(f"{self.id}", cmd))
                msg = self.getNextMessage()
                print(f"{self.id} got mail: {msg}")
                print(f"{int(msg)} != {i} -> {int(msg) != i}")
                while int(msg) != i:
                    msg = self.getNextMessage()
                    print(f"{self.id} got mail: {msg}")
                    print(f"{int(msg)} != {i} -> {int(msg) != i}")
                print(f"Continuing: i = {i+1}")

            i += 1

        print(f"Bye from {self.id}")
