from __future__ import absolute_import

import os
import types
import sys
import contextlib
import pytest

try:
    import environ as url
except ImportError:
    url = None

from .django import BaseDjangoSettings, make_django_settings
from .django import load_django_settings
from .providers import DictConfig
from .types import django_db_url
from . import Value, Settings


@contextlib.contextmanager
def unset_key(dictionary, key):
    key_is_set = key in dictionary
    value = dictionary.pop(key, None)

    try:
        yield
    finally:
        if key_is_set:
            dictionary[key] = value
        elif key in dictionary:
            del dictionary[key]


@contextlib.contextmanager
def set_key(dictionary, key, value):
    key_is_set = key in dictionary
    original_value = dictionary.pop(key, None)

    dictionary[key] = value

    try:
        yield
    finally:
        if key_is_set:
            dictionary[key] = original_value
        else:
            del dictionary[key]


def install_app_settings(app_path, settings_cls):
    def iter_ancestors(path, sep='.'):
        position = 0
        try:
            while True:
                position = app_path.index(sep, position + 1)
                yield app_path[:position]
        except ValueError:
            pass
        yield path

    for path in iter_ancestors(app_path):
        sys.modules[path] = types.ModuleType(path)

    settings_module = types.ModuleType(app_path + '.settins')
    settings_module.AppSettings = settings_cls
    sys.modules[app_path + '.settings'] = settings_module


def test_install():
    s = BaseDjangoSettings(DictConfig({}))

    with unset_key(os.environ, 'DJANGO_SETTINGS_MODULE'):
        with pytest.raises(KeyError):
            s.install()

    with set_key(os.environ, 'DJANGO_SETTINGS_MODULE', 'my_test_settings'):
        s.install()
        import my_test_settings
        assert my_test_settings is s

    s.install(name='my_other_test_settings')
    import my_other_test_settings
    assert my_other_test_settings is s

    # And let's overwrite it
    s2 = BaseDjangoSettings(DictConfig({}))
    s2.install(name='my_other_test_settings')
    import my_other_test_settings
    assert my_other_test_settings is s2


def test_iter():
    settings_class = make_django_settings({
        'INSTALLED_APPS': [],
        'ROOT_URLCONF': 'test.urls',
    })

    s = settings_class(DictConfig({
        'SECRET_KEY': 'test-secret-key'
    }))
    confdict = s.as_dict()
    assert confdict['INSTALLED_APPS'] == []
    assert confdict['ROOT_URLCONF'] == 'test.urls'


def test_load_apps():
    settings_class = make_django_settings({
        'INSTALLED_APPS': []
    })
    s = settings_class(DictConfig({
        'APP_KEY': 'app_val'
    }))

    # Load empty apps
    s.load_apps()
    s.load_apps([])

    class AppSettings(Settings):
        APP_KEY = Value(str)

    with pytest.raises(AttributeError):
        s.APP_KEY

    install_app_settings('my_test_app.module.submodule', AppSettings)
    s.load_apps([
        'my_non_test_app',  # Does not exist
        'my_test_app.module.submodule',
    ])

    assert s.APP_KEY == 'app_val'


def test_load_settings():
    class AppSettings(Settings):
        APP_KEY = Value(str)

    install_app_settings('my_loaded_app', AppSettings)

    provider = DictConfig({
        'APP_KEY': 'app_val',
    })
    static_config = {
        'INSTALLED_APPS': [
            'my_loaded_app',
        ],
        'ROOT_URLCONF': 'test.app.urls',
    }
    load_django_settings(provider, static_config, name='test_settings')

    import test_settings
    assert test_settings.INSTALLED_APPS == ['my_loaded_app']
    assert test_settings.ROOT_URLCONF == 'test.app.urls'
    assert test_settings.APP_KEY == 'app_val'


@pytest.mark.skipif(url is None, reason='django-environ is not installed')
def test_db_url():
    val = django_db_url('postgres://user:password@host/database')
    assert isinstance(val, dict)


@pytest.mark.skipif(url is not None, reason='django-environ is installed')
def test_db_url_not_implemented():
    with pytest.raises(NotImplementedError):
        django_db_url('postgres://user:password@host/database')
