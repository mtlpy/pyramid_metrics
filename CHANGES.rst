Changelog
=========

0.2.0 (2014-08-19)
------------------

* Change API of MetricsUtility.timing to use second(float) rather than ms(int)
* Add a timer as a context-manager
* Add functional tests

0.1.5 (2014-05-30)
------------------

* Add get_current_metrics to get the metrics utility from the thread-local
  data if the current request object is not otherwise available (for example,
  in the context of a model method.)
* Raise an exception if get_current_metrics is called and no request is active

0.1.4 (2014-05-08)
------------------

* Fix exception when no context is attached to request object

0.1.3 (2014-05-07)
------------------

* Add HTTP method in route performance stat name
* Change API a bit to accept tuple/list as stat name/prefix/suffix
* Improve feature and API documentation

0.1.2 (2014-05-07)
------------------

* Generate useful stat name from request context (for Traversal)

0.1.1 (2014-05-06)
------------------

* Fix incorrect maybe_dotted relative path usage in tween


0.1.0 (2014-05-06)
------------------

* Initial utility
* Global route performance collection
* Implement simple time markers and counter
* Implement metrics per_route option
* Release on PyPI
