import sys
import json
from bson import ObjectId

from lib.db.jolla import Article


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


save_to = sys.argv[1]

articles = []

for article in Article.find():
    # print(article.__dict__['__info__'])
    article_dict = article.__dict__['__info__']
    article_dict['_id'] = str(article_dict['_id'])
    articles.append(article_dict)

with open(save_to, 'w', encoding='utf-8') as out:
    # json.dump(articles, out, ensure_ascii=False, indent=2)
    json.dump(articles, out, cls=JSONEncoder, ensure_ascii=False, indent=2)
    # out.write(JSONEncoder().encode(analytics))
