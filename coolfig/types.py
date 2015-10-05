"""
Common types for settings classes.
"""
import importlib


class LazyCallable(object):
    def __init__(self, module_path, callable_path):
        self._module_path = module_path
        self._callable_path = callable_path
        self._func = None

    @property
    def func(self):
        if self._func is None:
            self._load()
        return self._func

    def _load(self):
        try:
            func = importlib.import_module(self._module_path)
            for part in self._callable_path.split('.'):
                func = getattr(func, part)
            self._func = func
        except (ImportError, AttributeError):
            self._func = self._not_implemented

    def _not_implemented(self, *args, **kwargs):
        raise NotImplementedError("'{}.{}' could not be imported".format(
            self._module_path, self._callable_path))

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def boolean(string):
    return string.lower() in set(['1', 'true', 'yes', 'on', 'y'])


sqlalchemy_url = LazyCallable('sqlalchemy.engine.url', 'make_url')

django_db_url = LazyCallable('environ', 'Env.db_url_config')
django_cache_url = LazyCallable('environ', 'Env.cache_url_config')


def list(inner_type, sep=','):
    def convert(string):
        return [inner_type(s.strip()) for s in string.split(sep)]
    return convert


def dottedpath(string):
    module_path, name = string.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, name)
