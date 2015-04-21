'''
Usage:
main.py [options]

Options:
-p --port=<port>          listen to this port[default: 8000]
-l --logging=<level>      log level, can be `DEBUG`, `INOF`, `WARNING`, `ERROR`, `CRITICAL`, or number from 0 to 50[default: INFO]
-f --log-file=<file>      log target file
-h --help                 show this message
'''


import logging
import os
import time
import tornado
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.locale
import tornado.autoreload

from lib.tool.bashlog import stdoutlogger
from lib.tool.bashlog import filelogger
from lib.config import Config

from lib.hdlr.notfound import AddSlashOr404Handler
from lib.hdlr.edit import EditHandler
from lib.hdlr.auth import LoginHandler
from lib.hdlr.auth import SigninHandler
from lib.hdlr.auth import LogoutHandler
from lib.hdlr.blacklist import BlackListHandler

from lib.ui.editor import MdWysiwygEditorModule
from lib.ui.editor import MdEditorModule
from lib.ui.upload import UploadImageModule
from lib.ui.upload import UploadFileModule

tornadologger = logging.getLogger('tornado')
for _hdlr in tornadologger.handlers:
    tornadologger.removeHandler(_hdlr)
    for _filter in tornadologger.filters:
        tornadologger.removeFilter(_filter)

tornado.options.options.logging = None

logger = logging.getLogger()

rootdir = os.path.dirname(__file__)


class Application(tornado.web.Application):
    config = Config()

    def __init__(self):
        handlers = (
            (r'/edit/', EditHandler),
            (r'/login/', LoginHandler),
            (r'/signin/', SigninHandler),
            (r'/logout/', LogoutHandler),
            (r'/xmlrpc\.php', BlackListHandler),
            (r'/wp-login\.php', BlackListHandler),
            (r'.*', AddSlashOr404Handler),
        )

        settings = {
            'template_path': os.path.join(rootdir, 'template'),
            'static_path': os.path.join(rootdir, 'static'),
            'debug': self.config.debug,
            'login_url': '/login/',
            'ui_modules': {
                'WysiwygEditor': MdWysiwygEditorModule,
                'MdEditor': MdEditorModule,
                'UploadFile': UploadFileModule,
                'UploadImage': UploadImageModule,
                },
        }

        if self.config.secret_cookie:
            # while self.config.secret is None:
            #     logger.debug('waitting for cookie secret')
            #     time.sleep(0.5)
            secret = self.config.secret
            assert secret is not None
            logger.debug('set secret')
            settings['cookie_secret'] = secret

        super(Application, self).__init__(handlers, **settings)


def main(port):
    Config.set_port(port)
    tornado.locale.load_translations(
        os.path.join(rootdir, "translations"))
    tornado.locale.set_default_locale('zh_CN')
    tornado.autoreload.watch(os.path.join(rootdir, 'translations', 'zh_CN.csv'))
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(port)
    logger.info('[port: %s]Sever started.', port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    from docopt import docopt

    args = docopt(__doc__, help=True)

    level = args['--logging']
    if level.isdigit():
        level = int(level)
    else:
        level = dict(debug=logging.DEBUG,
                     info=logging.INFO,
                     warning=logging.WARNING,
                     critical=logging.CRITICAL)[level.lower()]

    stdoutlogger(logger, level, True)

    logfile = args['--log-file']
    if logfile:
        filelogger(logfile, logger)

    main(int(args['--port']))
