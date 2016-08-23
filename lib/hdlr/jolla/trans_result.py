import logging
from .base import BaseHandler
from lib.db.base import Meta
from tornado.escape import xhtml_escape


class Record(Meta):
    _default = {
        '_id': None,
        '_ips': [],
    }

    # def __init__(self, *a, **k):
    #     super(Record, self).__init__(*a, **k)
    #     attrs = self.__dict__['__info__']
    #     for k, v in attrs.items():
    #         if isinstance(v, list):
    #             attrs[k] = set(v)

    def _before_save(self):
        attrs = self.__dict__['__info__']
        default = self._default

        for k, v in attrs.items():
            if isinstance(v, set):
                attrs[k] = list(v)
            if not k.startswith('_') and v == 0:
                del attrs[v]

        for common in set(attrs).intersection(default):
            if attrs[common] == default[common]:
                del attrs[common]



class TransProcessHandler(BaseHandler):
    logger = logging.getLogger('jolla.trans_process')

    def get(self):
        record = Record(_title='trans_process', _group='jolla')
        # self.info(self.record.__dict__['__info__'])
        attrs = sorted(
            (
                (k, v)
                for k, v in record.__info__.items()
                if not k.startswith('_')
            ),
            key=lambda k_v: k_v[-1])
        self.write('<h1>Thanks</h1>')
        self.write('<ul>')
        for k, v in attrs:
            self.write('<li>%s: %s</li>' % (xhtml_escape(k), v))
        self.write('</ul>')


    def post(self):
        ip = self.request.remote_ip
        record = Record(_title='trans_process', _group='jolla')
        if not record._ips:
            record._ips = []
        elif isinstance(record._ips, list):
            record._ips = record._ips
        ips = record._ips
        # self.info(ip)
        # self.info(record._ips)

        # if ip in ips:
        if False:
            self.debug('dup ip')
        else:
            video = set(x.decode('utf-8') for x in self.request.arguments.get('video', []))
            text = set(x.decode('utf-8') for x in self.request.arguments.get('text', []))
            app_raw = self.get_argument('app', '').strip()
            if app_raw:
                app = set(each.strip() for each in app_raw.split(','))
            else:
                app = set()
            if video or text or app:
                self.debug('add ip %s', ip)
                ips.append(ip)
                # self.info(record._ips)
                # self.info(Record(_title='trans_process', _group='jolla')._ips)
            
            for each in video.union(text).union(app):
                old = getattr(record, each, 0)
                setattr(record, each, old + 1)
                self.debug('%s: %s', each, old + 1)
            record.save()

        return self.redirect(self.request.uri)
