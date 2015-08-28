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
        for each in Article.find_trusted_jollas():
            info = each['transinfo']
            result = {
                'title': each['title'],
                'link': '//%s/%s/' % (cls.HOST, quote(each['url'])),
                'email': each['email'] if each['show_email'] else None,
                # 'img': info.get('cover', None) or info['headimg'],
                'descripition': (each['transinfo'].get('description', None)
                            or each['content'][:80] + '...'),
                'time': time.ctime(each['createtime'])
            }
            yield result
