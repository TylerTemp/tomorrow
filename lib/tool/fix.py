# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote
from pprint import pprint
import json
from pymongo import ReturnDocument

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import Article
sys.path.pop(0)

a = Article._article

for each in a.find({}):
    each['hide'] = False
    a.replace_one({'_id': each['_id']}, each)