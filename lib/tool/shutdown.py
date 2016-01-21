'''
Run this directly to stop the server
This depends on /tmp/tomorrow.pid file
'''

import os
import sys
import json
import subprocess as sp

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.minsix import open
from lib.tool import bashlog
from lib.config.base import Config
sys.path.pop(0)

logger = bashlog.stdoutlogger(None, bashlog.DEBUG, True)
cfg = Config()
cfg.auto_clean = False


def main():
    if not os.path.exists(cfg.pids_file):
        return logger.error('file(%s) not exits.', cfg.pids_file)

    with open(cfg.pids_file, 'r+', encoding='utf-8') as f:
        piddict = json.load(f)
    os.unlink(cfg.pids_file)

    if piddict is None:
        logger.info('no port info, nothing to kill')
        return

    logger.info(piddict)

    for pid, port in piddict.items():
        sub = sp.call(['kill', pid])    # wait and check
        if sub != 0:
            logger.error('failed to kill pid %s of port %s', pid, port)
            continue

        logger.info('killed pid %s, port %s', pid, port)

    else:
        logger.info('all done')


if __name__ == '__main__':
    main()
