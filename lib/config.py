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
from lib.db.tomorrow import User
sys.path.pop(0)

logger = logging.getLogger('tomorrow.config')


class Config(object):
    _ins = None
    auto_clean = False

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
            ins.jolla_post_limit = cfg.get('jolla_post_limit', 9)
            ins.main_host = cfg.get('main_host', '127.0.0.1')
            ins.jolla_host = cfg.get('jolla_host', '127.0.0.1/jolla/blog')
            # App config
            ins.jolla_app = cfg.get('jolla', {'key': None, 'secret': None})
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
            else:
                ins.secret = None

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
            ins.size_limit = {User.NORMAL: 0,
                              User.ADMIN: 5 * 1024 * 1024,
                              User.ROOT: float('inf')}
            cls._ins = ins

        return cls._ins

    @staticmethod
    def format_folder(name):
        return name.format(TMPDIR=tempfile.gettempdir())


@atexit.register
def remove():
    cfg = Config()
    if cfg.auto_clean:
        delete = False  # windows can not remove file when it's locked
        with FileLock(cfg.pids_file),\
                open(cfg.pids_file, 'r+', encoding='utf-8') as f:
            val = f.read()
            if val.strip():
                pid_2_port = json.loads(val)
            else:
                pid_2_port = {}
                delete = True
            if not delete:
                this_pid = os.getpid()
                pid_2_port.pop(this_pid)
                logger.debug('%s exit', this_pid)
            if not pid_2_port:
                delete = True
            if not delete:
                f.seek(0)
                f.truncate()
                json.dump(pid_2_port, f, indent=2)

        if delete:
            logger.debug('delete pid file %s', cfg.pids_file)
            return os.unlink(cfg.pids_file)

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

    # the posts number of '/blog/jolla/[page/NUM/]'
    # used by `lib/hdlr/jolla/blog/BolgHandler.py`
    "jolla_post_limit": 9,

    # the chars number of description in '/'
    # used by `lib/hdlr/home.py/HomeHandler`
    "home_description_limit": 50,

    # domain
    "main_host": "127.0.0.1",

    # jolla blog domain (rewrite to main_host/jolla/blog/.*)
    "jolla_host": "127.0.0.1",

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
