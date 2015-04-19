import tornado.web
import sys
import os
import atexit
import logging

logger = logging.getLogger('blacklist')

blacklist = open('/tmp/blacklist', 'r+', encoding='utf-8')

# in multi process, it does not works so fine in fact
collect = set()
for line in blacklist:
    line = line.strip()
    if line:
        collect.add(line)


class BlackListHandler(tornado.web.RequestHandler):
    def get(self):
        global collect
        ip = self.request.remote_ip
        host = self.request.host
        if ip not in collect:
            collect.add(ip)
            blacklist.write('%s\n'%ip)
            blacklist.flush()
            logger.info('%s - %s' % (ip, host))
        return self.redirect(ip, True)

    post = get

@atexit.register
def close():
    blacklist.close()
