import re
import logging
import time
from bson import ObjectId
import tornado.locale
from amazedown import link_icon_tab, link_image
try:
    from itertools import zip_longest
    from urllib.parse import urlsplit
except ImportError:
    from itertools import izip_longest as zip_longest
    from urlparse import urlsplit

from lib.hdlr.base import BaseHandler, get_exc_plus
from lib.tool.md import md2html
from lib.config.jolla import Config
from lib.db.jolla import User

logger = logging.getLogger('jolla')


class BaseHandler(BaseHandler):
    p_re = re.compile(r'^<p>(.*?)</p>$')

    config = Config()

    def render(self, template_name, **kwargs):
        kwargs.setdefault('user', self.current_user)
        kwargs.setdefault('HOST', self.config.host)
        kwargs.setdefault('TOMORROW_HOST', self.config.tomorrow_host)

        assert 'static_path' not in kwargs
        kwargs['static_path'] = self.static_path

        return super(BaseHandler, self).render(template_name, **kwargs)

    def md2html(self, md):
        return md2html(
                md,
                extensions=[link_image.makeExtension(),
                            link_icon_tab.makeExtension(host=self.config.host),
                            ])

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

    def make_source(self, link):
        if link is None:
            return ('<span class="am-badge am-badge-warning">%s</span>' %
                    self.locale.translate('original'))

        name = self.get_source_name(link)

        if name == 'jolla':
            return '<span class="iconfont icon-jolla"> </span>'
        elif name == 'reviewjolla':
            return ('<img src="https://dn-jolla.qbox.me/reviewjolla.ico" '
                    'style="display: inline">')
        elif name == 'jollausers':
            return ('<img src="https://dn-jolla.qbox.me/jollausers.ico" '
                    'style="display: inline">')
        else:
            return '<span class="am-badge am-badge-secondary">%s</span>' % name

    def md_description_to_html(self, content):
        result = md2html(content)
        search = self.p_re.match(result)
        if search:
            return search.group(1)
        return result

    def login(self, uid, token, expire_at):
        self.set_secure_cookie('uid', uid)
        self.set_secure_cookie('token', token)
        self.set_secure_cookie('expire_at', str(expire_at))

    def logout(self):
        self.clear_cookie('uid')
        self.clear_cookie('token')
        self.clear_cookie('expire_at')

    def get_current_user(self):
        uid = self.get_secure_cookie('uid')
        if not uid:
            return None
        expire = float(self.get_secure_cookie('expire_at'))
        if expire < time.time():
            logger.debug('user %s expired', uid)
            self.logout()
            return None

        u = User(ObjectId(uid.decode('utf-8')), self.locale.code[:2])
        if not u:
            self.logout()
            return None
        return u

    def write_error(self, status_code, **kwargs):
        msg = self.get_error(status_code, **kwargs)
        if self.is_ajax():
            return self.write({'error': -1, 'code': -1, 'message': msg})

        return self.render(
            'jolla/error.html',
            code=status_code,
            msg=msg
        )