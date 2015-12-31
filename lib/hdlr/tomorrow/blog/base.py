import sys
import os
import logging

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler, EnsureUser, EnsureSsl
from lib.tool.tracemore import get_exc_plus
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blog')

class BaseHandler(BaseHandler):

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)

        return self.render(
            'tomorrow/blog/error.html',
            code=status_code,
            msg=msg
        )