=======
History
=======

2.0.0 - 2018-08-03
==================

* Support for Docker secrets.


1.0.2 - 2016-03-14
==================

* Additional bug-fixing.


1.0.1 - 2016-03-14
==================

* Fixed a bug in AppConfig checking.


1.0.0 - 2016-03-14
==================

* Added support for Django ``AppConfig`` (including custom settings path
  configured with a ``settings`` property on the config class.
* Officially supporting Django 1.4, 1.5, 1.6, 1.7, 1.8 and 1.9, running on
  Python 2.7, 3.4 (where Django supports itself supports it) and PyPy.


0.4.0 - 2015-10-05
==================

* Added support for the CACHES Django settings directive
* Added support for computed_values
* Added initial documentation stub


0.3.0 - 2015-07-20
==================

* Added first-class support for Django
* Added some more importing shortcuts (``EnvConfig``, ``DictConfig``,
  ``load_django_settings``)
* Added a ``DictValue`` value, able to load multiple keys with the same prefix
  into the same value
* Added an API to merge different settings schema into an existing object


0.2.0 - 2015-05-31
==================

* Added a ``EnvConfig`` provider
* Added a ``dottedpath`` value type


0.1.0 – 2015-05-30
==================

* Initial release
