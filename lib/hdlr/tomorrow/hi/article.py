# coding: utf-8
import tornado.web
import logging
import time
try:
    from urllib.parse import unquote, quote
except ImportError:
    from urllib import unquote, quote

from lib.db.tomorrow import Article
from .base import BaseHandler, ItsNotMyself

logger = logging.getLogger('tomorrow.hi.article')


class ArticleHandler(BaseHandler):

    @ItsNotMyself('article/')
    def get(self, user):
        user_name = unquote(user)

        return self.render(
            'tomorrow/admin/hi/article.html',
            user_name=user_name,
            articles=self.get_articles(user_name),
        )

    @ItsNotMyself('article')
    def get_articles(self, user):
        for each in Article.find_by(user):
            if 'zh' in each and 'en' in each:
                if self.locale.code[:2] != 'zh':
                    meta = each.pop('en')
                else:
                    meta = each.pop('zh')
            else:
                meta = each.pop('zh', None) or each.pop('en')

            each['create_time'] = self.format_time(each['createtime'])
            each['edit_time'] = self.format_time(each['edittime'])
            each['create_time_attr'] = time.strftime(
                '%Y-%m-%dT%H:%M:%S',
                time.localtime(each.pop('createtime')))
            each['edit_time_attr'] = time.strftime(
                '%Y-%m-%dT%H:%M:%S',
                time.localtime(each.pop('edittime')))
            slug = quote(each.pop('slug'))
            if each['board'] == 'jolla':
                each['url'] = '//%s/%s/' % (self.JOLLA_HOST, slug)
            else:
                each['url'] = '/blog/%s/' % slug
            each.update(meta)
            yield each

    def format_time(self, t):
        if self.locale.code.startswith('en'):
            return time.ctime(t)
        return time.strftime('%m月%d日，%H:%M', time.localtime(t))
