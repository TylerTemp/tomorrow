# coding: utf-8
# this file is to adjust the data in database

import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.db import Article
sys.path.pop(0)

files = ['brey-news.md', 'brey-java.md', 'brey-home.md', 'brey-booklist.md']

for file_name in files:
    path = os.path.join('/tmp', file_name)
    slug = os.path.splitext(file_name)[0]
    print(path, slug)
    with open(path, 'r', encoding='utf-8') as f:
        title = next(f)[2:-1]
        content = f.read()

    a = Article(slug)
    a.add(board='hide', author=None, email=None, en={
        'title': title,
        'content': content,
        'description': None,
    })

    a.save()
