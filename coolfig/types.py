"""
Common types for settings classes.
"""

try:
    from sqlalchemy.engine.url import make_url as make_sqlalchemy_url
except ImportError:
    make_sqlalchemy_url = None


def boolean(string):
    return string.lower() in set(['1', 'true', 'yes', 'on', 'y'])


def sqlalchemy_url(string):
    if not make_sqlalchemy_url:
        raise NotImplementedError()
    return make_sqlalchemy_url(string)


def list(inner_type):
    def convert(string):
        return [inner_type(s.strip()) for s in string.split(',')]
    return convert
