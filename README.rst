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

Define your schema:

.. code:: python

   from coolfig import Settings, Value, types

   class DefaultSettings(Settings):
        SECRET_KEY = Value(str)
        DEBUG = Value(types.boolean, default=False)
        DB_URL = Value(types.sqlalchemy_url)
        LOCALES = Value(types.list(str))

Instantiate the configuration with a data provider:

.. code:: python

   from coolfig import EnvConfig

   settings = DefaultSettings(EnvConfig(prefix='MYAPP_'))

Profit:

.. code:: python

   if settings.DEBUG:
       print(settings.SECRET_KEY)
   else:
       print(settings.LOCALES)

   connect(settings.DB_URL)


Django integration
==================

In your ``settings.py`` file:

.. code:: python

   from coolfig import EnvConfig, load_django_settings

   INSTALLED_APPS = (
      'django.contrib.admin',
      'django.contrib.auth',
      'django.contrib.contenttypes',
      'django.contrib.sessions',
      'django.contrib.messages',
      'django.contrib.staticfiles',

      'testprj.my_custom_app',
   )

   MIDDLEWARE_CLASSES = (
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.common.CommonMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
      'django.contrib.messages.middleware.MessageMiddleware',
      'django.middleware.clickjacking.XFrameOptionsMiddleware',
      'django.middleware.security.SecurityMiddleware',
   )

   ROOT_URLCONF = 'testprj.urls'

   WSGI_APPLICATION = 'testprj.wsgi.application'

   TEMPLATES = [
      {
         'BACKEND': 'django.template.backends.django.DjangoTemplates',
         'DIRS': [],
         'APP_DIRS': True,
         'OPTIONS': {
               'context_processors': [
                  'django.template.context_processors.debug',
                  'django.template.context_processors.request',
                  'django.contrib.auth.context_processors.auth',
                  'django.contrib.messages.context_processors.messages',
               ],
         },
      },
   ]

   load_django_settings(EnvConfig(), locals())

Then, in each ``settings`` submodule of each app, you can define additional
setting entries to be added to the main settings object. For example, in 
``testprj/my_custom_app/settings.py`` you can add the following:

.. code:: python

   from coolfig import Settings, Value

   class AppSettings(Settings):  # The class has to be named AppSettings
      MY_APP_SETTING = Value(str)

Usage is 100% compatible with Django's settings machinery:

.. code:: python

   from django.conf import settings

   settings.MY_APP_SETTING
