import tempfile
import os
import sys
import atexit
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
from lib.tool.generate import generate
from lib.db import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.config')
auto_clean = True

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
            # posts number for '/'
            ins.home_post_limit = cfg.get('home_post_limit', 10)
            ins.home_description_limit = cfg.get('home_description_limit', 100)
            # wait time (for reload.py)
            ins.sleep = cfg.get('wait_bootup', 3)
            # ports (for reload.py)
            ins.ports = set(cfg.get('ports', (8001, 8002, 8003, 8004)))
            ins.port = cfg.get('port', 8000)
            # debug
            ins.debug = cfg.get('debug', False)
            # get/set secret
            ins.set_secret = cfg.get('set_secret', True)
            ins.pids_file = cls.format_folder(
                cfg.get('pids_file',
                        os.path.join('{TMPDIR}', 'tomorrow.pids')))
            ins.sec_file = cls.format_folder(
                cfg.get('secret_file',
                        os.path.join('{TMPDIR}', 'tomorrow.sec')))

            if ins.set_secret:
                secret = cfg.get('secret', None)
                if secret is None:
                    with FileLock(ins.sec_file), \
                            open(ins.sec_file, 'r+', encoding='utf-8') as f:
                        # if not exists, it will create by the locker
                        # so, x or w is not nessary
                        val = f.read()
                        if not val:    # empty
                            secret = generate()
                            f.write(secret)
                            f.flush()
                        else:
                            secret = val

            ins.secret = secret

            # logging level
            ins.tmr_level = parse_level(cfg.get("tomorrow_log_level", "DEBUG"))
            ins.tnd_level = parse_level(cfg.get("tornado_log_level", "DEBUG"))
            # logging file
            tmr_f = cfg.get("tomorrow_log_file", None)
            if tmr_f is None:
                ins.tmr_file = None
            else:
                ins.tmr_file = cls.format_folder(tmr_f)

            tnd_f = cfg.get("tornado_log_file", None)
            if tnd_f is None:
                ins.tnd_file = None
            else:
                ins.tnd_file = cls.format_folder(tnd_f)

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
            ins.zh_mail_list = cfg.get("zh_mail", [])

            ins.img_allow = ('jpg', 'jpeg', 'png', 'gif')
            ins.size_limit = {User.normal: 0,
                              User.admin: 5 * 1024 * 1024,
                              User.root: float('inf')}
            cls._ins = ins

        return cls._ins

    # @classmethod
    def set_port(self, port):
        pid = os.getpid()

        with FileLock(self.pids_file),\
                open(self.pids_file, 'r+', encoding='utf-8') as f:

            val = f.read()
            if not val:
                piddict = {}
            else:
                piddict = json.loads(val)
            piddict[pid] = port

            f.seek(0)
            f.truncate()
            json.dump(piddict, f, indent=4)

        logger.debug('pid: %s; port: %s at %s', pid, port, self.pids_file)

    @staticmethod
    def format_folder(name):
        return name.format(TMPDIR=tempfile.gettempdir())


@atexit.register
def remove():
    if auto_clean:
        cfg = Config()
        with FileLock(cfg.pids_file),\
                open(cfg.pids_file, 'r+', encoding='utf-8') as f:
            val = f.read()
            if val:
                piddict = json.loads(val)
            else:
                return os.unlink(cfg.pids_file)

            piddict.pop(str(os.getpid()))
            f.seek(0)
            f.truncate()
            json.dump(piddict, f, indent=4)

if __name__ == '__main__':
    with open(os.path.join(rootdir, 'config.conf'),
              'w', encoding='utf-8') as f:
        f.write(
'''{
    # logic logging file
    "tomorrow_log_file": "{TMPDIR}/tomorrow.log",

    # store pid/port file
    "pids_file": "{TMPDIR}/tomorrow.pids",

    # store secret file. Delete this file if you want to refresh secret
    "secret_file": "{TMPDIR}/tomorrow.sec",

    # the posts number of '/'
    # used by `lib/hdlr/home.py/HomeHandler`
    "home_post_limit": 10,

    # the chars number of description in '/'
    # used by `lib/hdlr/home.py/HomeHandler`
    "home_description_limit": 50,

    # used by `reboot.py`
    # time period after start up a process and before kill next process
    "wait_bootup": 3,

    # used by `reboot.py`
    # which ports you want to run
    "ports": [8001, 8002, 8003, 8004],

    # used by `main.py`
    # which port you want to run. No effect if you run by `reboot.py`
    "port": 8001.

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
