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


if __name__ == '__main__':
    fix_source()