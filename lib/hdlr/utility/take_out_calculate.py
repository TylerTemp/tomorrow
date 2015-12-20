import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)

class TakeOutCalculateHandler(BaseHandler):

    def get(self):
        return self.render(
            'utility/take-out-calculate.html'
        )