'''
Usage:
main.py [options]

Options:
-p --port=<port>          listen to this port
--tmr-level=<level>       site logic code logging level, can be `DEBUG`,
                          `INOF`, `WARNING`, `ERROR`, `CRITICAL`,
                          or number from 0 to 50
--tnd-level=<level>       request/response logging level.
--tmr-file=<file>         site logic code file logger.
--tnd-file=<file>         request/response file logger.
-h, -?, --help            print this message
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

from lib.tool.bashlog import stdoutlogger, filelogger, parse_level
from lib.config import Config

from lib.hdlr import brey
from lib.hdlr import project
from lib.hdlr import dash, hi, jolla, auth, api
from lib.hdlr.base import BaseHandler
from lib.hdlr.home import HomeHandler
from lib.hdlr.edit import EditHandler
from lib.hdlr.post import PostHandler
from lib.hdlr.notfound import AddSlashOr404Handler
from lib.hdlr.redirect import RedirectHandler
from lib.hdlr.verify import VerifyHandler
from lib.hdlr.blacklist import BlackListHandler

from lib.ui.editor import WysBarModule, MdBarModule
from lib.ui.iconfont import IconFontModule
from lib.ui.license import LicenseModule
from lib.ui.author import AuthorModule

tornadologger = logging.getLogger('tornado')
for _hdlr in tornadologger.handlers:
    tornadologger.removeHandler(_hdlr)
for _filter in tornadologger.filters:
    tornadologger.removeFilter(_filter)

tornado.options.options.logging = None

logger = logging.getLogger('tomorrow')

rootdir = os.path.dirname(__file__)

Config().auto_clean = True


class Application(tornado.web.Application):
    config = Config()

    def __init__(self):
        handlers = (
            # display
            (r'/', HomeHandler),
            (r'/page/1/?', RedirectHandler, {'to': '/', 'permanently': True}),
            (r'/page/(?P<page>\d+)/', HomeHandler),
            # auth
            (r'/login/', auth.LoginHandler),
            (r'/signin/', auth.SigninHandler),
            (r'/logout/', auth.LogoutHandler),
            (r'/verify/(?P<code>[^/]+)/', VerifyHandler),
            # dashboard
            (r'/am/(?P<user>[^/]+)/', dash.DashboardHandler),
            (r'/am/(?P<user>[^/]+)/info/', dash.InfoHandler),
            (r'/am/(?P<user>[^/]+)/secure/', dash.SecureHandler),
            (r'/am/(?P<user>[^/]+)/(?P<to>file|img)/', dash.FileHandler),
            (r'/am/(?P<user>[^/]+)/article/', dash.ArticleHandler),
            (r'/am/(?P<user>[^/]+)/message/', dash.MessageHandler),
            (r'/am/(?P<user>[^/]+)/manage/jolla/post/',
             dash.manage.jolla.PostHandler),
            (r'/am/(?P<user>[^/]+)/manage/jolla/author/',
             dash.manage.jolla.AuthorHandler),
            (r'/am/(?P<user>[^/]+)/manage/user/', dash.manage.UserHandler),
            (r'/am/(?P<user>[^/]+)/manage/message/', dash.manage.MessageHandler),
            # profile
            (r'/hi/(?P<user>[^/]+)/', hi.DashboardHandler),
            (r'/hi/(?P<user>[^/]+)/article/', hi.ArticleHandler),
            (r'/hi/(?P<user>[^/]+)/message/', hi.MessageHandler),
            # jolla
            (r'/jolla/', RedirectHandler, {'to': '/', 'permanently': True}),
            (r'/jolla/blog/Early-access:-Sailfish-OS-Aaslakkaj%C3%A4rvi-with-private-browsing-and-more-is-here!/',
             RedirectHandler,
             {'to': 'http://%s/sailfish-os-aaslakkajarvi/' % self.config.jolla_host,
              'permanently': True}),
            (r'/test/', RedirectHandler, {'to': '/'}),

            (r'/jolla/blog/', jolla.BlogHandler),
            (r'/jolla/blog/(favicon\.ico)', tornado.web.StaticFileHandler,
             {'path': os.path.join(rootdir, 'static')}),
            (r'/jolla/blog/page/1/',
             RedirectHandler,
             {'to': '//' + self.config.jolla_host, 'permanently': True}),
            (r'/jolla/blog/page/(\d+)/', jolla.BlogHandler),
            (r'/jolla/blog/feed/', jolla.RssHandler),
            (r'/jolla/blog/(?P<url>[^/]+)/', jolla.ArticleHandler),
            (r'/jolla/translate/', jolla.ListHandler),
            (r'/jolla/translate/(?P<url>[^/]+)/', jolla.TranslateHandler),
            (r'/jolla/task/', jolla.TaskHandler),
            (r'/jolla/task/(?P<url>[^/]+)/', jolla.TaskHandler),
            # project
            (r'/project/docpie/', project.docpie.HomeHandler),
            (r'/project/docpie/try/', project.docpie.TryHandler),

            (r'/blog/(?P<slug>[^/]+)/', PostHandler),
            (r'/edit/', EditHandler),
            (r'/edit/(?P<urlslug>[^/]+)/', EditHandler),

            (r'/api/load/', jolla.LoadHandler),
            (r'/api/(?P<source>html|md)/(?P<target>html|md)/', api.MdAndHtmlHandler),
            (r'/brey/', brey.IndexHandler),
            (r'/brey/exam/', brey.ExamHandler),
            (r'/brey/booklist/', brey.BooklistHandler),
            (r'/brey/news/', brey.NewsHandler),

            (r'.*?\.php$(?i)', BlackListHandler),
            (r'.*', AddSlashOr404Handler),
        )

        settings = {
            'template_path': os.path.join(rootdir, 'template'),
            'static_path': os.path.join(rootdir, 'static'),
            'debug': self.config.debug,
            'login_url': '/login/',
            'ui_modules': {
                'WysBar': WysBarModule,
                'MdBar': MdBarModule,
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
    from docpie import docpie

    config = Config()

    args = docpie(__doc__)

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
