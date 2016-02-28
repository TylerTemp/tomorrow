import tempfile
import os
import atexit
import json
import logging

from lib.tool.minsix import open
from lib.tool.filelock import FileLock
from lib import Log

rootdir = os.path.abspath(
        os.path.normpath(os.path.join(__file__, '..', '..', '..')))

try:
    Str = basestring
except NameError:
    Str = str

class Base(Log):
    _ins = None
    _parent = None

    def __new__(cls, *args, **kwargs):
        if cls._ins is None:
            ins = super(Base, cls).__new__(cls, *args, **kwargs)
            config_file = ins._get_file()
            config = ins._get_default()
            if not os.path.exists(config_file):
                logging.warning(
                    'config file %r not found, use default', config_file)
            else:
                logging.info('load config from %s', config_file)
                with open(config_file, 'r', encoding='utf-8') as f:
                    config.update(json.load(f))

            tmp_dir = tempfile.gettempdir()
            for key, value in config.items():
                if isinstance(value, Str) and value.startswith('{TMPDIR}'):
                    value = value.format(TMPDIR=tmp_dir)
                setattr(ins, key, value)

            cls._ins = ins

        return cls._ins

    def __getattr__(self, item):
        if self._parent is None:
            raise AttributeError("%r object has no attribute %r" %
                                 (self.__class__.__name__, item))

        return getattr(self._parent, item)

    def _get_file(self):
        raise NotImplementedError('override this and return config file')

    def _get_default(self):
        raise NotImplementedError('override this and return default config')

    @property
    def root(self):  # read only
        return rootdir


class Config(Base):
    _ins = None
    auto_clean = True

    def __init__(self):
        super(Config, self).__init__()

        if self.mail == self._get_default()['mail']:
            self.warning('You must set up email to make email part work')

        if self.jolla_host.startswith(self.tomorrow_host):
            self.warning("Same domain. Oauth2 can't work as expected")

    def _get_file(self):
        return os.path.join(self.root, 'config', 'base.conf')

    def _get_default(self):
        return {
            'DEBUG': True,

            'wait_bootup': 0,

            'set_secret': True,
            'pids_file': '{TMPDIR}/root.pids',
            'secret_file': '{TMPDIR}/root.secret',

            'tomorrow_host': '127.0.0.1',
            'jolla_host': '127.0.0.1/jolla/',
            'host': '127.0.0.1',

            'log_level': logging.DEBUG,
            'log_file': '{TMPDIR}/root.log',
            'tornado_log_level': logging.DEBUG,
            'tornado_log_file': '{TMPDIR}/tornado.log',

            'ports': [8001, 8002, 8003, 8004],
            'port': 8001,

            'zh_mail_list': ['126.com', '163.com', 'sina.com', '21cn.com',
                             'sohu.com', 'yahoo.com.cn', 'tom.com', 'qq.com',
                             'etang.com', 'eyou.com', '56.com', 'x.cn',
                             'chinaren.com', 'sogou.com', 'citiz.com'],

            'mail':  {
                'zh': {
                  'user': '<your-email-username>',
                  'password': '<your-password>',
                  'url': '<your-email-provider-link>',
                  'host': '<your-email-host>',
                },
                'default': {
                  'user': '<your-email-username>',
                  'password': '<your-password>',
                  'url': '<your-email-provider-link>',
                  'host': '<your-email-host>',
                }
            }
        }


@atexit.register
def remove():
    cfg = Config()
    if cfg.auto_clean and os.path.exists(cfg.pids_file):

        logger = cfg.logger

        if not logger.handlers:
            import logging
            import tempfile

            logger = logging.getLogger()

            fname = os.path.join(tempfile.gettempdir(), 'SITEERROR.log')
            try:
                from lib.tool.bashlog import stdoutlogger, filelogger, DEBUG
            except ImportError:
                logging.basicConfig(level=logging.DEBUG, filename=fname)
            else:
                stdoutlogger(logger)
                filelogger(fname, logger, DEBUG)

        logger.setLevel(0)

        delete = False  # windows can not remove file when it's locked
        with FileLock(cfg.pids_file),\
                open(cfg.pids_file, 'r+', encoding='utf-8') as f:
            val = f.read()
            if val.strip():
                pid_2_port = json.loads(val)
            else:
                pid_2_port = {}
                delete = True
            logger.info('current running: %s', pid_2_port)

            if not delete:
                this_pid = str(os.getpid())
                logger.info('current pid: %s', this_pid)
                pid_2_port.pop(this_pid)
                logger.info('%s exit', this_pid)

            if not pid_2_port:
                delete = True

            if not delete:
                f.seek(0)
                f.truncate()
                json.dump(pid_2_port, f, indent=2)

        if delete:
            logger.info('delete pid file %s', cfg.pids_file)
            return os.unlink(cfg.pids_file)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    config = Config()
    config.auto_clean = False
    logging.debug(config.__dict__)
