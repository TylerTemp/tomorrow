import tornado.web
import tornado.escape
import logging
import json
import time
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

from .base import BaseHandler
from lib.db.tomorrow import Article, User
from lib.tool.md import md2html


class HomeHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.blog.home')
    LIMIT = 10

    def get(self, page=1):
        this_page = int(page)

        limit = self.LIMIT
        offset = limit * (this_page - 1)
        collected = Article.all(offset, limit)

        total = collected.count()
        if total <= offset:
            raise tornado.web.HTTPError(404, 'Empty page %s' % page)
        has_next_page = (this_page * limit < total)

        article_and_author = self.parse_posts(collected)

        return self.render(
            'tomorrow/blog/home.html',
            article_and_author=article_and_author,
            this_page=this_page,
            has_next_page=has_next_page,
            quote=quote,
            md2html=md2html,
            escape=tornado.escape.xhtml_escape
        )

    def parse_posts(self, collected):
        for each in collected:
            lang = self.locale.code[:2]
            article = Article(lang=lang)
            article.update(each)


            if article.support_lang() == lang:
                current_lang = None
            else:
                current_lang = article.support_lang()

            alternative_lang = article.other_lang()
            if alternative_lang != current_lang:
                article.alternative_lang = alternative_lang
            else: 
                article.alternative_lang = None
                
            article.current_lang = current_lang

            yield article, User(article.author, lang)