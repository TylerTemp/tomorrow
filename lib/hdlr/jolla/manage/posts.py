import logging
from ..base import BaseHandler, EnsureUser
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


class PostHandler(BaseHandler):
    logger = logging.getLogger('jolla.manage.posts')

    @EnsureUser(EnsureUser.ROOT)
    def get(self):
        return self.render(
            'jolla/manage/post.html'
        )
