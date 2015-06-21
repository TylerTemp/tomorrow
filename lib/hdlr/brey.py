import os
import sys

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)

class ForBrey(BaseHandler):

    def get(self):
        return self.render('brey.html')
