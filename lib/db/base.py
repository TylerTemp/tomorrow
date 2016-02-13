import pymongo
from lib import Log


class Base(Log):
    _default = {'_id': None}
    collection = None

    def __init__(self):
        super(Base, self).__init__()
        self.__dict__['__info__'] = {}

    def __getattr__(self, item):
        default = self._default
        attrs = self.__dict__['__info__']

        if item in attrs:
            return attrs[item]

        if item in default:
            default_val = default[item]
            if isinstance(default_val, (dict, list)):
                attrs[item] = default_val = default_val.copy()  # re-bind
            return default_val

        raise AttributeError('%r object has no attribute %r' %
                             (self.__class__.__name__, item))

    def __setattr__(self, key, value):
        self.__dict__['__info__'][key] = value

    def __delattr__(self, item):
        attrs = self.__dict__['__info__']
        if item not in attrs:
            raise AttributeError(repr(item))

        del attrs[item]

    def __bool__(self):
        return self._id is not None

    __nozero__ = __bool__

    def update(self, *a, **k):
        self.__dict__['__info__'].update(*a, **k)

    def remove(self):
        result = self.collection.delete_one({'_id': self._id})
        return result.deleted_count

    def _validate_attrs(self):
        attrs = self.__dict__['__info__']
        default = self._default
        if not set(attrs).issubset(default):
            raise ValueError('Unexpected field(s) %s' %
                             set(attrs).difference(default))

    def _before_save(self):
        attrs = self.__dict__['__info__']
        default = self._default
        for common in set(attrs).intersection(default):
            if attrs[common] == default[common]:
                del attrs[common]

    def save(self):
        self._before_save()
        self._validate_attrs()
        attrs = self.__dict__['__info__']
        if not attrs:
            self.warning('empty save, abort')
            return

        collection = self.collection
        _id = self._id

        if _id is not None:
            result = collection.replace_one({'_id': _id}, attrs)
            if result.matched_count >= 1:
                return
            self.warning('No id matched, save directly')

        insert_result = collection.insert_one(attrs)
        _id = insert_result.inserted_id
        self._id = _id

    @classmethod
    def find_one(cls, *a, **k):
        result = cls.collection.find_one(*a, **k)
        ins = cls()
        if result is not None:
            ins.update(result)
        return ins

    @classmethod
    def find(cls, *a, **k):
        for each in cls.collection.find(*a, **k):
            ins = cls()
            ins.update(each)
            yield ins


client = pymongo.MongoClient()
db = client['meta']


class Meta(Base):
    collection = db.meta
    _default = {
        '_id': None,
        '_group': None,
        '_title': None,
    }

    def __init__(self, _title=None, _group=None):
        super(Meta, self).__init__()
        if _title is not None and _group is not None:
            result = self.collection.find_one(
                {'_title': _title, '_group': _group})
            if result is None:
                self._title = _title
                self._group = _group
            else:
                self.update(result)

    def _validate_attrs(self):
        if not (self._group and self._title):
            raise ValueError('%s can not be empty' % (
                'title' if self._title is None else 'group'))

        return True

    def _before_save(self):
        return True
