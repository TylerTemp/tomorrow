# coding: utf-8
# this file is to adjust the data in database

import sys
import os
import json

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import Wordz
sys.path.pop(0)

with open('/tmp/result.json', 'r', encoding='utf-8') as f:
    result = json.load(f)

for each in result:
    Wordz().save(**each)
