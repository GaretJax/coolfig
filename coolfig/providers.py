import os
from functools import partial


NOT_PROVIDED = object()


class ConfigurationProvider(object):
    def get(self, key):
        raise NotImplementedError()


class DictConfig(ConfigurationProvider):
    """
    Loads configuration values from the passed dictionary.
    """
    def __init__(self, conf_dict, prefix=''):
        self._conf_dict = conf_dict
        self._prefix = prefix

    def get(self, key):
        try:
            return self._conf_dict[self._prefix + key]
        except KeyError:
            return NOT_PROVIDED


EnvConfig = partial(DictConfig, os.environ)
