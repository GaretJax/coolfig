from __future__ import absolute_import

import sys
import os

import six

from . import types
from .schema import Settings, Value, DictValue, StaticValue


class BaseDjangoSettings(Settings):
    SECRET_KEY = Value(str)
    DEBUG = Value(types.boolean, default=False)
    ALLOWED_HOSTS = Value(types.list(str), default=tuple())

    DATABASES = DictValue(types.django_db_url, str.lower)
    CACHES = DictValue(types.django_cache_url, str.lower)

    # Internationalization
    # https://docs.djangoproject.com/en/1.8/topics/i18n/
    LANGUAGE_CODE = Value(str, default='en-us')
    TIME_ZONE = Value(str, default='UTC')
    USE_I18N = Value(types.boolean, default=True)
    USE_L10N = Value(types.boolean, default=True)
    USE_TZ = Value(types.boolean, default=True)

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.8/howto/static-files/
    STATIC_URL = Value(str, default='/static/')

    def install(self, name=None):
        if not name:
            name = os.environ['DJANGO_SETTINGS_MODULE']
        try:
            self.__file__ = sys.modules[name].__file__
        except (KeyError, AttributeError):
            pass
        sys.modules[name] = self

    def load_apps(self, apps=None):
        if apps is None:
            apps = getattr(self, 'INSTALLED_APPS', [])

        for app_path in apps:
            settings_path = app_path + '.settings.AppSettings'
            try:
                app_settings = types.dottedpath(settings_path)
            except (ImportError, AttributeError):
                pass
            else:
                self.merge(app_settings)


def make_django_settings(static_config, base=BaseDjangoSettings):
    static_config = {k: StaticValue(v)
                     for k, v in six.iteritems(static_config)
                     if k.upper() == k}
    return type('DjangoSettings', (base,), static_config)


def load_django_settings(provider, static_config, base=BaseDjangoSettings,
                         apps=None, name=None):
    settings_class = make_django_settings(static_config, base)
    settings = settings_class(provider)
    settings.install(name)
    settings.load_apps(apps)
