# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote
from pprint import pprint
import json
from pymongo import ReturnDocument

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import User
sys.path.pop(0)

u = User._user

for each in u.find({}):
    each['intro'] = {'content': None,
                     'show_in_home': True, 'show_in_article': False}
    each['donate'] = {'new': None, 'old': None, 'info': None,
                      'show_in_home': True, 'show_in_article': True}
    u.replace_one({'_id': each['_id']}, each)