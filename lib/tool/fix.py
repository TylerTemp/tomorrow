# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import re

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.bashlog import stdoutlogger, DEBUG
from lib.config.base import Config
from lib.db.jolla import Article
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)
config = Config()
config.auto_clean = False


def fix_article_new_md():
    tag = re.compile(r'\</?(?P<name>[^\s\\\>]+).*?\>')
    count = 0
    slugs = set()
    for each in Article.collection.find({}):

        content = each['content']

        tags = set()
        for match in tag.finditer(content):

            this_tag = match.groupdict()['name']

            tags.add(this_tag)

        if tags and 'video' in tags:
            count += 1
            slugs.add(each['slug'])
            logger.info('%s:\n %s', each['slug'], tags)

    logger.info(slugs)
    logger.info(count)


if __name__ == '__main__':
    # mkdir()
    # fix_jolla()
    fix_article_new_md()