import os
import time
import subprocess
import logging
import json
import structpack
from collections import namedtuple

IDLE_TIME = 15
APP_TIME = 1

log = logging.getLogger()

logging.basicConfig(
    level=logging.DEBUG,
    # format='%(message)s',
    datefmt='%Y-%m-%d %H:%M:%s',
    filename='logs/window.log',
)


class Entry(structpack.msg):
    idle        = structpack.bool
    app         = structpack.str
    window      = structpack.str
    start_time  = structpack.int
    end_time    = structpack.int

    def __init__(self, idle=False, app='', window='', start_time=0, end_time=0):
        self.idle   = idle
        self.app    = app
        self.window = window
        self.start_time = int(start_time)
        self.end_time   = int(end_time)

    def __eq__(self, that):
        return \
            (self.idle, self.app, self.window) == \
            (that.idle, that.app, that.window)

    def duration(self):
        return self.end_time - self.start_time


def get_idle_time():
    import Quartz
    idle = Quartz.CoreGraphics.CGEventSourceSecondsSinceLastEventType(1, 0xFFFFFFFF)
    return idle


def get_active_window():
    line = subprocess.check_output('osascript window.scpt', stderr=subprocess.STDOUT, shell=True).strip()
    app, window = line.split(':', 1)
    return app, window


def get_entry():
    idle = get_idle_time() > IDLE_TIME
    if idle:
        app, window = ('IDLE', 'IDLE')
    else:
        app, window = get_active_window()
    return Entry(idle, app, window, time.time())


def get_entries():
    entry = get_entry()

    while 1:
        time.sleep(APP_TIME)
        entry.end_time = time.time()

        next = get_entry()
        if entry.duration() > 300:
            yield entry

        if not next == entry:
            yield entry
            entry = next



def main():
    for entry in get_entries():
        log.info('Entry:' + json.dumps(entry.pack()))


if __name__ == '__main__':
    main()



















