import tornado.web
import sys
import os
import atexit
import subprocess as sp
import logging
import time

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.minsix import open
from lib.tool import bashlog
sys.path.pop(0)

logger = bashlog.stdoutlogger(None, bashlog.DEBUG, True)
logger = bashlog.filelogger('/tmp/block.log', logger, bashlog.debug)

blackfile = open('/tmp/blacklist', 'r', encoding='utf-8')


def run():
    blackfile.seek(0)
    collect = set()
    for line in blackfile:
        line = line.strip()
        if line.count('.') != 3:
            continue
        collect.add(line)
    blackfile.seek(0)
    blackfile.truncate()
    for line in collect:
        sub = sp.call(['iptables', '-A', 'INPUT', '-s', 'line',  '-j', 'DROP'])
        if sub != 0:
            logger.error('failed : %', line)
        else:
            logger.info('blocked: %s', line)


def loop(scd):
    logger.info(os.getpid())
    while True:
        run()
        time.sleep(scd)


@atexit.register
def close():
    blackfile.close()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        loop(int(sys.argv[-1]))
    else:
        run()
