from collections import namedtuple

WINDOW = 5
NUM_ACCEPTED_PROPOSALS = 0


class BallotNumber(namedtuple('BallotNumber', ['round', 'leader_id'])):
    __slots__ = ()

    def __str__(self):
        return f"BN({self.round},{self.leader_id})"


class PValue(namedtuple('PValue', ['ballot_number',
                                   'slot_number',
                                   'command'])):
    __slots__ = ()

    def __str__(self):
        return f"PV({self.ballot_number},{self.slot_number},{self.command})"


class Command(namedtuple('Command', ['client',
                                     'req_id',
                                     'op'])):
    __slots__ = ()

    def __str__(self):
        return f"Command({self.client},{self.req_id},{self.op})"


class ReconfigCommand(namedtuple('ReconfigCommand', ['client',
                                                     'req_id',
                                                     'config'])):
    __slots__ = ()

    def __str__(self):
        return f"ReconfigCommand({self.client},{self.req_id},{self.config})"


class Config(namedtuple('Config', ['replicas',
                                   'acceptors',
                                   'leaders'])):
    __slots__ = ()

    def __str__(self):
        return f"{','.join(self.replicas)},{','.join(self.acceptors)},\
                 {','.join(self.leaders)}"
