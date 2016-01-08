import pymongo
import logging
from bson import ObjectId
# import sys
# import os
# sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
# from base import Base
from .base import Base

logger = logging.getLogger('db.jolla')
client = pymongo.MongoClient()
db = client['jolla']


class User(Base):
    pass


class Article(Base):
    pass


class Author(Base):
    pass