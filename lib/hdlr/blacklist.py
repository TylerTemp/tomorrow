import tornado.web
import sys
import os

import logging

logger = logging.getLogger('blacklist')

blacklist = open('/tmp/blacklist', 'a')

class BlackListHandler(tornado.web.RequestHandler):

    def get(self):
        ip = self.request.remote_ip
        host = self.request.host
        logger.debug('%s - %s' % (ip, host))
        blacklist.write(ip)
        blacklist.write('\n')
        blacklist.flush()
        return self.redirect(ip, True)

    post = get
