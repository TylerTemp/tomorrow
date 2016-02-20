import logging
import tornado.web
from lib.db.jolla import Redirect, Article
from ..base import BaseHandler, EnsureUser


class RedirectHandler(BaseHandler):
    logger = logging.getLogger('jolla.manage.redirect')

    @EnsureUser(EnsureUser.ROOT)
    def get(self):
        return self.render(
            'jolla/manage/redirect.html',
            redirects=Redirect.find({}),
        )

    @EnsureUser(EnsureUser.ROOT)
    def post(self):
        redi = Redirect(self.get_argument('source'))

        if self.get_argument('action', None) == 'delete':
            return self.delete(redi)

        return self.save(redi)

    def save(self, redirect):
        redirect.target = self.get_argument('target').strip()

        if not Article(redirect.target):
            raise tornado.web.HTTPError(404,
                                        'no such article %r' % redirect.source)

        if redirect.source == redirect.target:
            raise tornado.web.HTTPError(
                400, 'source and target should not be the same')

        redirect.permanent = bool(self.get_argument('permanent', False))
        self.info('redirect %r -> %r (%s)',
                  redirect.source,
                  redirect.target,
                  redirect.permanent)

        redirect.save()

        return self.write({'source': redirect.source,
                           'target': redirect.target,
                           'permanent': redirect.permanent})

    def delete(self, redirect):
        if not redirect:
            raise tornado.web.HTTPError(404,
                                        '%r not found' % redirect.source)
        redirect.remove()

        return self.write({'error': 0, 'source': redirect.source})
