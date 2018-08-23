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
from .django import load_django_settings
from .providers import DictConfig, EnvConfig, EnvDirConfig
from .schema import Dictionary, Settings, Value, computed_value


__version__ = "3.1.0"
__url__ = "https://github.com/GaretJax/coolfig"
__all__ = [
    "computed_value",
    "DictConfig",
    "Dictionary",
    "EnvConfig",
    "EnvDirConfig",
    "load_django_settings",
    "Settings",
    "Value",
]
