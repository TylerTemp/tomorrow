import os
from .base import Base, Config as RootConfig
import logging


class Config(Base):
    _parent = RootConfig()
    logger = logging.getLogger('tomorrow.config')

    def _get_file(self):
        return os.path.join(self.root, 'config', 'tomorrow.conf')

    def _get_default(self):
        return {
            'log_level': logging.DEBUG,
            'log_file': '{TMPDIR}/tomorrow.log',
        }

    @property
    def host(self):
        return self._parent.tomorrow_host
