import tornado.web
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
        for each in Article.find_trusted_jollas(limit=3):
            info = each['transinfo']
            content = md2html(each['content'])
            img = info.get('cover', None) or info['headimg']
            if img:
                content = '<img src="%s">%s' % (img, content)
            result = {
                'title': each['title'],
                'link': '//%s/%s/' % (cls.HOST, quote(each['url'])),
                'author': each['author'],
                # 'img': info.get('cover', None) or info['headimg'],
                'descripition': (each['transinfo'].get('description', None)
                            or each['content'][:80] + '...'),
                'content': content,
                'time': time.ctime(each['createtime'])
            }
            yield result
