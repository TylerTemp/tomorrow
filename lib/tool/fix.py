# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import db
sys.path.pop(0)

article = db.article
jolla  = db.jolla

slug = 'Early-access%3A-Sailfish-OS-Aaslakkajärvi-with-private-browsing-and-more-is-here!'
slug = unquote(slug)
newurl = 'sailfish-os-aaslakkajarvi'

a = article.find_one({'url': slug})
a['url'] = newurl
a['transref'] = newurl
a['transinfo']['url'] = newurl
a['title'] = 'Sailfish系统Aaslakkajärvi带来隐私浏览和更多特性！'
a['transinfo']['title'] = 'Sailfish OS Aaslakkajärvi with private browsing and more is here!'

j = jolla.find_one({'url': slug})
j['url'] = newurl
j['trusted_translation'] = newurl
j['title'] = 'Sailfish OS Aaslakkajärvi with private browsing and more is here!'

article.save(a)
jolla.save(j)
