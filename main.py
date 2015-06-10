'''
Usage:
main.py [options]

Options:
-p --port=<port>          listen to this port(default: 8000)
--tmr-level=<level>       site logic code logging level, can be `DEBUG`,
                          `INOF`, `WARNING`, `ERROR`, `CRITICAL`,
                          or number from 0 to 50(default: INFO)
--tnd-level=<level>       request/response logging level.(default: INFO)
--tmr-file=<file>         site logic code file logger.
                          (default: /tmp/tomorrow.log)
--tnd-file=<file>         request/response file logger.
                          (default: /tmp/tornado.log)
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
from lib.tool.bashlog import parse_level
from lib.config import Config

from lib.hdlr.notfound import AddSlashOr404Handler
from lib.hdlr.redirect import RedirectHandler
from lib.hdlr.brey import ForBrey
from lib.hdlr import dash
from lib.hdlr import hi
from lib.hdlr import jolla
from lib.hdlr import auth
from lib.hdlr.blacklist import BlackListHandler
from lib.hdlr.base import BaseHandler

from lib.ui.editor import MdWysiwygEditorModule
from lib.ui.editor import MdEditorModule
from lib.ui.iconfont import IconFontModule
from lib.ui.license import LicenseModule
from lib.ui.author import AuthorModule

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
            ('/', RedirectHandler, {'to': '/jolla/'}),
            (r'/login/', auth.LoginHandler),
            (r'/signin/', auth.SigninHandler),
            (r'/logout/', auth.LogoutHandler),

            (r'/am/(?P<user>[^/]+)/', dash.DashboardHandler),
            (r'/am/(?P<user>[^/]+)/info/', dash.InfoHandler),
            (r'/am/(?P<user>[^/]+)/secure/', dash.SecureHandler),
            (r'/am/(?P<user>[^/]+)/(?P<to>file|img)/', dash.FileHandler),
            (r'/am/(?P<user>[^/]+)/verify/'
             r'(?P<act>newuser|newmail|changemail|changeuser|changepwd)/'
             r'(?P<code>[^/]+)/', dash.VerifyHandler),
            (r'/am/(?P<user>[^/]+)/article/', dash.ArticleHandler),
            (r'/am/(?P<user>[^/]+)/message/', dash.MessageHandler),
            (r'/am/(?P<user>[^/]+)/manage/jolla/', dash.manage.JollaHandler),

            (r'/hi/(?P<user>[^/]+)/', hi.DashboardHandler),
            (r'/hi/(?P<user>[^/]+)/article/', hi.ArticleHandler),
            (r'/hi/(?P<user>[^/]+)/message/', hi.MessageHandler),

            (r'/jolla/', jolla.HomeHandler),
            (r'/jolla/blog/', jolla.BlogHandler),
            (r'/jolla/blog/(?P<url>[^/]+)/', jolla.ArticleHandler),
            (r'/jolla/translate/', jolla.ListHandler),
            (r'/jolla/translate/(?P<url>[^/]+)/', jolla.TranslateHandler),
            (r'/jolla/task/', jolla.TaskHandler),
            (r'/jolla/task/(?P<url>[^/]+)/', jolla.TaskHandler),

            (r'/blog/(?P<board>[^/]+)/', BareHandler),
            (r'/edit/', BareHandler),
            (r'/edit/(?P<board>[^/]+)/', BareHandler),

            (r'/api/load/', jolla.LoadHandler),
            (r'/brey/', ForBrey),

            (r'.*?\.php$(?i)', BlackListHandler),
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
                'License': LicenseModule,
                'Author': AuthorModule,
                'IconFontCss': IconFontModule,
                # 'UploadFile': UploadFileModule,
                # 'UploadImage': UploadImageModule,
                },
        }

        if self.config.set_secret:
            secret = self.config.secret
            assert secret is not None
            logger.debug('set secret')
            settings['cookie_secret'] = secret

        if self.config.debug:
            logger.warning('debug is on')

        super(Application, self).__init__(handlers, **settings)


class BareHandler(BaseHandler):

    def get(self, *a, **k):
        self.write('''Sorry, this page is building...<br>
            a: %s<br>
            k: %s''' % (a, k))


def main(port):
    Config().set_port(port)
    tornado.locale.load_translations(
        os.path.join(rootdir, "translations"))
    # set this tornado will ignore the borwser `Accept-Language` head, why?
    # tornado.locale.set_default_locale('zh')
    tornado.autoreload.watch(
        os.path.join(rootdir, 'translations', 'zh.csv'))
    tornado.autoreload.watch(
        os.path.join(rootdir, 'config.conf'))
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(port)
    logger.info('[port: %s]Sever started.', port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    from docopt import docopt

    config = Config()

    args = docopt(__doc__, help=True)

    rootlogger = logging.getLogger()
    stdoutlogger(rootlogger, logging.DEBUG, True)

    tmr_level = parse_level(args['--tmr-level'] or config.tmr_level)
    tnd_level = parse_level(args['--tnd-level'] or config.tnd_level)
    tmr_file = args['--tmr-file'] or config.tmr_file
    tnd_file = args['--tnd-file'] or config.tnd_file

    if tmr_file is None:
        rootlogger.warning("tomorrow file logger disabled")
    else:
        filelogger(tmr_file, logger, tmr_level)

    if tnd_file is None:
        rootlogger.warning("tornado file logger disabled")
    else:
        filelogger(tnd_file, tornadologger, tnd_level)

    port = args['--port']
    if port is None:
        port = config.port
    else:
        port = int(port)

    main(port)
