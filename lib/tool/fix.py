# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import shutil

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.db.jolla import Source, Article
from lib.db.tomorrow import User
from lib.config.base import Config
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)

def fix_source():
    for each in Source.find({'translated': {'$exists': True}}):
        trans = each.translated
        a = Article(trans)
        if not a:
            # logger.info(trans)
            new_link = each.link.split('/')[-2]
            logger.info(new_link)
            assert Article(new_link)
            each.translated = new_link
            each.save()


def fix_to_root():
    u = User('TylerTemp')
    assert u
    u.type = u.ROOT
    u.save()

def fix_tomorrow_uploader():
    Config().auto_clean = False
    root = Config().root
    static = os.path.join(root, 'static')
    source = os.path.join(static, 'upload')
    target = os.path.join(static, 'tomorrow')
    shutil.move(os.path.join(root, source), os.path.join(root, target))


if __name__ == '__main__':
    fix_source()
    fix_to_root()
    fix_tomorrow_uploader()
