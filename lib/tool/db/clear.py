import sys
import os
import time

root = os.path.normpath(os.path.join(__file__, '..', '..', '..', '..'))

sys.path.insert(0, root)
from lib.db.tomorrow import Auth
from lib.config.jolla import Config
from lib.config.base import Config as BaseConfig
from lib.tool.bashlog import stdoutlogger, DEBUG
sys.path.pop(0)

logger = stdoutlogger(None, DEBUG)
BaseConfig.auto_clean = False
config = Config()
key = config.tomorrow['key']
a = Auth(key)

for attr in ('codes', 'tokens'):
    lis = getattr(a, attr)
    to_pop = []
    for index, each in enumerate(lis):
        if each['expire_at'] < time.time():
            logger.debug('pop %s / %s', index, each['expire_at'])
            to_pop.append(index)

    for index in to_pop[::-1]:
        lis.pop(index)

a.save()
