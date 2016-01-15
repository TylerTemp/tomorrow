import tornado.web
import logging
try:
    from urllib.parse import quote, unquote
except ImportError:
    from urllib import quote
    from urlparse import unquote

from .base import BaseHandler
from lib.tool.md import html2md
from lib.tool.md import escape
from lib.db.jolla import Article, User, Source

logger = logging.getLogger('tomorrow.jolla.translate')


class EditHandler(BaseHandler):
    pass