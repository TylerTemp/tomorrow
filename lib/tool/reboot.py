'''
Run this directly to start/reboot the server
This depends on /tmp/tomorrow.pid file
'''
import os
import sys
import json
import time
import subprocess

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.filelock import FileLock
from lib.tool.minsix import open
from lib.tool import bashlog
from lib.config.base import Config
sys.path.pop(0)

logger = bashlog.stdoutlogger(None, bashlog.DEBUG, True)
cfg = Config()
cfg.auto_clean = False
mainfile = os.path.join(cfg.root, 'main.py')


def run(argv):    # won't wait
    args = ['python', mainfile]
    args.extend(argv)
    popen = subprocess.Popen(args, shell=False)
    pid = popen.pid
    logger.info('start on %s: %s', pid, args)
    return pid


def directly_run(ports):
    pid_2_port = {}
    for port in ports:
        args = ['-p', str(port)]
        args.extend(sys.argv[1:])
        pid = run(args)
        pid_2_port[pid] = port
    return pid_2_port


def main():
    with FileLock(cfg.pids_file),\
            open(cfg.pids_file, 'r+', encoding='utf-8') as f:
        val = f.read()
        if not val.strip():
            logger.debug('No running instance, starts directly on %s',
                         cfg.ports)
            pid_2_port = directly_run(cfg.ports)
            f.seek(0)
            f.truncate()
            json.dump(pid_2_port, f, indent=2)
            return

        running_pid_2_port = json.loads(val)

    all_ports = set(cfg.ports)
    reboot_pid_2_ports = {}
    kill_pid_2_ports = {}
    new_ports = all_ports.difference(running_pid_2_port.values())

    for old_pid, old_port in running_pid_2_port.items():
        if old_port in all_ports:
            reboot_pid_2_ports[old_pid] = old_port
        else:
            kill_pid_2_ports[old_pid] = old_port

    now_pid_2_port = directly_run(new_ports)

    for kill_pid, port in reboot_pid_2_ports.items():
        logger.debug('reboot port %s, kill %s', port, kill_pid)
        sub = subprocess.call(['kill', kill_pid])
        if sub != 0:
            logger.error('failed to kill pid %s of port %s',
                         kill_pid, port)
        else:
            new_pid = run(['-p', str(port)] + sys.argv[1:])
            logger.debug('sleep %s', cfg.wait_bootup)
            time.sleep(cfg.wait_bootup)
            now_pid_2_port[new_pid] = port

    for kill_pid, old_port in kill_pid_2_ports.items():
        logger.debug('kill %s on port %s', kill_pid, old_port)
        sub = subprocess.call(['kill', kill_pid])
        if sub != 0:
            logger.error('failed to kill pid %s of port %s',
                         kill_pid, old_port)

    logger.debug('currently pid to port: %s', now_pid_2_port)
    with open(cfg.pids_file, 'w', encoding='utf-8') as f:
        json.dump(now_pid_2_port, f, indent=2)

if __name__ == '__main__':
    main()
