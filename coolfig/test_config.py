import os
import math
import pytest

try:
    from sqlalchemy.engine import url
except ImportError:
    url = None

from .providers import ConfigurationProvider, DictConfig
from .providers import NOT_PROVIDED
from .schema import BoundValue, ref, DictValue
from .schema import ImproperlyConfigured
from . import types, Value, Settings


def test_lazy_callable():
    func = types.LazyCallable('not.existing.module', 'func')
    with pytest.raises(NotImplementedError):
        func()

    func = types.LazyCallable('string', 'non.existing.func')
    with pytest.raises(NotImplementedError):
        func()

    func = types.LazyCallable('math', 'ceil')
    assert func.func is math.ceil
    assert func(4.4) == 5


def test_config_abc():
    conf = ConfigurationProvider()

    with pytest.raises(NotImplementedError):
        conf.get('key')

    with pytest.raises(NotImplementedError):
        conf.iterprefixed('prefix')


def test_dict_get_config():
    conf = DictConfig({
        'TEST_KEY': 1,
    }, prefix='TEST_')

    assert conf.get('KEY') == 1
    assert conf.get('NOKEY') is NOT_PROVIDED


def test_dict_iter_config():
    conf = DictConfig({
        'TEST_KEY_1': 1,
        'TEST_KEY_2': 2,
        'TEST_FOO_3': 3,
        'TEST_KEX_1': 1,
        'TEST_KEY_3': 3,
        'TEST_BAR_1': 1,
    }, prefix='TEST_')

    items = conf.iterprefixed('KEY_')
    assert sorted(items) == [
        ('KEY_1', 1),
        ('KEY_2', 2),
        ('KEY_3', 3),
    ]


def test_simple():
    class SimpleSettings(Settings):
        INTKEY = Value(int)
        STRKEY = Value(str)
        NOKEY = Value(str)
        DEFKEY = Value(str, default='hello')

    assert isinstance(SimpleSettings.INTKEY, BoundValue)

    s = SimpleSettings(DictConfig({
        'INTKEY': '1',
        'STRKEY': 'string'
    }))
    assert s.INTKEY == 1
    assert s.STRKEY == 'string'
    assert s.DEFKEY == 'hello'

    with pytest.raises(ImproperlyConfigured):
        s.NOKEY


def test_dict_value():
    class DictSettings(Settings):
        DICTKEY = DictValue(str)

    assert isinstance(DictSettings.DICTKEY, BoundValue)
    s = DictSettings(DictConfig({
        'DICTKEY_KEY1': 1,
        'DICTKEY_KEY2': 2,
        'DICTKE_KEY3': 3,
    }))
    assert s.DICTKEY == {'KEY1': '1', 'KEY2': '2'}


def test_merge():
    class SimpleSettings(Settings):
        ORIGINAL_KEY = Value(int)

    class MergeSettings(Settings):
        MERGED_KEY = Value(int)

    s = SimpleSettings(DictConfig({
        'ORIGINAL_KEY': 1,
        'MERGED_KEY': 2,
    }))

    assert s.ORIGINAL_KEY == 1
    with pytest.raises(AttributeError):
        s.MERGED_KEY

    s.merge(MergeSettings)

    assert s.ORIGINAL_KEY == 1
    assert s.MERGED_KEY == 2


def test_readonly():
    class SimpleSettings(Settings):
        KEY = Value(int)

    s = SimpleSettings(DictConfig({
        'KEY': '1',
    }))
    assert s.KEY == 1

    with pytest.raises(AttributeError):
        s.KEY = 2

    assert s.KEY == 1


def test_reference():
    class RefSettings(Settings):
        KEY1 = Value(int)
        KEY2 = Value(int, default=ref('KEY1'))

    s = RefSettings(DictConfig({
        'KEY1': '1',
        'KEY2': '2',
    }))

    assert s.KEY1 == 1
    assert s.KEY2 == 2

    s = RefSettings(DictConfig({
        'KEY1': '1',
    }))

    assert s.KEY1 == 1
    assert s.KEY2 == 1


def test_mixin():
    class TestMixin:
        KEY = Value(int)

    class SimpleSettings(TestMixin, Settings):
        pass

    class SimpleSettingsOverride(TestMixin, Settings):
        KEY = Value(str)

    assert isinstance(SimpleSettings.KEY, BoundValue)
    assert isinstance(SimpleSettingsOverride.KEY, BoundValue)

    s = SimpleSettings(DictConfig({
        'KEY': '1'
    }))
    assert s.KEY == 1

    s = SimpleSettingsOverride(DictConfig({
        'KEY': 'string'
    }))
    assert s.KEY == 'string'


def test_iter():
    class SimpleSettings(Settings):
        KEY1 = Value(int)
        KEY2 = Value(int)
        KEY3 = Value(int)
        KEY4 = Value(int)
        KEY5 = Value(int)

    s = SimpleSettings(DictConfig({
        'KEY1': '10',
        'KEY2': '20',
        'KEY3': '30',
        'KEY4': '40',
        'KEY5': '50',
    }))

    assert list(s.keys()) == [
        'KEY1',
        'KEY2',
        'KEY3',
        'KEY4',
        'KEY5',
    ]
    assert list(s.items()) == [
        ('KEY1', 10),
        ('KEY2', 20),
        ('KEY3', 30),
        ('KEY4', 40),
        ('KEY5', 50),
    ]
    assert s.as_dict() == {
        'KEY1': 10,
        'KEY2': 20,
        'KEY3': 30,
        'KEY4': 40,
        'KEY5': 50,
    }


def test_boolean():
    assert types.boolean('y')
    assert types.boolean('yes')
    assert types.boolean('1')
    assert types.boolean('true')
    assert types.boolean('on')
    assert not types.boolean('n')
    assert not types.boolean('')
    assert not types.boolean('no')
    assert not types.boolean('false')
    assert not types.boolean('off')
    assert not types.boolean('0')


def test_list():
    int_list = types.list(int)
    str_list = types.list(str)
    assert int_list('1,2,3, 4, 5 ,6 ') == [1, 2, 3, 4, 5, 6]
    assert str_list('a,b,cd, e f g , h ') == ['a', 'b', 'cd', 'e f g', 'h']


def test_dottedpath():
    func = types.dottedpath('coolfig.test_config.test_dottedpath')
    assert func == test_dottedpath


@pytest.mark.skipif(url is None, reason='sqlalchemy is not installed')
def test_sqlalchemy_url():
    val = types.sqlalchemy_url('postgres://user:password@host/database')
    assert isinstance(val, url.URL)


@pytest.mark.skipif(url is not None, reason='sqlalchemy is installed')
def test_sqlalchemy_url_not_implemented():
    with pytest.raises(NotImplementedError):
        types.sqlalchemy_url('postgres://user:password@host/database')


# def test_validate():
#     class SimpleSettings(Settings):
#         KEY = Value(int)
#
#     s = SimpleSettings(DictConfig({}))
#     with pytest.raises(ImproperlyConfigured):
#         s.validate()
#
#     s = SimpleSettings(DictConfig({
#         'KEY': '1',
#     }))
#     s.validate()
#
#     s = SimpleSettings(DictConfig({
#         'KEY': 'string'
#     }))
#     with pytest.raises(ImproperlyConfigured):
#         s.validate()


def test_env_config():
    class DefaultSettings(Settings):
        SECRET_KEY = Value(str)
        DEBUG = Value(types.boolean, default=False)
        DB_URL = Value(types.sqlalchemy_url)
        LOCALES = Value(types.list(str))

    settings = DefaultSettings(DictConfig(os.environ, prefix='APP_'))

    assert settings.config_provider.__class__ == DictConfig
    assert settings.config_provider._conf_dict == os.environ
