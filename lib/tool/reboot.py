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
config.autodelete = False
cfg = config.Config()
mainfile = os.path.join(rootdir, 'main.py')


def run(argv):    # won't wait
    args = ['python', mainfile]
    args.extend(argv)
    logger.info('start: %s', args)
    return sp.Popen(args)


def main():
    if not os.path.exists(cfg.info_path):
        logger.error('file(%s) not exits. Start directly')
        for port in range(8001, 8005):
            args = ['-p', str(port)]
            args.extend(sys.argv[1:])
            run(args)
        else:
            logger.info('done')
            return

    with FileLock(cfg.info_path),\
            open(cfg.info_path, 'r+', encoding='utf-8') as f:
        obj = json.load(f)

        if 'secret' in obj:
            f.seek(0)
            f.truncate()
            json.dump({'secret': obj['secret']}, f)
        else:
            os.unlink(cfg.info_path)

    if 'pid2port' in obj:
        for pid, port in obj['pid2port'].items():
            sub = sp.call(['kill', pid])    # wait and check
            if sub != 0:
                logger.error('failed to kill pid %s of port %s', pid, port)
                continue

            logger.info('killed pid %s, port %s', pid, port)

            args = ['-p', str(port)]
            args.extend(sys.argv[1:])
            run(args)
            time.sleep(1)    # wait process to fully run
    else:
        logger.info('no port to kill, start new')
        for port in range(8001, 8005):
            args = ['-p', str(port)]
            args.extend(sys.argv[1:])
            run(args)
        else:
            logger.info('done')
            return


if __name__ == '__main__':
    main()
