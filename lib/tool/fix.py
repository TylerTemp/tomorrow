# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import re

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.db.jolla import Article
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)

def fix_empty_tag():
    for each in Article.collection.find({}):
        old_tag = each.get('tag', [])
        tag = list(filter(lambda x: bool(x), old_tag))
        if old_tag != tag:
            logger.info('%s: %s -> %s', each['slug'], old_tag, tag)
            if not tag:
                each.pop('tag', None)
            else:
                each['tag'] = tag

            Article.collection.replace_one({'_id': each['_id']}, each)


if __name__ == '__main__':
    fix_empty_tag()
