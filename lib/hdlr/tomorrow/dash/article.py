# coding: utf-8
import tornado.web
import logging
from bson.objectid import ObjectId
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.db.tomorrow import Article
from .base import BaseHandler


class ArticleHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.dash.article')

    @tornado.web.authenticated
    def get(self):

        return self.render(
            'tomorrow/dash/article.html',
            articles=Article.find({}),
            quote=quote,
        )

    @tornado.web.authenticated
    def post(self):
        self.check_xsrf_cookie()

        _id = ObjectId(self.get_argument('_id'))
        article = Article.find_one({'_id': _id})
        assert article, '%s does not exist' % _id