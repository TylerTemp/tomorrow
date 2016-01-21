import logging
import tornado.ioloop
from lib.hdlr.tomorrow.base import BaseHandler
from lib.db.tomorrow import User
try:
    from urllib.parse import urlencode, urlsplit, parse_qs, urlunsplit
except:
    from urlparse import urlencode, urlsplit, parse_qs, urlunsplit

logger = logging.getLogger('tomorrow.oauth')


class BaseHandler(BaseHandler):

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
        user = User(user)
        assert user, 'User %s not found' % user
        return user._id

    def do_at(self, callback, expire_at):
        logger.debug('call %s at %s', callback, expire_at)
        tornado.ioloop.IOLoop.instance().add_timeout(
            expire_at,
            callback
        )
