# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import shutil

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.config.base import Config
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)

root = Config().root
Config().auto_clean = False
static = os.path.join(root, 'static')


def fix_jolla_path():
    for name in ('author', 'avatar'):
        src = os.path.join(static, name)
        dis = os.path.join(static, 'jolla', name)
        logger.info('%s -> %s', src, dis)
        shutil.move(src, dis)


if __name__ == '__main__':
    fix_jolla_path()
