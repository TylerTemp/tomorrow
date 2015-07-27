import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler, EnsureUser
from lib.tool.md import md2html, html2md, escape
from lib.db import User
sys.path.pop(0)

class MdAndHtmlHandler(BaseHandler):

    # @EnsureUser(User.normal, True)
    def get(self, source, target):
        content = self.get_argument('content')

        if source == 'html':
            content = html2md(content)
        elif self.current_user['type'] < User.root:
            content = escape(content)

        if target == 'html':
            content = md2html(content)
        return self.write(content)

    def post(self, *a, **k):
        return self.get(*a, **k)

    def check_xsrf_cookie(self):
        return True
