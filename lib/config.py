import tempfile
import os
import sys
import atexit
import base64
import uuid
import json
import logging
import time

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..')))
from lib.tool.minsix import open
from lib.tool.minsix import py3
from lib.tool.minsix import FileExistsError
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.config')
tempf = os.path.join(tempfile.gettempdir(), 'tomorrow.pid')
autodelete = True


class Config(object):
    _ins = None

    def __new__(cls):
        if cls._ins is None:
            ins = super(Config, cls).__new__(cls)
            ins.debug = False
            cls._ins = ins
            cls._secret = None
            cls.secret_cookie = True
            cls.img_allow = ('jpg', 'jpeg', 'png', 'gif')
            cls.size_limit = {User.block: 0, User.normal: 0,
                              User.admin: 5 * 1024 * 1024,
                              User.root: float('inf')}

        return cls._ins

    @classmethod
    def set_port(cls, port):
        pid = os.getpid()
        try:
            f = open(tempf, 'x+', encoding='utf-8')    # new
        except FileExistsError:
            f = open(tempf, 'r+', encoding='utf-8')
            while True:
                try:
                    obj = json.load(f)
                except ValueError as e:    # other process is writing
                    logger.debug('wait: %s', e)
                    time.sleep(0.5)
                    f.seek(0)
                else:
                    break
            piddict = obj.setdefault('pid2port', {})
            piddict[pid] = port
        else:
            obj = {'pid2port': {pid: port}}

        if cls.secret_cookie:
            if 'secret' not in obj:
                secret = cls.generate()
                obj['secret'] = secret

            cls._secret = obj['secret']

        f.seek(0)
        f.truncate()
        json.dump(obj, f, indent=4)
        f.close()
        logger.debug('pid: %s; port: %s', pid, port)

    # call `set_port` before use this method
    @property
    def secret(self):
        return self._secret

    @staticmethod
    def generate():
        s = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        if py3:
            s = s.decode('utf-8')

        return s


@atexit.register
def del_file():
    logger.debug('removing pid file...')
    if autodelete:
        try:
            os.unlink(tempf)
        except BaseException as e:
            logger.debug('failed: %s', e)
        else:
            logger.debug('removed')


if __name__ == '__main__':
    print(Config().generate())
