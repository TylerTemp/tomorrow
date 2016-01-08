import tornado.web
import logging

from .base import BaseHandler
import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.tomorrow import Article, User
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blog.post')


class ArticleHandler(BaseHandler):

    def get(self, slug):
        lang = self.locale.code[:2].lower()
        article = Article(slug, lang)
        if not article:
            raise tornado.web.HTTPError(404, "post '%s' not found" % slug)

        return self.render(
            'tomorrow/blog/article.html',
            article=article,
            md2html=md2html
        )
