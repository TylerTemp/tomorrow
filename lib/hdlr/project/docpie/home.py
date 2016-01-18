import logging

from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
from lib.db.base import Meta

logger = logging.getLogger('_docpie.home')


class HomeHandler(BaseHandler):

    def get(self):
        info = Meta('home', 'docpie')
        if self.locale.code[:2].lower() == 'zh':
            article = info.zh
        else:
            article = info.en

        article['content'] = md2html(article['content'])

        return self.render(
            'project/docpie/home.html',
            article=article
        )
