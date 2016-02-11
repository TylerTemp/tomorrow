# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import re

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.config.base import Config
from lib.db.jolla import User as JUser
from lib.db.tomorrow import User
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)
config = Config()
config.auto_clean = False

def fix_my_account():
    tu = User('TylerTemp')
    _id = tu._id
    ju = JUser.by_source_id(JUser.TOMORROW, _id)
    assert ju, 'ju can not be new'
    logger.debug(ju._id)
    ju.type = ju.ROOT
    ju.save()

if __name__ == '__main__':
    fix_my_account()