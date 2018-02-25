from process import Process
from message import RequestMessage
from utils import Command


class Client(Process):
    def __init__(self, env, id, replicas, num_requests, verbose):
        Process.__init__(self, env, id)
        self.replicas = replicas
        self.num_requests = num_requests
        self.verbose = verbose
        self.env.addProc(self)

    def body(self):
        if self.verbose:
            print(f"Here I am:  {self.id}")

        next_cmd = i = 0
        while i < self.num_requests:
            cmd = Command(str(self), i, f"operation {self.id}")
            for replica in self.replicas:
                self.sendMessage(replica,
                                 RequestMessage(f"{self.id}", cmd))

            msg = self.getNextMessage()
            while int(msg) <= next_cmd:
                msg = self.getNextMessage()

            next_cmd = int(msg)
            i += 1

        if self.verbose:
            print(f"{self.id} is leaving")
