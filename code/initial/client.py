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
        #print(f"\tHere I am:  {self.id}")
        next_cmd = i = 0
        while i < self.max_requests:
            cmd = Command(str(self), i, f"operation {self.id}")
            #print(f"\t{self.id} sends command {cmd}")

            with Timing("Time for a single proposal to go through"):
                #print(f"\t{self.id} sends the new command!")
                for replica in self.replicas:
                    self.sendMessage(replica, RequestMessage(f"{self.id}", cmd))
                msg = self.getNextMessage()
                #print(f"\t{self.id} got mail: {msg}")
                #print(f"\t{int(msg)} <= {next_cmd} -> {int(msg) <= next_cmd} meaning the loop will {'' if int(msg) <= next_cmd else 'not'} be entered")
                while int(msg) <= next_cmd:
                    msg = self.getNextMessage()
                    #print(f"\t{self.id} got mail: {msg}")
                    #print(f"\t{self.id} {int(msg)} <= {next_cmd} -> {int(msg) <= next_cmd}")

            #print(f"\t{self.id} Got a message which is greater than or equal to the old one!")
            #print(f"\tUpdating {next_cmd} to {msg}")
            #print(f"\tContinuing: i = {i+1}")

            next_cmd = int(msg)
            i += 1

        #print(f"\n\t{self.id} is leaving because i={i} and number requests to send was {self.max_requests}")
        print(f"Bye from {self.id}")
