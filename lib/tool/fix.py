# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import re

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.db.jolla import Redirect, Article
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)

def fix_slug():
    for each in Article.find({'source': {'$exists': True}}):
        # link = each.source['link']
        # print(link)
        slug = each.slug
        source_title = each.source['title']
        if source_title.replace(' ', '-') == slug:
            link = each.source['link']
            last = link.split('/')[-2]
            logger.debug('%s ->%s', slug, last)
            each.slug = last
            each.save()
            r = Redirect(slug)
            r.target = last
            r.permanent = True
            r.save()


if __name__ == '__main__':
    fix_slug()