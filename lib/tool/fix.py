# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import db
sys.path.pop(0)

article = db.article

for each in article.find({}):
    if 'transinfo' in each:
        transinfo = each['transinfo']
        share = transinfo.pop('reprint')
        result = []
        print(each['url'])
        for name, url in share.items():
            print(name, url)
            result.append({'name': name, 'url': url})
        transinfo['share'] = result
        article.save(each)
