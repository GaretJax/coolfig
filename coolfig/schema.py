from six import with_metaclass, iteritems

from .providers import NOT_PROVIDED


class ImproperlyConfigured(Exception):
    """
    Raised when e request for a configuration value cannot be fulfilled.
    """


class ValueBase(object):
    def __call__(self, settingsobj, key):
        raise NotImplementedError


class Value(ValueBase):
    def __init__(self, type, default=NOT_PROVIDED, key=None):
        self.type = type
        self.default = default
        self.key = key

    def _get_provided_value(self, settingsobj, key):
        return settingsobj.config_provider.get(key)

    def __call__(self, settingsobj, key):
        key = self.key if self.key else key
        value = self._get_provided_value(settingsobj, key)
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


class Secret(Value):
    def __init__(self, type, default=NOT_PROVIDED, key=None, fallback=False):
        super(Secret, self).__init__(type, default, key)
        self.fallback = fallback

    def _get_provided_value(self, settingsobj, key):
        value = NOT_PROVIDED
        if settingsobj.secrets_provider:
            value = settingsobj.secrets_provider.get(key)
        if value is NOT_PROVIDED and self.fallback:
            value = super(Secret, self)._get_provided_value(settingsobj, key)
        return value


class ComputedValue(ValueBase):
    def __init__(self, callable, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def __call__(self, settingsobj, key):
        return self.callable(settingsobj, *self.args, **self.kwargs)


def computed_value(func):
    return ComputedValue(func)


class DictValue(Value):
    def __init__(self, type, keytype=str, *args, **kwargs):
        super(DictValue, self).__init__(type, *args, **kwargs)
        self.keytype = keytype

    def __call__(self, settingsobj, key):
        key = (self.key if self.key else key) + '_'
        return {self.keytype(k[len(key):]): self.type(v)
                for k, v in settingsobj.config_provider.iterprefixed(key)}


class DictSecret(DictValue):
    def __init__(self, type, keytype=str, fallback=False, *args, **kwargs):
        super(DictSecret, self).__init__(type, keytype, *args, **kwargs)
        self.fallback = fallback

    def __call__(self, settingsobj, key):
        key = (self.key if self.key else key) + '_'
        data = {}
        for k, v in settingsobj.secrets_provider.iterprefixed(key):
            data[self.keytype(k[len(key):])] = self.type(v)
        if self.fallback and not data:
            for k, v in settingsobj.config_provider.iterprefixed(key):
                postfix = self.keytype((k[len(key):]))
                if postfix not in data.keys():
                    data[postfix] = self.type(v)
        return data


class Dictionary(ValueBase):
    def __init__(self, spec):
        self.spec = spec

    def __call__(self, settingsobj, key):
        return {
            key: value(settingsobj, key)
            for key, value in iteritems(self.spec)
        }


class BoundValue(object):
    def __init__(self, cls, name, value):
        self.cls = cls
        self.name = name
        self.value = value

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.value(obj, self.name)

    def __set__(self, obj, objtype=None):
        raise AttributeError("can't set attribute")

    def __repr__(self):  # NOCOV
        return 'BoundValue({}, {}) of class {}'.format(
            self.name, self.value.type, self.cls.__name__)


class StaticValue(BoundValue):
    def __init__(self, value):
        self.value = value

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return self.value

    def __repr__(self):  # NOCOV
        return 'StaticValue({!r})'.format(self.value)


class Reference(object):
    def __init__(self, key):
        self.key = key

    def __call__(self, obj):
        return getattr(obj, self.key)


ref = Reference  # NOQA


def bind_values(cls, clsdict):
    for k, v in clsdict.items():
        if isinstance(v, ValueBase):
            setattr(cls, k, BoundValue(cls, k, v))


class SettingsMeta(type):
    def __init__(cls, name, bases, clsdict):
        for base in bases:
            if not isinstance(base, cls.__class__):
                bind_values(cls, base.__dict__)
        bind_values(cls, clsdict)
        return super(SettingsMeta, cls).__init__(name, bases, clsdict)

    def __iter__(self):
        for k in dir(self):
            v = getattr(self, k, None)
            if isinstance(v, BoundValue):
                yield k, v


class SettingsBase(object):
    def __init__(self, config_provider, secrets_provider=None):
        self.config_provider = config_provider
        self.secrets_provider = secrets_provider

    def __iter__(self):
        return iter(self.__class__)

    def items(self):
        for k, v in self:
            yield k, getattr(self, k)

    def keys(self):
        for k, v in self:
            yield k

    def as_dict(self):
        return dict(self.items())


class Settings(with_metaclass(SettingsMeta, SettingsBase)):
    @classmethod
    def merge(cls, *others):
        """
        Merge the `others` schema into this instance.

        The values will all be read from the provider of the original object.
        """
        for other in others:
            for k, v in other:
                setattr(cls, k, BoundValue(cls, k, v.value))
