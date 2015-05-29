from six import with_metaclass

from .providers import NOT_PROVIDED


class ImproperlyConfigured(Exception):
    """
    Raised when e request for a configuration value cannot be fulfilled.
    """


class Value(object):
    def __init__(self, type, default=NOT_PROVIDED, key=None):
        self.type = type
        self.default = default
        self.key = key

    def __call__(self, settingsobj, config_provider, key):
        key = self.key if self.key else key
        value = config_provider.get(key)
        if value is NOT_PROVIDED and self.default is NOT_PROVIDED:
            # Value is required but was not provided
            raise ImproperlyConfigured('no value set for {}'.format(key))
        elif value is NOT_PROVIDED:
            # Value is optional, return the default
            if isinstance(self.default, Reference):
                return self.default(settingsobj)
            else:
                return self.default
        else:
            # Coerce to the correct type and return it
            return self.type(value)


class BoundValue(object):
    def __init__(self, cls, name, value):
        self.cls = cls
        self.name = name
        self.value = value

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.value(obj, obj.config_provider, self.name)

    def __set__(self, obj, objtype=None):
        raise AttributeError("can't set attribute")

    def __repr__(self):  # NOCOV
        return 'BoundValue({}, {}) of class {}'.format(
            self.name, self.value.type, self.cls.__name__)


class Reference(object):
    def __init__(self, key):
        self.key = key

    def __call__(self, obj):
        return getattr(obj, self.key)

ref = Reference


def bind_values(cls, clsdict):
    for k, v in clsdict.items():
        if isinstance(v, Value):
            setattr(cls, k, BoundValue(cls, k, v))


class SettingsMeta(type):
    def __init__(cls, name, bases, clsdict):
        for base in bases:
            if not isinstance(base, cls.__class__):
                bind_values(cls, base.__dict__)
        bind_values(cls, clsdict)
        return super(SettingsMeta, cls).__init__(name, bases, clsdict)


class SettingsBase(object):
    def __init__(self, config_provider):
        self.config_provider = config_provider

    def __iter__(self):
        for k in dir(self):
            v = getattr(self.__class__, k, None)
            if isinstance(v, BoundValue):
                yield k, v

    def items(self):
        for k, v in self:
            yield k, getattr(self, k)

    def keys(self):
        for k, v in self:
            yield k

    def as_dict(self):
        return dict(self.items())


class Settings(with_metaclass(SettingsMeta, SettingsBase)):
    pass
