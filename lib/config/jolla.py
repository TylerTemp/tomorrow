import os
from .base import Base, Config as RootConfig
import logging

logger = logging.getLogger('config.jolla')


class Config(Base):
    _parent = RootConfig()


    def __init__(self):
        if self.tomorrow == self._get_default()['tomorrow']:
            logger.warning("oauth2 can't work without setting tomorrow config")

    def _get_file(self):
        return os.path.join(self.root, 'config', 'jolla.conf')

    def _get_default(self):
        return {
            'log_level': logging.DEBUG,
            'log_file': '{TMPDIR}/jolla.log',
            'tomorrow': {
                'key': None,
                'secret': None,
                'token_url': None,
                'auth_url': None,
                'callback': None
            }
        }

    @property
    def host(self):
        return self._parent.jolla_host