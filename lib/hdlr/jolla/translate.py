import tornado.web
import logging
import json

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.hdlr.base import BaseHandler
from lib.db import Article
sys.path.pop(0)

class TranslateHandler(BaseHandler):

    def get(self):
        pass
