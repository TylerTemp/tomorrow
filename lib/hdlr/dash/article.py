# coding: utf-8
import tornado.web
import logging
import json
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
from lib.hdlr.dash.base import its_myself
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.secure')


class ArticleHandler(BaseHandler):

    def get(self, user):

        return self.render(
            'dash/article.html',
            cc_license=Article.CC_LICENSE,
            pub_license=Article.PUB_LICENSE,
            articles=self.get_articles(self.current_user['user'])
        )

    def get_articles(self, user):
        for each in Article.find_by(user):
            each['id'] = str(each.pop('_id'))
            each['edit_time'] = self.format_time(each.pop('edittime'))
            each['create_time'] = self.format_time(each.pop('createtime'))
            if each['board'] == 'jolla':
                each['url'] = '/jolla/blog/%s' % each['url']
            yield each

    def format_time(self, t):
        if self.locale.code.startswith('en'):
            return time.ctime(t)
        return time.strftime('%Y年%m月%d日，%H:%M', time.localtime(t))
