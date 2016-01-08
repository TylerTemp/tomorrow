# coding: utf-8
# this file is to adjust the data in database

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db.tomorrow import Article
sys.path.pop(0)

article = Article.collection

def fix_blog_article(art):
    art.pop('board')
    art.pop('title', None)
    art.pop('transinfo', None)
    art.pop('status', None)
    art.pop('index', None)
    art['create_time'] = art['createtime']
    art['edit_time'] = art['edittime']
    if 'headimg' in art:
        art['banner'] = art.pop('headimg')

for each in article.find({}):
    if each['board'] != 'blog':
        article.delete_one({'_id': each['_id']})
        continue
    fix_blog_article(each)
    article.replace_one({'_id': each['_id']}, each)