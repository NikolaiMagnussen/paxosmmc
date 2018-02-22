import signal
import sys
from argparse import ArgumentParser
from client import Client
from acceptor import Acceptor
from leader import Leader
from replica import Replica
from utils import Config

NREPLICAS = 1
NLEADERS = 1
NREQUESTS = 10


class Env:
    def __init__(self, quorum_size, conc_clients, verbose):
        self.conc_clients = conc_clients
        self.quorum_size = quorum_size
        self.verbose = verbose
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
            Replica(self, pid, initialconfig, self.conc_clients * NREQUESTS,
                    self.verbose)
            initialconfig.replicas.append(pid)
        for i in range(self.quorum_size):
            pid = "acceptor %d.%d" % (c, i)
            Acceptor(self, pid, self.verbose)
            initialconfig.acceptors.append(pid)
        for i in range(NLEADERS):
            pid = "leader %d.%d" % (c, i)
            Leader(self, pid, initialconfig, self.verbose)
            initialconfig.leaders.append(pid)
        for i in range(self.conc_clients):
            pid = f"client {c}.{i}"
            Client(self, pid, initialconfig.replicas, NREQUESTS, self.verbose)

    def terminate_handler(self, signal, frame):
        self._graceexit()

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        return


def main(quorum_size, conc_clients, verbose):
    e = Env(quorum_size, conc_clients, verbose)
    e.run()

    signal.signal(signal.SIGINT, e.terminate_handler)
    signal.signal(signal.SIGTERM, e.terminate_handler)
    signal.pause()


if __name__ == '__main__':
    parser = ArgumentParser(description="Run a Paxos cluster")
    parser.add_argument("-s", "--size", type=int, default=3,
                        help="Size of the Paxos cluster quorum")
    parser.add_argument("-c", "--concurrency", type=int, default=1,
                        help="Number of concurrently proposing clients")
    parser.add_argument("--verbose", help="Increase output verbosity",
                        action="store_true")

    args = parser.parse_args()
    main(args.size, args.concurrency, args.verbose)
