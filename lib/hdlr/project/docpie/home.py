import logging

import sys
import os
sys.path.insert(0, os.path.normpath(
                    os.path.join(__file__, '..', '..', '..', '..')))
from lib.hdlr.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.project.docpie.home')


class HomeHandler(BaseHandler):

    def get(self):
        return self.render(
            'project/docpie/home.html'
        )
