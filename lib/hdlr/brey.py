import tornado.locale
import tornado.web
try:
    from urllib.parse import unquote
except ImportError:
    from urlparse import unquote

from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
from lib.db.base import Meta

class BreyHandler(BaseHandler):

    def get(self, slug='home'):

        article = self.get_article(slug)

        return self.render(
            'brey/brey.html',
            page_title=article.title,
            title=article.title,
            content=md2html(article.content)
        )

    def get_user_locale(self):
        return tornado.locale.get('en')

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)

        return self.render(
            'brey/error.html',
            code=status_code,
            msg=msg,
        )

    def get_article(self, slug):
        m = Meta.find_one({'slug': slug, '_group': 'brey'})
        if not m:
            raise tornado.web.HTTPError(404, 'page %r not found' % slug)
        return m