import tornado.web
import tornado.escape
import logging
import time

from .base import BaseHandler
from lib.tool.avatar import gen_avatar


class AvatarHandler(BaseHandler):

    def get(self, avatar_slug):
        self.set_header('Content-Type', 'image/png')
        return self.write(gen_avatar(avatar_slug))
