#!/usr/bin/env python3
import time


class Timing(object):
    '''
    A timing object context, which allow you to easily time an event.
    Is used as such:

    with Timing("some message"):
        do_something()

    After do_something(), the context is ended, the timer is stopped
    and both the message and time will be printed.
    '''
    def __init__(self, msg=""):
        self.msg = msg

    def __enter__(self):
        self.start = time.perf_counter()

    def __exit__(self, *args):
        self.end = time.perf_counter()
        self.diff = self.end - self.start

        if self.msg == "":
            print(f"Timing completed in {self.diff:.2f} seconds")
        else:
            print(f"Timing: {self.msg} completed in {self.diff:.2f} seconds")
