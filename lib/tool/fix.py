# coding: utf-8
# this file is to adjust the data in database

import sys
import os
from urllib.parse import unquote, quote

rootdir = os.path.normpath(os.path.join(__file__, '..', '..', '..'))
sys.path.insert(0, rootdir)
from lib.db import Message
sys.path.pop(0)

coll = Message._msg

for each in coll.find({}):
    coll.update_one(each, {'$set': {
                                     'sender_delete': False,
                                     'receiver_status': Message.UNREAD
    }})
