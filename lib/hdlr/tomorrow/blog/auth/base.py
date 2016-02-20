import logging
import re
from ..base import BaseHandler


class BaseHandler(BaseHandler):
    logger = logging.getLogger('tomorrow.auth')
    USERNAME = re.compile(r'^[a-zA-Z0-9\u4e00-\u9fa5\_\.\ \-\+]+$')
    USERMAX = 100
