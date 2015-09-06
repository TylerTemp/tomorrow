import tornado.web
import logging
import json

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.post')


class PostHandler(BaseHandler):

    def get(self, slug):
        article = Article(slug)
        if article.new:
            raise tornado.web.HTTPError(404, "post %s not found" % slug)

        info = article.get()
        zh = info.pop('content', None)
        en = info.pop('en', None)
        use_en = (self.locale.code[:2].lower() != 'zh')
        if use_en:
            if en:
                content = en
                is_en = True
            else:
                content = zh
                is_en = False
        else:
            if zh:
                content = zh
                is_en = False
            else:
                content = en
                is_en = True
        info['content'] = md2html(content)
        info['is_en'] = is_en
        return self.render(
            'post.html',
            **info
        )
