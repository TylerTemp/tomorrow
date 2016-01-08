import logging
import tornado.ioloop
from lib.hdlr.base import BaseHandler
from lib.config import Config
from lib.db.tomorrow import User
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

    def get_uid(self, user):
        u = User(user)
        assert not u.new, 'User %s not found' % user
        info = u.get()
        return info['_id']

    def clear_at(self, callback, expire_at):
        logger.debug('clean up at %s' % expire_at)
        tornado.ioloop.IOLoop.instance().add_timeout(
            expire_at,
            callback
        )
