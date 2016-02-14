import logging
import tornado.web

from .base import BaseHandler
from lib.db.jolla import Source
import pymongo

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


class ListHandler(BaseHandler):
    logger = logging.getLogger('jolla.list')
    LIMIT = 10

    def get(self, page=None):
        if page is None:
            self.page = 1
        else:
            self.page = int(page)
        skip = (self.page - 1) * self.LIMIT
        # TODO: better solution
        # all_num = Source.collection.find({}).count()

        all_source = self.get_all_source(skip, self.LIMIT)

        if self.page >= 2:
            prev_page = self.page - 1
        else:
            prev_page = None

        return self.render(
            'jolla/list.html',
            sources=all_source,
            prev_page=prev_page,
            get_next_page=self.get_next_page,
            quote=quote,
        )

    def get_next_page(self):
        if not hasattr(self, '_next_page'):
            self._next_page = self._get_next_page()

        return self._next_page

    def _get_next_page(self):
        current_page = self.page
        current_shown = self.LIMIT * current_page
        trans_total = self.trans_total
        untrans_total = self.untrans_total

        if current_shown < untrans_total:
            return current_page + 1

        if trans_total is None:
            return None

        full_num = trans_total + untrans_total

        if current_shown < full_num:
            return current_page + 1

        return None

    def get_all_source(self, start, length):
        self.debug('start: %s; limit: %s', start, length)

        untrans = Source.all_untranslated(start, length)
        self.untrans_total = untrans.count()
        self.trans_total = None
        is_empty = True

        for each in untrans:
            source = Source()
            source.update(each)
            is_empty = False
            yield source
            length -= 1

        if length <= 0:
            yield self.raise_if_true(is_empty)
            return

        if start > self.untrans_total:
            start -= self.untrans_total
        else:
            start = 0

        trans = Source.all_translated(start, length)
        self.trans_total = trans.count()

        for each in trans:
            source = Source()
            source.update(each)
            is_empty = False
            yield source

        yield self.raise_if_true(is_empty)

    def raise_if_true(self, true):
        if true:
            raise tornado.web.HTTPError(404, 'This page is Empty')
