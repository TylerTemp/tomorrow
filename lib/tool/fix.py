# coding: utf-8
# this file is to adjust the data in database

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.config.base import Config
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)
config = Config()


def mkdir():
    root = config.root
    for folder in ('avatar', 'author'):
        path = os.path.join(root, 'static', folder)
        if not os.path.isdir(path):
            os.mkdir(path)


if __name__ == '__main__':
    mkdir()
