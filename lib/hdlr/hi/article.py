import tornado.web
import logging
import time
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import Article
from lib.hdlr.hi.base import BaseHandler
from lib.hdlr.hi.base import ItsNotMyself
sys.path.pop(0)

logger = logging.getLogger('tomorrow.hi.article')


class ArticleHandler(BaseHandler):

    @ItsNotMyself('article/')
    def get(self, user):
        user_name = unquote(user)
        main_url = '/hi/' + user

        return self.render(
            'hi/article.html',
            main_url=main_url,
            user_name=user_name,
            articles=self.get_articles(user_name),
            act='article'
        )

    @ItsNotMyself('article')
    def get_articles(self, user):
        for each in Article.find_by(user):
            each['create_time'] = self.format_time(each['createtime'])
            each['edit_time'] = self.format_time(each['edittime'])
            each['create_time_attr'] = time.strftime(
                '%Y-%m-%dT%H:%M:%S',
                time.localtime(each.pop('createtime')))
            each['edit_time_attr'] = time.strftime(
                '%Y-%m-%dT%H:%M:%S',
                time.localtime(each.pop('edittime')))
            each['url'] = '/jolla/blog/%s/' % quote(each['url'])
            yield each

    def format_time(self, t):
        if self.locale.code.startswith('en'):
            return time.ctime(t)
        return time.strftime('%m月%d日，%H:%M', time.localtime(t))
