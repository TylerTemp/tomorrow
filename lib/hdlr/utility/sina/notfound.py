import tornado.web
from .base import BaseHandler


class NotFoundHandler(BaseHandler):

    def get(self):
        raise tornado.web.HTTPError(404, '"%s" Not Found' % self.request.uri)

    post = get