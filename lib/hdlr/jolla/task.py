import tornado.web
import logging
import json
import time
try:
    from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit
except ImportError:
    from urllib import quote
    from urlparse import unquote, urljoin, urlsplit, urlunsplit

from .base import BaseHandler
from lib.config import Config
from lib.tool.md import html2md
from lib.tool.md import escape
from lib.db.jolla import Source, User

cfg = Config()
logger = logging.getLogger('tomorrow.jolla.task')


class TaskHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.xsrf_token

        link = self.get_argument('source', None)
        if link is not None:
            source = Source(link)
            if not source:
                raise tornado.web.HTTPError(
                    404, "source %r not found" % link)
        else:
            source = Source()

        return super(TaskHandler, self).render(
            'jolla/task.html',
            source=source
        )

    @tornado.web.authenticated
    def post(self, urlslug=None):
        self.check_xsrf_cookie()
        url_link = self.get_argument('source', None)

        link = self.formal_link(self.get_argument('link'))
        title = self.get_argument('title', '').strip() or None
        author = self.get_argument('author', '').strip() or None
        banner = self.get_argument('banner', '').strip() or None
        cover = self.get_argument('cover', '').strip() or None
        slug = self.get_argument('slug', '').strip() or None
        tags = []
        for tag in self.get_argument('tag', '').split(','):
            this_tag = tag.strip()
            if this_tag and this_tag not in tags:
                tags.append(this_tag)

        if url_link is not None:
            source = Source(url_link)
            if not source:
                raise tornado.web.HTTPError(
                    404, 'source %r not found' % url_link)
        else:
            source = Source(link)
            if source:
                raise tornado.web.HTTPError(
                    409, 'source %r exists' % link)

        source.title = title
        source.author = author
        source.banner = banner
        source.cover = cover
        source.slug = slug
        source.tag = tags
        source.save()
        return self.write(json.dumps(
                {'error': 0, 'redirect': '/tr/?source=%s' % quote(source.link, '')}))

    def formal_link(self, link):
        splited = list(urlsplit(link))
        if not splited[0] or not splited[1]:
            raise tornado.web.HTTPError(
                400, 'scheme or netloc missed in %r' % link)

        splited[4] = ''
        return urlunsplit(splited)

