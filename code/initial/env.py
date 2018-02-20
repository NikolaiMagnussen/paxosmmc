import signal
import sys
import time
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from replica import Replica
from timing import Timing
from utils import Config, Command, ReconfigCommand, WINDOW

NACCEPTORS = 3
NREPLICAS = 2
NLEADERS = 2
NREQUESTS = 10
NCONFIGS = 2


class Env:
    def __init__(self, max_clients=NREQUESTS):
        self.max_clients = max_clients
        self.procs = {}
        print(("Max clients: {}".format(self.max_clients)))

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
        for i in range(NACCEPTORS):
            pid = "acceptor %d.%d" % (c, i)
            Acceptor(self, pid)
            initialconfig.acceptors.append(pid)
        for i in range(NLEADERS):
            pid = "leader %d.%d" % (c, i)
            Leader(self, pid, initialconfig)
            initialconfig.leaders.append(pid)
        for i in range(self.max_clients):
            pid = "client %d.%d" % (c, i)
            for r in initialconfig.replicas:
                cmd = Command(pid, 0, "operation %d.%d" % (c, i))
                self.sendMessage(r, RequestMessage(pid, cmd))
                time.sleep(1)

        for c in range(1, NCONFIGS):
            print(("\nConfig: {}".format(c)))
            # Create new configuration
            config = Config(initialconfig.replicas, [], [])
            for i in range(NACCEPTORS):
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
            for i in range(self.max_clients):
                pid = "client %d.%d" % (c, i)
                print(pid)
                for r in config.replicas:
                    cmd = Command(pid, 0, "operation %d.%d" % (c, i))
                    self.sendMessage(r, RequestMessage(pid, cmd))
                    time.sleep(1)
            print("Shits")

    def terminate_handler(self, signal, frame):
        self._graceexit()

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        return


def main(max_clients):
    e = Env(max_clients)
    with Timing("kake"):
        e.run()
        signal.signal(signal.SIGINT, e.terminate_handler)
        signal.signal(signal.SIGTERM, e.terminate_handler)
        print("Waiting for processes to finish")
        signal.pause()
    print("\nJeg er ferdig!\n")


if __name__ == '__main__':
    print(("{}".format(sys.argv)))
    if len(sys.argv) < 2:
        print(("{} size=<size>".format(sys.argv[0])))
        sys.exit(0)
    else:
        main(int(sys.argv[1].split("=")[1]))
