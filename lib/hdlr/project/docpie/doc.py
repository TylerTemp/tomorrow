import logging
try:
    from urllib.parse import unquote, urlsplit, urlunsplit, urljoin
except ImportError:
    from urlparse import urlsplit, urlunsplit, urljoin
    from urllib import unquote

from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
from lib.db.base import Meta

logging.getLogger('docpie').setLevel(logging.CRITICAL)

class DocHandler(BaseHandler):
    logger = logging.getLogger('_docpie.doc')

    def get(self, slug=None):
        if slug is None:
            home_slug = 'quick-start'
            splited = urlsplit(self.request.uri)
            replaced = list(splited)
            replaced[2] = urljoin(splited.path, home_slug)
            return self.redirect(urlunsplit(replaced))
        else:
            unquote_slug = unquote(slug)

        info = Meta(unquote_slug, 'docpie')

        if self.locale.code[:2] == 'zh':
            article = info.zh
        else:
            article = info.en

        return self.render(
            'project/docpie/doc.html',
            title=article['title'],
            content=md2html(article['content']),
            slug=unquote_slug
        )
