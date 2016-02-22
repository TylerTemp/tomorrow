# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import re

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.db.jolla import Source, Article
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)


if __name__ == '__main__':
    pass