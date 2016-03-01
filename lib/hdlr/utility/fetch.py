import logging
import tornado.web
import tornado.gen
import tornado.httpclient
from lib.hdlr.base import BaseHandler
from lib.tool.minsix import py3


class FetchHandler(BaseHandler):
    logger = logging.getLogger('jolla.oauth')

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        url = self.get_argument('url')
        method = self.get_argument('method', 'GET').upper()

        self.info('[%s] %s', method, url)

        client = tornado.httpclient.AsyncHTTPClient()

        response = yield tornado.gen.Task(client.fetch,
                                          url,
                                          method=method)
                                          # validate_cert=False,
                                          # headers={'X-Requested-With':
                                          #              'XMLHttpRequest'})
        code = response.code
        try:
            self.set_status(code)
        except ValueError as e:
            self.debug('%s: %s', code, str(e))

        body = response.body

        if body and py3:
            body = body.decode('utf-8')
        if body:
            self.write(body)
        else:
            self.write('[EMPTY RESULT]')
        self.finish()