# coding: utf-8
import tornado.web
import logging
import json
import time
from bson.objectid import ObjectId
try:
    from urllib.parse import unquote
    from urllib.parse import quote
except ImportError:
    from urllib import unquote
    from urllib import quote

import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(__file__,
                                                 '..', '..', '..', '..')))
from lib.db import Article
from lib.db import Jolla
from lib.hdlr.dash.base import its_myself
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.secure')


class ArticleHandler(BaseHandler):

    @tornado.web.authenticated
    @its_myself
    def get(self, user):

        self.xsrf_token

        return self.render(
            'dash/article.html',
            cc_license=Article.CC_LICENSE,
            pub_license=Article.PUB_LICENSE,
            articles=self.get_articles(self.current_user['user'])
        )

    @tornado.web.authenticated
    @its_myself
    def post(self, user):
        self.check_xsrf_cookie()

        if self.get_argument('action') == 'delete':
            self.delete_article()
        else:
            self.save_article()

    def get_articles(self, user):
        for each in Article.find_by(user):
            each['id'] = str(each.pop('_id'))
            each['edit_time'] = self.format_time(each.pop('edittime'))
            each['create_time'] = self.format_time(each.pop('createtime'))
            if each['board'] == 'jolla':
                each['url'] = '/jolla/blog/%s/' % each['url']
            if 'transinfo' in each:
                each['edit'] = \
                    '/jolla/translate/%s/' % each['transinfo']['url']
                each['reprint'] = each['transinfo']['reprint']
                each['source_title'] = each['transinfo']['title']
                each['source_url'] = each['transinfo']['link']
            else:
                each['edit'] = each['reprint'] = each['source_title'] \
                    = each['source_url'] = None
            yield each

    def format_time(self, t):
        if self.locale.code.startswith('en'):
            return time.ctime(t)
        return time.strftime('%Y年%m月%d日，%H:%M', time.localtime(t))

    def save_article(self):
        pass

    def delete_article(self):
        coll = Article.get_collect()
        id_obj = ObjectId(self.get_argument('id'))
        arti_info = coll.find_one({'_id': id_obj})
        if not arti_info:
            raise tornado.web.HTTPError(500,
                                        'article id %s not exists' % id_obj)
        if ('transinfo' in arti_info and
                arti_info['transinfo']['status'] == Article.TRUSTED):
            jolla_url = arti_info['transinfo']['url']
            jolla_post = Jolla(jolla_url)
            assert not jolla_post.new, 'Jolla(%s) not exists' % jolla_url
            jolla_info = jolla_post.get()
            logger.info('remove jolla trusted translation %s',
                        jolla_info['url'])
            jolla_info['trusted_translation'] = None
            jolla_post.save()
        logger.info('remove article %s', arti_info['url'])
        coll.delete_one(arti_info)

        self.write(json.dumps({'error': 0}))
