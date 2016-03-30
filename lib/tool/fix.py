# coding: utf-8
# this file is to adjust the data in database

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.db.tomorrow import Article
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)

def article_attr():
    for each in Article.find({}):
        info = each.__info__
        info.pop('show_email', None)
        info.pop('email', None)
        each.save()


if __name__ == '__main__':
    article_attr()
