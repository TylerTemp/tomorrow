import logging
import datetime
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:
    from email.utils import formatdate
except ImportError:
    from email.Utils import formatdate

from lib.db.jolla import Article, User
from lib.tool import md2html
from .base import BaseHandler

logger = logging.getLogger('jolla.rss')


class RssHandler(BaseHandler):

    def get(self):
        return self.render(
            'jolla/rss.xml',
            host=self.config.jolla_host,
            time_str=formatdate,
            md2html=md2html,
            articles=self.get_articles(Article.all_shown(limit=5))
        )

    def get_articles(self, result):
        for each in result:
            a = Article()
            a.update(each)
            a.author = User(each['author'])
            logger.debug(a.slug)
            yield a