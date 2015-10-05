"""
Support for working with different sources of configuration values.

    class DefaultSettings(schema.Settings):
        SECRET_KEY = schema.Value(str)
        DEBUG = schema.Value(types.boolean, default=False)
        DB_URL = schema.Value(types.sqlalchemy_url)
        LOCALES = schema.Value(types.list(str))

    settings = DefaultSettings(
        providers.DictConfig(os.environ, prefix='MYAPP_'))
"""
from .schema import Value, Settings, computed_value, Dictionary
from .providers import EnvConfig, DictConfig
from .django import load_django_settings


__version__ = '0.4.0'
__url__ = 'https://github.com/GaretJax/coolfig'
__all__ = ['Value', 'Dictionary', 'computed_value', 'Settings',
           'EnvConfig', 'DictConfig', 'load_django_settings']
