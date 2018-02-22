from process import Process
from timing import Timing
from message import ProposeMessage, DecisionMessage, RequestMessage
from utils import WINDOW, ReconfigCommand, Config


class Replica(Process):
    def __init__(self, env, id, config, total_requests, verbose):
        Process.__init__(self, env, id)
        self.slot_in = self.slot_out = 1
        self.total_requests = total_requests
        self.num_performed = 0
        self.verbose = verbose
        self.proposals = {}
        self.decisions = {}
        self.requests = []
        self.config = config
        self.env.addProc(self)

    def propose(self):
        while len(self.requests) != 0 and self.slot_in < self.slot_out+WINDOW:
            if self.slot_in > WINDOW and self.slot_in-WINDOW in self.decisions:
                if isinstance(self.decisions[self.slot_in-WINDOW],
                              ReconfigCommand):
                    repl, acpt, lead = self.decisions[self.slot_in-WINDOW]\
                                           .config.split(';')
                    self.config = Config(repl.split(','), acpt.split(','),
                                         lead.split(','))
                    print(self.id, ": new config:", self.config)
            if self.slot_in not in self.decisions:
                cmd = self.requests.pop(0)
                self.proposals[self.slot_in] = cmd
                for ldr in self.config.leaders:
                    self.sendMessage(ldr, ProposeMessage(self.id, self.slot_in,
                                                         cmd))
            self.slot_in += 1

    def perform(self, cmd):
        for s in range(1, self.slot_out):
            if self.decisions[s] == cmd:
                self.slot_out += 1
                return
            if isinstance(cmd, ReconfigCommand):
                self.slot_out += 1
                return

        if self.verbose:
            print(f"{self.id} : perform {self.slot_out} : {cmd.op}")
        client = " ".join(cmd.op.split()[1:])
        self.sendMessage(client, f"{self.slot_out}")
        self.slot_out += 1
        self.num_performed += 1

    def body(self):
        if self.verbose:
            print("Here I am: ", self.id)

        with Timing(f"Time to perform {self.total_requests}"):
            while self.num_performed < self.total_requests:
                msg = self.getNextMessage()
                if isinstance(msg, RequestMessage):
                    self.requests.append(msg.command)
                elif isinstance(msg, DecisionMessage):
                    self.decisions[msg.slot_number] = msg.command
                    while self.slot_out in self.decisions:
                        if self.slot_out in self.proposals:
                            if self.proposals[self.slot_out] !=\
                               self.decisions[self.slot_out]:
                                self.requests.append(
                                        self.proposals[self.slot_out])
                            del self.proposals[self.slot_out]
                        self.perform(self.decisions[self.slot_out])
                else:
                    print("Replica: unknown msg type")
                self.propose()
