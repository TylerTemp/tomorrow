import pymongo
import logging
from passlib.hash import sha256_crypt
from bson import ObjectId
# import sys
# import os
# sys.path.insert(0, os.path.normpath(os.path.join(__file__, '..', '..', '..')))
from lib.tool.generate import generate
# from base import Base
from .base import Base

logger = logging.getLogger('db.wordz')
client = pymongo.MongoClient()
db = client['wordz']


class Glossary(Base):

    pass