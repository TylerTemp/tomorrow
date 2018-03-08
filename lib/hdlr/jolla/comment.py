import tornado.web
import tornado.escape
import logging
import time
try:
    from urllib.parse import unquote, quote, urlsplit
except ImportError:
    from urllib import quote
    from urlparse import unquote, urlsplit
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

from .base import BaseHandler

from lib.db.jolla import Article, Comment


class CommentHandler(BaseHandler):

    def post(self, article_slug):
        # article_slug = self.get_argument('article-slug')
        article = Article(article_slug)
        if not article:
            raise tornado.web.HTTPError(404, 'article not found')
        nickname = self.get_argument('nickname').strip()
        if not nickname:
            raise tornado.web.HTTPError(400, 'nickname empty')
        email = self.get_argument('email', '').strip() or None
        content = self.get_argument('content').rstrip()
        if not content.strip():
            raise tornado.web.HTTPError(400, 'comment empty')
        headers = self.request.headers
        ips = headers.get('X-Forwarded-For', None)
        if ips:
            ip = ips.split(',')[0].strip()
        else:
            ip = headers.get('X-Real-Ip', self.request.remote_ip)
        user_agent = headers.get('User-Agent', None)
        comment = Comment()
        now_timestamp = time.time()
        comment.update({
            'nickname': nickname,
            'email': email,
            'content': content,
            'ip': ip,
            'user_agent': user_agent,
            'create_time': now_timestamp,
            'update_time': now_timestamp,
            'article_id': article._id,
        })
        comment.save()
        return self.redirect('/%s/#%s' % (article_slug, comment._id))
