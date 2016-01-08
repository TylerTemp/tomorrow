class Base(object):
    _default = {'_id': None}
    collection = None

    def __init__(self):
        self.__dict__['__info__'] = {}

    def __getattr__(self, item):
        default = self._default
        attrs = self.__dict__['__info__']

        if item in attrs:
            return attrs[item]

        if item in default:
            return default[item]

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

    def _validate_attrs(self):
        attrs = self.__dict__['__info__']
        default = self._default
        if not set(attrs).issubset(default):
            raise ValueError('Unexpected field(s) %s' %
                             set(attrs).difference(default))

    def save(self):
        self._validate_attrs()
        attrs = self.__dict__['__info__']
        collection = self.collection
        _id = self._id

        if _id is not None:
            collection.replace_one({'_id': _id}, attrs)
            return

        insert_result = collection.insert_one(self.article_info)
        _id = insert_result.inserted_id
        attrs['_id'] = _id
