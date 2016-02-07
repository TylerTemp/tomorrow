import logging
try:
    Str = basestring
except NameError:
    Str = str


class Log(object):

    logger = logging.getLogger()

    def __init__(self):
        super(Log, self).__init__()
        log = self.logger

        for attr in ('debug', 'info', 'warning', 'error'):
            if hasattr(log, attr):
                self.__dict__[attr] = getattr(log, attr)
            else:
                logging.warning('%r has not %r in logger',
                                self.__class__.__name__, attr)


# def with_logger(logger=None):
#     if isinstance(logger, Str):
#         logger = logging.getLogger(logger)
#
#     func_logger = logger
#
#     def deco(cls):
#         old_init = cls.__init__
#
#         def init(self, *a, **k):
#             old_init(self, *a, **k)
#
#             if func_logger is not None:
#                 self.logger = logger = func_logger
#             else:
#                 logger = getattr(self, 'logger', None)
#                 if logger is None:
#                     self.logger = logger = logging.getLogger()
#
#             self.debug = logger.debug
#             self.info = logger.info
#             self.warning = logger.warning
#             self.error = logger.error
#
#         cls.__init__ = init
#
#         return cls
#
#     return deco
#
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG)
#
#     @with_logger()
#     class Parent(object):
#         pass
#
#     @with_logger('sub')
#     class Sub(Parent):
#         pass
#
#     class GrandSub(Sub):
#         pass
#
#     grand = GrandSub()
#     grand.info('grand')
