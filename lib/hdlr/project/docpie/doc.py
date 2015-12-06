import logging
try:
    from urllib.parse import unquote, urlsplit, urlunsplit, urljoin
except ImportError:
    from urllib import unquote, urlsplit, urlunsplit, urljoin

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.project.docpie.doc')
logging.getLogger('docpie').setLevel(logging.CRITICAL)


class DocHandler(BaseHandler):

    def get(self, slug=None):
        if slug is None:
            home_slug = 'quick-start'
            splited = urlsplit(self.request.uri)
            replaced = list(splited)
            replaced[2] = urljoin(splited.path, home_slug)
            return self.redirect(urlunsplit(replaced))
        else:
            unquote_slug = unquote(slug)

        info = Article(unquote_slug).get()

        if self.locale.code[:2] == 'zh':
            article = info['zh']
        else:
            article = info['en']

        return self.render(
            'project/docpie/doc.html',
            title=article['title'],
            content=md2html(article['content']),
            slug=unquote_slug
        )
