# coding: utf-8
# this file is to adjust the data in database

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.db.tomorrow import User
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)

def strip_user():
    for each in User.find({}):
        info = each.__info__
        logger.info(info)

        if 'user' in info:
            info['name'] = info.pop('user')
        if 'active' in info and info['active'] is not True:
            info['active'] = True

        info.pop('for_', None)
        info.pop('show_email', None)
        info.pop('intro', None)
        info.pop('donate', None)
        each.save()


if __name__ == '__main__':
    strip_user()
