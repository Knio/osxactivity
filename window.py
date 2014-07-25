import os
import time
import subprocess
import logging
import json
from collections import namedtuple

log = logging.getLogger()

logging.basicConfig(
    level=logging.DEBUG,
    # format='%(message)s',
    datefmt='%Y-%m-%d %H:%M:%s',
    filename='logs/window.log',
)

def get_idle_time():
    import Quartz
    idle = Quartz.CoreGraphics.CGEventSourceSecondsSinceLastEventType(1, 0xFFFFFFFF)
    return idle

def get_active_window():
    line = subprocess.check_output('osascript window.scpt', stderr=subprocess.STDOUT, shell=True).strip()
    return line


Entry = namedtuple('Entry', ['time', 'app', 'window'])

while 1:
    time.sleep(5)

    idle = get_idle_time()
    if idle > 15:
        continue

    app, window = get_active_window().split(':', 1)

    entry  = Entry(
        time=int(time.time()),
        app=app,
        window=window
    )

    log.info('Entry:' + json.dumps(entry))