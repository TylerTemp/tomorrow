import tornado.web
import tornado.escape
import logging
import time
try:
    from urllib.parse import quote
except ImportError:
    from urlparse import quote

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
# from lib.hdlr.base import BaseHandler
from lib.db import Article
from lib.config import Config
from lib.tool import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.rss')


class RssHandler(tornado.web.RequestHandler):
    HOST = Config().jolla_host

    def get(self):
        return self.render(
            'jolla/rss.xml',
            articles=self.get_tred_jolla()
        )

    @classmethod
    def get_tred_jolla(cls):
        for each in Article.display_jolla(limit=3):
            content = md2html(each['content'] or each.get('en'))
            img = each['cover'] or each['headimg']
            if img:
                content = '<img src="%s">%s' % (img, content)
            des = each['description']
            if not des:
                des = tornado.escape.xhtml_escape(content[:80]) + '...'
            else:
                des = md2html(des)
            result = {
                'title': each['title'],
                'link': '//%s/%s/' % (cls.HOST, quote(each['url'])),
                'author': each['author'],
                'descripition': des,
                'content': content,
                'time': time.ctime(each['createtime'])
            }
            yield result
