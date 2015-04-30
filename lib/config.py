import tempfile
import os
import sys
import atexit
import base64
import uuid
import json
import logging
import time


rootdir = os.path.normpath(os.path.join(__file__, '..', '..'))
sys.path.insert(0, rootdir)
from lib.tool.minsix import open
from lib.tool.minsix import py3
from lib.tool.minsix import FileExistsError
from lib.tool.filelock import FileLock
from lib.tool.bashlog import parse_level
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.config')
autodelete = True


class Config(object):
    _ins = None

    def __new__(cls):
        if cls._ins is None:
            # store info in class, not instance. Maybe not a good idea
            ins = super(Config, cls).__new__(cls)

            cfgpath = os.path.join(rootdir, 'config.conf')
            if os.path.exists(cfgpath):
                with open(cfgpath, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
            else:
                cfg = {}

            cls.debug = cfg.get('debug', False)
            # get/set secret
            cls.set_secret = cfg.get('set_secret', True)
            cls.info_path = cls.format_folder(
                cfg.get('info_path',
                        os.path.join('{TMPDIR}', 'tomorrow.info')))

            if cls.set_secret:
                secret = cfg.get('secret', None)
                if secret is None:
                    with FileLock(cls.info_path), \
                            open(cls.info_path, 'r+', encoding='utf-8') as f:
                        # if not exists, it will create by the locker
                        # so, x or w is not nessary
                        val = f.read()
                        if not val:    # empty
                            secret = cls.generate()
                            json.dump({'secret': secret}, f, indent=4)
                            f.flush()
                        else:
                            secret = json.loads(val)['secret']

            cls.secret = secret

            # logging level
            cls.tmr_level = parse_level(cfg.get("tomorrow_log_level", "DEBUG"))
            cls.tnd_level = parse_level(cfg.get("tornado_log_level", "DEBUG"))
            # logging file
            tmr_f = cfg.get("tomorrow_log_file", None)
            if tmr_f is None:
                cls.tmr_file = None
            else:
                cls.tmr_file = cls.format_folder(tmr_f)

            tnd_f = cfg.get("tornado_log_file", None)
            if tnd_f is None:
                cls.tnd_file = None
            else:
                cls.tnd_file = cls.format_folder(tnd_f)

            # get/set email
            cls.mail = cfg.get(
                "mail",
                {
                    "zh_CN": {
                        "url": "mail.example.cn",
                        "host": "smtp.example.cn",
                        "user": "example@example.cn",
                        "password": "example"
                    },
                    "default": {
                        "url": "mail.example.com",
                        "host": "smtp.example.com",
                        "user": "example@example.com",
                        "password": "example"
                    }
                }
            )

            # get Chinese email list
            cls.zh_mail_list = cfg.get("zh_mail", [])

            cls.img_allow = ('jpg', 'jpeg', 'png', 'gif')
            cls.size_limit = {User.block: 0, User.normal: 0,
                              User.admin: 5 * 1024 * 1024,
                              User.root: float('inf')}
            cls._ins = ins

        return cls._ins

    @classmethod
    def set_port(cls, port):
        pid = os.getpid()

        with FileLock(cls.info_path),\
                open(cls.info_path, 'r+', encoding='utf-8') as f:

            val = f.read()
            if not val:
                obj = {}
            else:
                obj = json.loads(val)
            piddict = obj.setdefault('pid2port', {})
            piddict[pid] = port

            f.seek(0)
            f.truncate()
            json.dump(obj, f, indent=4)

        logger.debug('pid: %s; port: %s at %s', pid, port, cls.info_path)

    @staticmethod
    def generate():
        s = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        if py3:
            s = s.decode('utf-8')

        return s

    @staticmethod
    def format_folder(name):
        return name.format(TMPDIR=tempfile.gettempdir())


@atexit.register
def remove():
    global autodelete
    if autodelete:
        try:
            os.remove(Config().info_path)
        except:
            pass

if __name__ == '__main__':
    with open(os.path.join(rootdir, 'config.conf'),
              'w', encoding='utf-8') as f:
        f.write(
'''{
    # logic logging file
    "tomorrow_log_file": "{TMPDIR}/tomorrow.log",

    # store cookie secret and pid/port file
    "info_path": "{TMPDIR}/tomorrow.info",

    "debug": false,

    # tornado logging level
    "tornado_log_level": "DEBUG",

    # the mail you use to send a mail
    "mail": {

        # send for Chinese mail
        # for some mails like gmail send to Chinese mail may have a long delay
        "zh_CN":  {
            "url": "mail.example.cn",
            "host": "smtp.example.cn",
            "user": "example@example.cn",
            "password": "example"
        },

        # the default mail you use to send a mail
        "default": {
            "url": "mail.example.com",
            "host": "smtp.example.com",
            "user": "example@example.com",
            "password": "example"
        }
    },

    # tornado logging file
    "tornado_log_file": "{TMPDIR}/tornado.log",

    # whether to set a cookie secret or not
    "set_secret": true,

    # logic logging level
    "tomorrow_log_level": "DEBUG",

    # mail end with this is regarded as Chinese email
    "zh_mail": [
        "163.com",
        "189.cn",
        "yeah.net",
        "126.net",
        "qq.com",
        "sina.com",
        "sogou.com"
    ]
}'''
                )
