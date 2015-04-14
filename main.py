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
import tornado
import tornado.web
import tornado.httpserver
import tornado.options

from lib.bashlog import stdoutlogger
from lib.bashlog import filelogger
from lib.hdlr.notfound import AddSlashOr404Handler
from lib.config import Config

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
            (r'.*', AddSlashOr404Handler),
        )

        settings = {
            'template_path': os.path.join(rootdir, 'template'),
            'static_path': os.path.join(rootdir, 'static'),
            'debug': self.config.debug,
        }

        super(Application, self).__init__(handlers, **settings)


def main(port):
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
