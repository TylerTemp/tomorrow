import os
import sys

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)

class RedirectHandler(BaseHandler):

    def initialize(self, to, permanently=False):
        self._to = to
        self._permanently = permanently

    def get(self, *a, **k):
        return self.redirect(self._to, self._permanently)

    post = get
