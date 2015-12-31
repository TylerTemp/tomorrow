import tornado.web
import logging

from .base import BaseHandler
import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import Article, User
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blog.post')


class ArticleHandler(BaseHandler):

    def get(self, slug):
        article = Article(slug)
        if article.new:
            raise tornado.web.HTTPError(404, "post %s not found" % slug)

        info = article.get()
        zh = info.pop('zh', None)
        en = info.pop('en', None)
        is_en = self.locale.code[:2].lower() != 'zh'
        if zh and en:
            if is_en:
                info.update(en)
            else:
                info.update(zh)
        else:
            info.update(zh or en)
        info['is_en'] = is_en
        info['content'] = md2html(info['content'])
        info['id'] = info.pop('_id')
        author = info['author']
        if author is None:
            donate = None
        else:
            author_info = User(author).get()
            donate_info = author_info.pop('donate')
            if donate_info['show_in_article']:
                donate = (donate_info['old']
                          if donate_info['info']
                          else donate_info['new'])

        return self.render(
            'tomorrow/blog/article.html',
            donate=md2html(donate) if donate else None,
            **info
        )
