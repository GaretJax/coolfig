import os
from functools import partial


NOT_PROVIDED = object()


class ConfigurationProvider(object):
    def get(self, key):
        raise NotImplementedError()

    def iterprefixed(self, prefix):
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

    def iterprefixed(self, prefix):
        prefix = self._prefix + prefix
        for k in self._conf_dict:
            if k.startswith(prefix):
                yield (k[len(self._prefix):], self._conf_dict[k])


class EnvDirConfig(ConfigurationProvider):
    def __init__(self, base_path):
        self._base_path = base_path

    def get(self, key):
        path = os.path.join(self._base_path, key)
        try:
            with open(path) as fh:
                return fh.read()
        except:  # TODO: Handle OSErrors (not found, not readable,...)
            return NOT_PROVIDED


EnvConfig = partial(DictConfig, os.environ)
SecretsConfig = partial(EnvDirConfig, '/run/secrets')
