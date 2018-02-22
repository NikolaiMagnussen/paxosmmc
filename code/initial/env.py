import signal
import sys
import time
from argparse import ArgumentParser
from client import Client
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from replica import Replica
from timing import Timing
from utils import Config, Command, ReconfigCommand, WINDOW

NREPLICAS = 1
NLEADERS = 1
NCONFIGS = 2


class Env:
    def __init__(self, quorum_size, num_conc_clients):
        self.num_conc_clients = num_conc_clients
        self.quorum_size = quorum_size
        self.procs = {}

    def sendMessage(self, dst, msg):
        if dst in self.procs:
            self.procs[dst].deliver(msg)

    def addProc(self, proc):
        self.procs[proc.id] = proc
        proc.start()

    def removeProc(self, pid):
        del self.procs[pid]

    def run(self):
        initialconfig = Config([], [], [])
        c = 0

        for i in range(NREPLICAS):
            pid = "replica %d" % i
            Replica(self, pid, initialconfig)
            initialconfig.replicas.append(pid)
        for i in range(self.quorum_size):
            pid = "acceptor %d.%d" % (c, i)
            Acceptor(self, pid)
            initialconfig.acceptors.append(pid)
        for i in range(NLEADERS):
            pid = "leader %d.%d" % (c, i)
            Leader(self, pid, initialconfig)
            initialconfig.leaders.append(pid)
        for i in range(self.num_conc_clients):
            pid = f"client {c}.{i}"
            Client(self, pid, initialconfig.replicas, 10)

        '''
        for c in range(1, NCONFIGS):
            print(("\nConfig: {}".format(c)))
            # Create new configuration
            config = Config(initialconfig.replicas, [], [])
            for i in range(self.quorum_size):
                pid = "acceptor %d.%d" % (c, i)
                Acceptor(self, pid)
                config.acceptors.append(pid)
            for i in range(NLEADERS):
                pid = "leader %d.%d" % (c, i)
                Leader(self, pid, config)
                config.leaders.append(pid)
            # Send reconfiguration request
            for r in config.replicas:
                pid = "master %d.%d" % (c, i)
                cmd = ReconfigCommand(pid, 0, str(config))
                self.sendMessage(r, RequestMessage(pid, cmd))
                time.sleep(1)
            for i in range(WINDOW-1):
                pid = "master %d.%d" % (c, i)
                for r in config.replicas:
                    cmd = Command(pid, 0, "operation noop")
                    self.sendMessage(r, RequestMessage(pid, cmd))
                    time.sleep(1)
            #for i in range(self.num_conc_clients):
                #Client(self, i, c, config.replicas)
        '''

    def terminate_handler(self, signal, frame):
        self._graceexit()

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        return


def main(quorum_size, num_conc_clients):
    e = Env(quorum_size, num_conc_clients)
    with Timing("kake"):
        e.run()
        signal.signal(signal.SIGINT, e.terminate_handler)
        signal.signal(signal.SIGTERM, e.terminate_handler)
        print("Waiting for processes to finish")
        signal.pause()
    print("\nJeg er ferdig!\n")


if __name__ == '__main__':
    parser = ArgumentParser(description="Run a Paxos cluster")
    parser.add_argument("-s", "--size", type=int, default=3,
                        help="Size of the Paxos cluster quorum")
    parser.add_argument("-c", "--concurrency", type=int, default=1,
                        help="Number of concurrently proposing clients")

    args = parser.parse_args()
    with Timing("Total time to run shits"):
        main(args.size, args.concurrency)
