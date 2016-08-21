"""
Usage:
main.py [options]

Options:
-p --port=<port>          listen to this port
--tmr-level=<level>       site logic code logging level, can be `DEBUG`,
                          `INOF`, `WARNING`, `ERROR`, `CRITICAL`,
                          or number from 0 to 50
--tnd-level=<level>       request/response logging level.
--jolla-level=<level>
--tmr-file=<file>         site logic code file logger.
--tnd-file=<file>         request/response file logger.
--jolla-file=<file>
-h, -?, --help            print this message
"""

import logging
import os
import tornado
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.locale
import tornado.autoreload
import tornado.ioloop

from lib.config.base import Config

from lib.hdlr import BlackListHandler, RedirectHandler,\
                     StaticFileHandler, BaseHandler
from lib.hdlr import brey, jolla, tomorrow, api, utility, mail
from lib.hdlr.project import docpie, wordz

from lib.ui import WysBarModule, MdBarModule, ErrorImageModule, \
                   TimeModule, TagModule

from lib.tool.generate import generate
from lib.tool.minsix import open
from lib.tool.filelock import FileLock

# tornado.options.options.logging = None

logger = logging.getLogger()


class Application(tornado.web.Application):
    config = Config()

    def __init__(self):
        handlers = (
            # static
            (r'/static/(.*)', tornado.web.StaticFileHandler,
             {'path': os.path.join(self.config.root, 'static')}),
            # display
            (r'/', tomorrow.blog.HomeHandler),
            (r'/page/1/?', RedirectHandler, {'to': '/', 'permanently': True}),
            (r'/page/(?P<page>\d+)/', tomorrow.blog.HomeHandler),
            (r'/blog/(?P<slug>[^/]+)/', tomorrow.blog.ArticleHandler),
            (r'/(?P<from_>blog|edit)/(?P<slug>[^/]+)/(?P<attach>.+)',
             tomorrow.blog.ArticleAttachmentHandler),
            (r'/edit/', tomorrow.blog.EditHandler),
            (r'/edit/(?P<urlslug>[^/]+)/', tomorrow.blog.EditHandler),
            # auth
            (r'/login/', tomorrow.blog.auth.LoginHandler),
            (r'/signin/', tomorrow.blog.auth.SigninHandler),
            (r'/logout/', tomorrow.blog.auth.LogoutHandler),
            (r'/forget/', tomorrow.blog.auth.ForgetHandler),
            (r'/verify/', tomorrow.blog.auth.VerifyHandler),
            # oauth2
            (r'/oauth2/authorize/', tomorrow.oauth2.AuthorizeHandler),
            (r'/oauth2/confirm/(?P<app_key>[^/]+)/',
             tomorrow.oauth2.ConfirmHandler),
            (r'/oauth2/confirm/(?P<app_key>[^/]+)/(?P<temp_code>[^/]+)/',
             tomorrow.oauth2.ConfirmHandler),
            (r'/oauth2/token/', tomorrow.oauth2.GetTokenHandler),
            (r'/(page|blog|edit|login|signin|logout|verify)/.*?',
             tomorrow.blog.BaseHandler),
            # dashboard
            (r'/dashboard/', tomorrow.dash.DashboardHandler),
            (r'/dashboard/info/', tomorrow.dash.InfoHandler),
            (r'/dashboard/secure/', tomorrow.dash.SecureHandler),
            (r'/dashboard/uploaded/(?P<path>.*?)',
             tomorrow.dash.UploadedHandler),
            (r'/dashboard/article/', tomorrow.dash.ArticleHandler),
            (r'/dashboard/users/',
             tomorrow.dash.UsersHandler),
            (r'/dashboard/.*', tomorrow.dash.BaseHandler),
            # profile
            (r'/hi/(?P<user>[^/]+)/', tomorrow.hi.DashboardHandler),
            (r'/hi/(?P<user>[^/]+)/article/', tomorrow.hi.ArticleHandler),
            (r'/hi/.*', tomorrow.hi.BaseHandler),
            (r'/robots.txt', StaticFileHandler,
             {'path': os.path.join(self.config.root,
                                   'static', 'robots', 'blog.txt')}),
            (r'/(favicon\.ico)', tornado.web.StaticFileHandler,
             {'path': os.path.join(self.config.root, 'static')}),
            # jolla

            (r'/jolla/(favicon\.ico)', tornado.web.StaticFileHandler,
             {'path': os.path.join(self.config.root, 'static')}),
            (r'/jolla/', jolla.HomeHandler),
            (r'/jolla/page/1/',
             RedirectHandler,
             {'to': '//' + self.config.jolla_host, 'permanently': True}),
            (r'/jolla/page/(\d+)/', jolla.HomeHandler),
            (r'/jolla/search/', jolla.SearchHandler),
            (r'/jolla/search/(.*?)/', jolla.SearchHandler),
            (r'/jolla/feed/', jolla.RssHandler),
            (r'/jolla/list/', jolla.ListHandler),
            (r'/jolla/list/page/1/', RedirectHandler,
             {'to': '//%s/list/' % self.config.jolla_host,
              'permanently': True}),
            (r'/jolla/list/page/(?P<page>\d+)/', jolla.ListHandler),
            (r'/jolla/tr/', jolla.TranslateHandler),
            (r'/jolla/tr/(?P<slug>[^/]+)/', jolla.TranslateHandler),
            (r'/jolla/edit/', jolla.EditHandler),
            (r'/jolla/edit/(?P<slug>[^/]+)/', jolla.EditHandler),
            (r'/jolla/task/', jolla.TaskHandler),
            (r'/jolla/login/', jolla.LoginHandler),
            (r'/jolla/logout/', jolla.LogoutHandler),
            (r'/jolla/oauth2/tomorrow/', jolla.OAuthHandler),
            (r'/jolla/posts/', jolla.PostsHandler),
            (r'/jolla/profile/', jolla.ProfileHandler),
            (r'/jolla/author/', jolla.AuthorHandler),
            (r'/jolla/manage/user/', jolla.manage.UserHandler),
            (r'/jolla/manage/tr/', jolla.manage.TranslateHandler),
            (r'/jolla/manage/post/', jolla.manage.PostHandler),
            (r'/jolla/manage/redirect/', jolla.manage.RedirectHandler),
            (r'/jolla/robots.txt', StaticFileHandler,
             {'path': os.path.join(self.config.root,
                                   'static', 'robots', 'jolla.txt')}),
            (r'/jolla/trans_process/', jolla.TransProcessHandler),
            (r'/jolla/sitemap/', jolla.SiteMapHandler),
            (r'/jolla/(?P<slug>[^/]+)/', jolla.ArticleHandler),
            (r'/jolla/.*', jolla.BaseHandler),
            # project
            (r'/project/docpie/', docpie.HomeHandler),
            (r'/project/docpie/document/', docpie.DocHandler),
            (r'/project/docpie/document/(?P<slug>[^/]+)/', docpie.DocHandler),
            (r'/project/docpie/try/', docpie.TryHandler),
            (r'/project/docpie/robots.txt', StaticFileHandler,
             {'path': os.path.join(self.config.root,
                                   'static', 'robots', 'docpie.txt')}),
            (r'/project/docpie/(favicon\.ico)', tornado.web.StaticFileHandler,
             {'path': os.path.join(self.config.root, 'static')}),

            (r'/project/wordz/', wordz.HomeHandler),
            (r'/project/wordz/quiz/', wordz.QuizHandler),
            (r'/project/wordz/modify/', wordz.ModifyHandler),

            (r'/api/(?P<source>html|md)/(?P<target>html|md)/',
             api.MdAndHtmlHandler),

            (r'/utility/sina/', utility.sina.HomeHandler),
            (r'/utility/sina/callback/', utility.sina.CallbackHandler),
            (r'/utility/sina/exec/', utility.sina.ExecHandler),
            (r'/utility/sina/[^/]+/', utility.sina.BaseHandler),
            (r'/utility/woopse/(\d+)/', utility.WoopseHandler),
            (r'/utility/fetch/', utility.fetch.FetchHandler),

            (r'/brey/', brey.BreyHandler),
            (r'/brey/robots\.txt', StaticFileHandler,
             {'path': os.path.join(self.config.root,
                                   'static', 'robots', 'brey.txt')}),
            (r'/brey/(favicon\.ico)', tornado.web.StaticFileHandler,
             {'path': os.path.join(self.config.root, 'static')}),
            (r'/brey/(?P<slug>[^/]+)/', brey.BreyHandler),

            (r'/utility/pts/', utility.TakeOutCalculateHandler),
            (r'/mail/', mail.MailHandler),

            (r'.*?\.php$(?i)', BlackListHandler),
            (r'.*', BaseHandler),
        )

        settings = {
            'template_path': os.path.join(self.config.root, 'template'),
            'debug': self.config.DEBUG,
            'login_url': '/login/',
            'ui_modules': {
                'WysBar': WysBarModule,
                'MdBar': MdBarModule,
                'ErrorImage': ErrorImageModule,
                'Time': TimeModule,
                'Tag': TagModule,
            },
        }

        if self.config.set_secret:
            sec_file = self.config.secret_file
            if sec_file is None:
                logger.warning(
                    "Can't share cookie secret without secret_file, "
                    "multi processes will not work as expected")
                secret = generate()
            else:
                with FileLock(sec_file), \
                        open(sec_file, 'r+', encoding='utf-8') as f:
                    secret = f.read().strip()
                    if not secret:
                        secret = generate()
                        logger.info('save secret to %s', sec_file)
                        f.seek(0)
                        f.truncate()
                        f.write(secret)
                    else:
                        logger.info('load secret from %s', sec_file)

            logger.info('set secret')
            settings['cookie_secret'] = secret

        if self.config.DEBUG:
            logger.warning('debug is on')

        super(Application, self).__init__(handlers, **settings)


def main(port):
    root = Config().root
    tornado.locale.load_translations(
        os.path.join(root, 'translations'))
    # set this tornado will ignore the borwser `Accept-Language` head, why?
    # tornado.locale.set_default_locale('zh')
    tornado.autoreload.watch(
        os.path.join(root, 'translations', 'zh.csv'))
    tornado.autoreload.watch(
        os.path.join(root, 'config'))
    http_server = tornado.httpserver.HTTPServer(Application(), xheaders=True)
    http_server.listen(port)
    logger.info('[port: %s]Sever started.', port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    from docpie import docpie as pie
    from lib.tool.bashlog import stdoutlogger, parse_level, filelogger
    from lib.config.tomorrow import Config as TomorrowConfig
    from lib.config.jolla import Config as JollaConfig

    args = dict(pie(__doc__))

    rootlogger = logging.getLogger()
    for _hdlr in rootlogger.handlers:
        rootlogger.removeHandler(_hdlr)
    for _filter in rootlogger.filters:
        rootlogger.removeFilter(_filter)

    stdoutlogger(rootlogger, logging.DEBUG, True)

    config = Config()
    tmr_cfg = TomorrowConfig()
    jolla_cfg = JollaConfig()

    tmr_level = parse_level(args['--tmr-level'] or tmr_cfg.log_level)
    jolla_level = parse_level(args['--jolla-level'] or jolla_cfg.log_level)
    tnd_level = parse_level(args['--tnd-level'] or config.tornado_log_level)
    tmr_file = args['--tmr-file'] or tmr_cfg.log_file
    jolla_file = args['--jolla-file'] or jolla_cfg.log_file
    tnd_file = args['--tnd-file'] or config.tornado_log_file

    tmr_logger = logging.getLogger('tomorrow')
    tmr_logger.setLevel(tmr_level)
    if tmr_file is None:
        rootlogger.warning("tomorrow file logger disabled")
    else:
        filelogger(tmr_file, tmr_logger, tmr_level)

    jolla_logger = logging.getLogger('jolla')
    jolla_logger.setLevel(jolla_level)
    if jolla_file is None:
        rootlogger.warning("jolla file logger disabled")
    else:
        filelogger(jolla_file, jolla_logger, tmr_level)

    tnd_logger = logging.getLogger('tornado')
    tnd_logger.setLevel(tnd_level)
    if tnd_file is None:
        rootlogger.warning("tornado file logger disabled")
    else:
        filelogger(tnd_file, tnd_logger, tnd_level)

    port = args['--port']
    if port is None:
        port = config.port
    else:
        port = int(port)

    main(port)
