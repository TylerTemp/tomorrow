"""
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
"""

import logging
import os
import sys
import tornado
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.locale
import tornado.autoreload
import tornado.ioloop

rootdir = os.path.dirname(__file__)
sys.path.insert(0, rootdir)

from lib.tool.bashlog import stdoutlogger, parse_level
from lib.config import Config

from lib.hdlr import BlackListHandler, AddSlashOr404Handler, RedirectHandler
from lib.hdlr import brey, jolla, tomorrow, api, utility
from lib.hdlr.project import docpie, wordz

from lib.ui.editor import WysBarModule, MdBarModule
sys.path.pop(0)


tornadologger = logging.getLogger('tornado')
for _hdlr in tornadologger.handlers:
    tornadologger.removeHandler(_hdlr)
for _filter in tornadologger.filters:
    tornadologger.removeFilter(_filter)

# tornado.options.options.logging = None

logger = logging.getLogger('tomorrow')

Config().auto_clean = True


class Application(tornado.web.Application):
    config = Config()

    def __init__(self):
        handlers = (
            # display
            (r'/', tomorrow.blog.HomeHandler),
            (r'/page/1/?', RedirectHandler, {'to': '/', 'permanently': True}),
            (r'/page/(?P<page>\d+)/', tomorrow.blog.HomeHandler),
            # auth
            (r'/login/', tomorrow.blog.LoginHandler),
            (r'/signin/', tomorrow.blog.SigninHandler),
            (r'/logout/', tomorrow.blog.LogoutHandler),
            (r'/verify/(?P<code>[^/]+)/', tomorrow.blog.VerifyHandler),
            # dashboard
            (r'/am/(?P<user>[^/]+)/', tomorrow.dash.DashboardHandler),
            (r'/am/(?P<user>[^/]+)/info/', tomorrow.dash.InfoHandler),
            (r'/am/(?P<user>[^/]+)/secure/', tomorrow.dash.SecureHandler),
            (r'/am/(?P<user>[^/]+)/(?P<to>file|img)/',
             tomorrow.dash.FileHandler),
            (r'/am/(?P<user>[^/]+)/article/', tomorrow.dash.ArticleHandler),
            (r'/am/(?P<user>[^/]+)/message/', tomorrow.dash.MessageHandler),
            (r'/am/(?P<user>[^/]+)/manage/jolla/post/',
             tomorrow.dash.manage.jolla.PostHandler),
            (r'/am/(?P<user>[^/]+)/manage/jolla/author/',
             tomorrow.dash.manage.jolla.AuthorHandler),
            (r'/am/(?P<user>[^/]+)/manage/user/',
             tomorrow.dash.manage.UserHandler),
            (r'/am/(?P<user>[^/]+)/manage/message/',
             tomorrow.dash.manage.MessageHandler),
            # profile
            (r'/hi/(?P<user>[^/]+)/', tomorrow.hi.DashboardHandler),
            (r'/hi/(?P<user>[^/]+)/article/', tomorrow.hi.ArticleHandler),
            (r'/hi/(?P<user>[^/]+)/message/', tomorrow.hi.MessageHandler),
            # jolla

            (r'/jolla/(favicon\.ico)', tornado.web.StaticFileHandler,
             {'path': os.path.join(rootdir, 'static')}),
            (r'/jolla/', jolla.HomeHandler),
            (r'/jolla/page/1/',
             RedirectHandler,
             {'to': '//' + self.config.jolla_host, 'permanently': True}),
            (r'/jolla/page/(\d+)/', jolla.HomeHandler),
            (r'/jolla/feed/', jolla.RssHandler),
            (r'/jolla/tr/', jolla.ListHandler),
            (r'/jolla/tr/(?P<slug>[^/]+)/', jolla.TranslateHandler),
            (r'/jolla/task/', jolla.TaskHandler),
            (r'/jolla/task/(?P<urlslug>[^/]+)/', jolla.TaskHandler),
            (r'/jolla/(?P<slug>[^/]+)/', jolla.ArticleHandler),
            # project
            (r'/project/docpie/', docpie.HomeHandler),
            (r'/project/docpie/document/', docpie.DocHandler),
            (r'/project/docpie/document/(?P<slug>[^/]+)/', docpie.DocHandler),
            (r'/project/docpie/try/', docpie.TryHandler),

            (r'/project/wordz/', wordz.HomeHandler),
            (r'/project/wordz/quiz/', wordz.QuizHandler),
            (r'/project/wordz/modify/', wordz.ModifyHandler),

            (r'/blog/(?P<slug>[^/]+)/', tomorrow.blog.ArticleHandler),
            (r'/edit/', tomorrow.blog.EditHandler),
            (r'/edit/(?P<urlslug>[^/]+)/', tomorrow.blog.EditHandler),

            (r'/api/load/', jolla.LoadHandler),
            (r'/api/(?P<source>html|md)/(?P<target>html|md)/',
             api.MdAndHtmlHandler),
            (r'/utility/sina/', utility.sina.HomeHandler),
            (r'/utility/sina/callback/', utility.sina.CallbackHandler),
            (r'/utility/sina/exec/', utility.sina.ExecHandler),
            (r'/utility/sina/[^/]+/', utility.sina.NotFoundHandler),

            (r'/brey/', brey.BreyHandler),
            (r'/brey/(?P<slug>[^/]+)/', brey.BreyHandler),

            (r'/utility/pts/', utility.TakeOutCalculateHandler),

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


def main(port):
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
    from docpie import docpie as pie

    args = dict(pie(__doc__))

    config = Config()

    rootlogger = logging.getLogger()
    stdoutlogger(rootlogger, logging.DEBUG, True)

    tmr_level = parse_level(args['--tmr-level'] or config.tmr_level)
    tnd_level = parse_level(args['--tnd-level'] or config.tnd_level)
    tmr_file = args['--tmr-file'] or config.tmr_file
    tnd_file = args['--tnd-file'] or config.tnd_file

    if tmr_file is None:
        rootlogger.warning("tomorrow file logger disabled")
    else:
        logger.setLevel(tmr_level)
        handler = logging.FileHandler(tmr_file)
        logger.addHandler(handler)
        # filelogger(tmr_file, logger, tmr_level)

    if tnd_file is None:
        rootlogger.warning("tornado file logger disabled")
    else:
        tornadologger.setLevel(tnd_level)
        handler = logging.FileHandler(tnd_file)
        tornadologger.addHandler(handler)
        # filelogger(tnd_file, tornadologger, tnd_level)

    port = args['--port']
    if port is None:
        port = config.port
    else:
        port = int(port)

    main(port)
