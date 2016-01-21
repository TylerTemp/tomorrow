import tornado.web
import logging

from .base import BaseHandler

from lib.db.tomorrow import Article, User
from lib.tool.md import md2html

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
            author=User(article.author),
            md2html=md2html
        )
