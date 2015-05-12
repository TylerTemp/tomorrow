'''
Run this directly to start/reboot the server
This depends on /tmp/tomorrow.pid file
'''
import os
import sys
import json
import time
import subprocess as sp

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.filelock import FileLock
from lib.tool.minsix import open
from lib.tool import bashlog
from lib import config
sys.path.pop(0)

logger = bashlog.stdoutlogger(None, bashlog.DEBUG, True)
config.auto_clean = False
cfg = config.Config()
mainfile = os.path.join(rootdir, 'main.py')


def run(argv):    # won't wait
    args = ['python', mainfile]
    args.extend(argv)
    logger.info('start: %s', args)
    return sp.Popen(args)


def directly_run(ports):
    for port in ports:
        args = ['-p', str(port)]
        args.extend(sys.argv[1:])
        run(args)


def main():
    if not os.path.exists(cfg.pids_file):
        logger.error('file(%s) not exits. Start directly', cfg.pids_file)
        directly_run(cfg.ports)
        logger.info('done')
        return

    with FileLock(cfg.pids_file),\
            open(cfg.pids_file, 'r+', encoding='utf-8') as f:
        val = f.read()
        if not val:
            return directly_run(cfg.ports)

        pid2port = json.loads(val)

    os.unlink(cfg.pids_file)

    port2pid = {port: pid for pid, port in pid2port.items()}

    all_ports = cfg.ports
    reboot_ports = all_ports.intersection(port2pid)
    new_ports = all_ports.difference(port2pid)
    kill_ports = set(port2pid).difference(all_ports)

    directly_run(new_ports)
    for reboot in reboot_ports:
        sub = sp.call(['kill', port2pid[reboot]])
        if sub != 0:
            logger.error('failed to kill pid %s of port %s',
                         port2pid[reboot], reboot)
            continue
        run(['-p', str(reboot)] + sys.argv[1:])
        logger.debug('sleep %s', cfg.sleep)
        time.sleep(cfg.sleep)

    for kill in kill_ports:
        sub = sp.call(['kill', pid])
        if sub != 0:
            logger.error('failed to kill pid %s of port %s', pid, port)
            continue


if __name__ == '__main__':
    main()
