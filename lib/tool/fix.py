# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote
from pprint import pprint
import json
from pymongo import ReturnDocument

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import Article, Email
sys.path.pop(0)

a = Article._article
e = Email._email

for each in a.find({}):
    each.pop('hide', None)
    a.replace_one({'_id': each['_id']}, each)

for each in e.find({}):
    if each['name'] == '_extra':
        continue
    if each['name'] == 'invite_no_verify':
        each['default'] = each['defualt']
    article = Article(each['name'])
    article.add('hide', None, None,
                  zh={'title': each['zh']['title'],
                      'content': each['zh']['content'],
                      'description': None},
                  en={'title': each['default']['title'],
                      'content': each['default']['content'],
                      'description': None},
                  show_email=False)
    article.save()

with open(os.path.join(os.path.dirname(__file__), 'fix.json'), 'r', encoding='utf-8') as f:
    articles = json.load(f)
    a.insert_many(articles)
