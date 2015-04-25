'''
Usage:
main.py [options]

Options:
-p --port=<port>          listen to this port[default: 8000]
--tmr-level=<level>       site logic code logging level, can be `DEBUG`, `INOF`, `WARNING`, `ERROR`, `CRITICAL`, or number from 0 to 50[default: INFO]
--tnd-level=<level>       request/response logging level.[default: INFO]
--tmr-file=<file>         site logic code file logger.[default: /tmp/tomorrow.log]
--tnd-file=<file>         request/response file logger.[default: /tmp/tornado.log]
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
from lib.hdlr.jollatask import TaskHandler
from lib.hdlr.upload import UploadHandler
from lib.hdlr.load import LoadHandler
from lib.hdlr.blacklist import BlackListHandler
from lib.hdlr.base import BaseHandler

from lib.ui.editor import MdWysiwygEditorModule
from lib.ui.editor import MdEditorModule
from lib.ui.upload import UploadImageModule
from lib.ui.upload import UploadFileModule

tornadologger = logging.getLogger('tornado')
for _hdlr in tornadologger.handlers:
    tornadologger.removeHandler(_hdlr)
    for _filter in tornadologger.filters:
        tornadologger.removeFilter(_filter)

# tornado.options.options.logging = None

logger = logging.getLogger('tomorrow')

rootdir = os.path.dirname(__file__)


class Application(tornado.web.Application):
    config = Config()

    def __init__(self):
        handlers = (
            (r'/edit/', EditHandler),
            (r'/login/', LoginHandler),
            (r'/signin/', SigninHandler),
            (r'/logout/', LogoutHandler),
            (r'/hi/(?P<user>[^/]+)/', BareHandler),
            (r'/hi/(?P<user>[^/]+)/(?P<to>file|img)/', UploadHandler),
            (r'/jolla/', BareHandler),
            (r'/jolla/blog/', BareHandler),
            (r'/jolla/blog/(?P<title>[^/]+)/', BareHandler),
            (r'/jolla/translate/', BareHandler),
            (r'/jolla/translate/(?P<title>[^/]+)/', BareHandler),
            (r'/jolla/task/', TaskHandler),
            (r'/jolla/task/(?P<title>[^/]+)/', TaskHandler),

            (r'/blog/(?P<board>[^/]+)/', BareHandler),
            (r'/edit/', BareHandler),
            (r'/edit/(?P<board>[^/]+)/', BareHandler),

            (r'/api/load/', LoadHandler),


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


class BareHandler(BaseHandler):

    def get(self, *a, **k):
        self.write('''Sorry, this page is building...<br>
            a: %s<br>
            k: %s''' % (a, k))


def get_level(level):
    level = level.strip()
    if level.isdigit():
        level = int(level)
    else:
        level = dict(debug=logging.DEBUG,
                     info=logging.INFO,
                     warning=logging.WARNING,
                     critical=logging.CRITICAL)[level.lower()]


def main(port):
    Config.set_port(port)
    tornado.locale.load_translations(
        os.path.join(rootdir, "translations"))
    tornado.locale.set_default_locale('zh_CN')
    tornado.autoreload.watch(
        os.path.join(rootdir, 'translations', 'zh_CN.csv'))
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(port)
    logger.info('[port: %s]Sever started.', port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    from docopt import docopt

    args = docopt(__doc__, help=True)


    stdoutlogger(logging.getLogger(), logging.DEBUG, True)

    filelogger(args['--tmr-file'], logger)
    filelogger(args['--tnd-file'], logger)


    main(int(args['--port']))
