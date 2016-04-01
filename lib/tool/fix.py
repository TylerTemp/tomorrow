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

u = re.compile(r'<u>(?P<content>.+?)</u>')

def fix_u():
    for each in Article.collection.find({}):
        content = each['content']
        result, times = u.subn(r'__\1__', content)
        if times:
            logger.info(each['slug'])
            each['content'] = result
            db_result = Article.collection.replace_one({'_id': each['_id']}, each)
            logger.info(db_result.matched_count)
        # if u:
        #     print(u)
        #     print(each['slug'])

if __name__ == '__main__':
    fix_u()
