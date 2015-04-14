class Config(object):
    _ins = None

    def __new__(cls):
        if cls._ins is None:
            ins = super(Config, cls).__new__(cls)
            ins.debug = True
            cls._ins = ins

        return cls._ins
