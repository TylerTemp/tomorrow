import logging
from lib.hdlr.base import BaseHandler
from lib.config import Config
try:
    from urllib.parse import urlencode, urlsplit, parse_qs, urlunsplit
except:
    from urlparse import urlencode, urlsplit, parse_qs, urlunsplit

logger = logging.getLogger('tomorrow.oauth')


class BaseHandler(BaseHandler):
    config = Config()

    def parse_callback(self, callback, code):
        url_components = urlsplit(callback)
        query = url_components.query
        args = parse_qs(query)
        args['code'] = code
        url_elements = list(url_components)
        url_elements[3] = urlencode(args)
        new_callback = urlunsplit(url_elements)
        logger.debug('call %s', new_callback)
        return new_callback