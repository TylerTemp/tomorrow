import tornado.web
import logging

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import Article
sys.path.pop(0)

logger = logging.getLogger('tomorrow.ui.license')


class LicenseModule(tornado.web.UIModule):

    def render(self, license, name, emaillink=None):
        if emaillink is None:
            emaillink = ''
        if license == Article.CC_LICENSE:
            return '''
本文基于
<a href="https://creativecommons.org/licenses/by/2.0/legalcode" target="_blank">
    <span class="am-icon-cc"> CC协议</span>
</a>发布。作商业用途的转载请先联系%s %s。''' % (emaillink, name)
        if license == Article.PUB_LICENSE:
            return '''
本文由%s %s基于
<a href="http://choosealicense.com/licenses/unlicense/" target="_blank">
    公共邻域协议
<a/>发布。请在该协议下自由使用。''' % (emaillink, name)
