import logging
import tornado.web

from .base import BaseHandler
from lib.db.jolla import Source

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

logger = logging.getLogger('jolla.list')


class ListHandler(BaseHandler):
    LIMIT = 10

    def get(self, page=None):
        if page is None:
            page = 1
        else:
            page = int(page)
        skip = page * self.LIMIT
        all_raw_source = Source.all(skip, self.LIMIT)
        all_num = all_raw_source.count()

        if skip >= all_num:
            raise tornado.web.HTTPError(404, 'Page %s empty' % page)

        all_source = self.get_all_source(all_raw_source)

        if page >= 2:
            prev_page = page - 1
        else:
            prev_page = None

        if self.LIMIT * (page + 1) < all_num:
            next_page = page + 1
        else:
            next_page = None


        return self.render(
            'jolla/list.html',
            sources=all_source,
            prev_page=prev_page,
            next_page=next_page,
            quote=quote,
        )

    def get_all_source(self, sources):
        for each in sources:
            s = Source()
            s.update(each)
            yield s

