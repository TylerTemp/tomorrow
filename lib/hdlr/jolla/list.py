import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Jolla
sys.path.pop(0)

logger = logging.getLogger('jolla.list')

# todo: pagination
class ListHandler(BaseHandler):

    def get(self):

        return self.render(
            'jolla/list.html',
            articles=self.parse_jolla(Jolla.all()),
            nav_active='jolla_tr'
        )

    def parse_jolla(self, collected):
        for each in collected:
            each['cover'] = each.get('cover', None) or each['headimg']
            each['preview'] = (each.get('description', None) or
                               each['content'][:200] + '...')
            yield each
