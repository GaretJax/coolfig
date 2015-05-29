=======
COOLFIG
=======

.. image:: https://img.shields.io/travis/GaretJax/coolfig.svg
   :target: https://travis-ci.org/GaretJax/coolfig

.. image:: https://img.shields.io/pypi/v/coolfig.svg
   :target: https://pypi.python.org/pypi/coolfig

.. image:: https://img.shields.io/pypi/dm/coolfig.svg
   :target: https://pypi.python.org/pypi/coolfig

.. image:: https://img.shields.io/coveralls/GaretJax/coolfig/master.svg
   :target: https://coveralls.io/r/GaretJax/coolfig?branch=master

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg
   :target: http://coolfig.readthedocs.org/en/latest/

.. image:: https://img.shields.io/pypi/l/coolfig.svg
   :target: https://github.com/GaretJax/coolfig/blob/develop/LICENSE

.. image:: https://img.shields.io/requires/github/GaretJax/coolfig.svg
   :target: https://requires.io/github/GaretJax/coolfig/requirements/?branch=master

.. .. image:: https://img.shields.io/codeclimate/github/GaretJax/coolfig.svg
..   :target: https://codeclimate.com/github/GaretJax/coolfig

Coolfig is a library to easily write configuration specifications to be
fulfilled by various sources.

* Free software: MIT license
* Documentation: http://coolfig.rtfd.org


Installation
============

::

  pip install coolfig


Example
=======

Define your schema::

   from coolfig import Settings, Value, types

   class DefaultSettings(Settings):
        SECRET_KEY = Value(str)
        DEBUG = Value(types.boolean, default=False)
        DB_URL = Value(types.sqlalchemy_url)
        LOCALES = Value(types.list(str))

Instantiate the configuration with a data provider::

   import os
   from coolfig import providers

   settings = DefaultSettings(
       providers.DictConfig(os.environ, prefix='MYAPP_'))

Profit::

   if settings.DEBUG:
       print(settings.SECRET_KEY)
   else:
       print(settings.LOCALES)

   connect(settings.DB_URL)

