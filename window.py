import os
import time
import subprocess
import logging
import json
import sys
import structpack
from collections import defaultdict

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
    try:
        app, window = line.split(':', 1)
    except:
        import traceback
        traceback.print_exc()
        return 'ERROR', line
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
            entry = next

        if not next == entry:
            yield entry
            entry = next


def log():
    for entry in get_entries():
        log.info('Entry:' + json.dumps(entry.pack()))


def load_entries(inp):
    for line in inp:
        entry_json = line.split('Entry:', 1)[1]
        entry_data = json.loads(entry_json)
        entry = Entry.load(entry_data)
        yield entry


def display_time(d, t):
    h = d / 60 / 60
    m = d / 60 % 60
    p = d * 100.0 / t
    return '%2dh %2dm (%2d%%)' % (h, m, p)


def stats(entries):
    time = defaultdict(lambda:defaultdict(int))
    app_time = defaultdict(int)
    total = 0
    for e in entries:
        d = e.duration()
        total += d
        app_time[e.app] += d
        time[e.app][e.window] += d

    for app, d in sorted(app_time.items(), reverse=True):
        if d < 5 * 60:
            continue
        print '### %-50s ### %s' % (app, display_time(d, total))
        for window, d in sorted(time[app].items(), reverse=True):
            if d < 60:
                continue
            print '        %-50s %s' % (window[:50], display_time(d, total))
        print



if __name__ == '__main__':
    if len(sys.argv) == 2:
        stats(load_entries(file(sys.argv[1])))

    else:
        log()



















