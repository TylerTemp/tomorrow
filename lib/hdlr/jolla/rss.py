import logging
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:
    from email.utils import formatdate
except ImportError:
    from email.Utils import formatdate

from lib.db.jolla import Article, User
from .base import BaseHandler


class RssHandler(BaseHandler):
    logger = logging.getLogger('jolla.rss')

    def get(self):
        self.set_header('Content-Type', 'application/rss+xml; charset="utf-8"')
        return self.render(
            'jolla/rss.xml',
            host=self.config.jolla_host,
            time_str=formatdate,
            md2html=self.md2html,
            articles=self.get_articles(Article.all_shown(limit=5))
        )

    def get_articles(self, result):
        for each in result:
            a = Article()
            a.update(each)
            a.author = User(each['author'])
            yield a