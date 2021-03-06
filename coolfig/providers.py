import errno
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

    def __init__(self, conf_dict, prefix=""):
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
                yield (k[len(self._prefix) :], self._conf_dict[k])


class EnvDirConfig(ConfigurationProvider):
    def __init__(self, base_path, prefix=""):
        self._base_path = base_path
        self._prefix = prefix

    def get(self, key):
        path = os.path.join(self._base_path, key)
        try:
            with open(path) as fh:
                return fh.read()
        except IOError as e:
            if e.errno == errno.EACCES:  # Wrong permissions
                raise
            return NOT_PROVIDED  # File does not exist

    def iterprefixed(self, prefix):
        prefix = self._prefix + prefix
        if os.path.exists(self._base_path):
            for k in os.listdir(self._base_path):
                path = os.path.join(self._base_path, k)
                if k.startswith(prefix) and os.path.isfile(path):
                    yield (k[len(self._prefix) :], self.get(k))


class FallbackProvider(ConfigurationProvider):
    def __init__(self, providers):
        self._providers = list(providers)

    def get(self, key):
        for provider in self._providers:
            value = provider.get(key)
            if value is not NOT_PROVIDED:
                break
        else:
            value = NOT_PROVIDED
        return value

    def iterprefixed(self, prefix):
        seen = set()
        for provider in self._providers:
            for k, v in provider.iterprefixed(prefix):
                if k not in seen:
                    seen.add(k)
                    yield k, v


EnvConfig = partial(DictConfig, os.environ)
