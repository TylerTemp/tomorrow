import re
import logging
try:
    from itertools import zip_longest
    from urllib.parse import urlsplit
except ImportError:
    from itertools import izip_longest as zip_longest
    from urlparse import urlsplit

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.tool.md import md2html
sys.path.pop(0)

logger = logging.getLogger('tomorrow.jolla.base')


class BaseHandler(BaseHandler):
    p_re = re.compile(r'^<p>(.*?)</p>$')

    def make_tag(self, tags):
        for tag1, tag2 in zip_longest(tags[::2], tags[1::2]):
            first = ('<span class="am-badge am-badge-success am-radius">'
                     '%s'
                     '</span>') % self.locale.translate(tag1)
            yield first
            if tag2 is None:
                second = ''
            else:
                second = ('<span class="am-badge am-badge-primary am-radius">'
                          '%s'
                          '</span>') % self.locale.translate(tag2)
            yield second

    def get_source_name(self, link):
        sp = urlsplit(link)
        netloc = sp.netloc
        if netloc.endswith('.jolla.com'):
            return 'jolla'
        elif netloc.startswith('reviewjolla.blogspot.'):
            return 'reviewjolla'
        elif netloc.endswith('.jollausers.com'):
            return 'jollausers'

        else:
            sep = netloc.split('.')
            if len(sep) == 2:
                name = sep[0]
            elif len(sep) == 3:
                name = sep[1]
            else:
                name = netloc

            return name

    def make_source(self, name):
        if name == 'jolla':
            return '<span class="iconfont icon-jolla"> </span>'
        elif name == 'reviewjolla':
            return ('<img src="https://dn-jolla.qbox.me/reviewjolla.ico" '
                    'style="display: inline">')
        elif name == 'jollausers':
            return ('<img src="https://dn-jolla.qbox.me/jollausers.ico" '
                    'style="display: inline">')
        elif name is None:
            return ('<span class="am-badge am-badge-warning">%s</span>' %
                    self.locale.translate('original'))
        else:
            return '<span class="am-badge am-badge-secondary">%s</span>' % name

    def md_description_to_html(self, content):
        result = md2html(content)
        search = self.p_re.match(result)
        if search:
            return search.group(1)
        return result

    def write_error(self, status_code, **kwargs):
        # if self.if_debug(status_code, **kwargs):
        #     return

        msg = str(status_code)
        if True:  # status_code == 404:
            msg = 'Page Not Found'
            if 'exc_info' in kwargs:
                exc_info = kwargs['exc_info']
                if exc_info and len(exc_info) >= 2:
                    msg = getattr(exc_info[1], 'log_message', None) or msg

        return self.render(
            'jolla/error.html',
            msg=msg or 'Unknown ERROR'
        )