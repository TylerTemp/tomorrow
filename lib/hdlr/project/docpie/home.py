import logging

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.project.docpie.home')


class HomeHandler(BaseHandler):

    def get(self):
        info = Article('docpie_home').get()
        if self.locale.code[:2].lower() == 'zh':
            article = info['zh']
        else:
            article = info['en']
        article['content'] = md2html(article['content'])

        return self.render(
            'project/docpie/home.html',
            article=article
        )
