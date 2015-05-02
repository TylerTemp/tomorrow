import tornado.web
import sys
import os
import atexit
import logging

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.minsix import open
from lib.tool.minsix import FileNotFoundError
sys.path.pop(0)

logger = logging.getLogger('tomorrow.blacklist')
try:
    blacklist = open('/tmp/blacklist', 'r+', encoding='utf-8')
except FileNotFoundError:
    blacklist = open('/tmp/blacklist', 'w+', encoding='utf-8')
# in multi process, it does not works so fine in fact
collect = set()
for line in blacklist:
    line = line.strip()
    if line:
        collect.add(line)


class BlackListHandler(tornado.web.RequestHandler):
    def get(self, *a, **k):
        global collect
        ip = self.request.remote_ip
        host = self.request.host
        if ip not in collect:
            collect.add(ip)
            blacklist.write('%s\n' % ip)
            blacklist.flush()
            logger.info('%s - %s' % (ip, host))
            if len(collect) >= 1000:
                logger.warning('too many blacklist. Clean')
                collect.clear()
        return self.redirect('//'+ip, True)

    post = get


@atexit.register
def close():
    blacklist.close()
