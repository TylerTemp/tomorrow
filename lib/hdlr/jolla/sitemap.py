import logging
import datetime
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from lib.db.jolla import Article, User
from .base import BaseHandler


class SiteMapHandler(BaseHandler):
    logger = logging.getLogger('jolla.sitemap')

    def get(self):
        self.set_header('Content-Type', 'text/xml; charset="utf-8"')
        return self.render(
            'jolla/sitemap.xml',
            host=self.config.jolla_host,
            time_str=lambda t: datetime.datetime.fromtimestamp(
                t).strftime('%Y-%m-%dT%H:%M:%S'),
            articles=self.get_articles(Article.all_shown()),
            quote=quote
        )

    def get_articles(self, result):
        for each in result:
            a = Article()
            a.update(each)
            a.author = User(each['author'])
            yield a