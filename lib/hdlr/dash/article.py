# coding: utf-8
import tornado.web
import logging
import json
import time
import re
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
from lib.tool.minsix import py3
from lib.hdlr.dash.base import ItsMyself
from lib.hdlr.dash.base import BaseHandler
sys.path.pop(0)

logger = logging.getLogger('tomorrow.dash.secure')


class ArticleHandler(BaseHandler):

    @tornado.web.authenticated
    @ItsMyself('article/')
    def get(self, user):

        self.xsrf_token

        return self.render(
            'dash/article.html',
            cc_license=Article.CC_LICENSE,
            pub_license=Article.PUB_LICENSE,
            articles=self.get_articles(self.current_user['user']),
            act=('article', )
        )

    @tornado.web.authenticated
    @ItsMyself('article/')
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
                each['share'] = each['transinfo']['share']
                each['source_title'] = each['transinfo']['title']
                each['source_url'] = each['transinfo']['link']
            else:
                each['edit'] = each['share'] = each['source_title'] \
                    = each['source_url'] = None
            yield each

    def format_time(self, t):
        if self.locale.code.startswith('en'):
            return time.ctime(t)
        return time.strftime('%Y年%m月%d日，%H:%M', time.localtime(t))

    def save_article(self):
        coll = Article.get_collect()
        id_obj = ObjectId(self.get_argument('id'))
        title = self.get_argument('title')
        # jQuery will send 'true'/'false', and tornado will not deal this
        show_email = (self.get_argument('show_email').lower() != 'false')
        share = self.get_share_argument()

        logger.info('update id(%s): title: %s; show_email: %s; share: %s',
                    id_obj, title, show_email, share)

        assert title
        coll.update_one(
            {'_id': id_obj},
            {'$set':
                {
                    'title': title,
                    'show_email': show_email,
                    'transinfo.share': share,
                }
            }
        )

        return self.write(json.dumps({'error': 0}))

    re_share = re.compile(r'^share\[(?P<key>.*?)\]$')
    def get_share_argument(self):
        result = []
        re_share = self.re_share
        logger.debug(self.request.arguments)
        for k, v in self.request.arguments.items():
            logger.debug('k: %r; v: %r', k, v)
            match = re_share.match(k)
            if match is not None:
                k = match.groupdict()['key']
                if isinstance(v, (list, tuple)):
                    v = v[0]
                if py3:
                    v = v.decode('utf-8')
                # result[v] = match.groupdict()['key']
                result.append({'name': v, 'url': k})
        return result

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
