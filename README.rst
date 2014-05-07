===============
Pyramid_metrics
===============

Performance metrics for Pyramid using StatsD. The project aims at providing
ways to instrument a Pyramid application in the least intrusive way.

* PyPI: https://pypi.python.org/pypi/pyramid_metrics
* Bitbucket: https://bitbucket.org/Ludia/pyramid_metrics
* |droneio|

.. |droneio| image::
   https://drone.io/bitbucket.org/Ludia/pyramid_metrics/status.png
   :target: https://drone.io/bitbucket.org/Ludia/pyramid_metrics
   :alt: Tests on drone.io


Installation
============

Install using setuptools, e.g. (within a virtualenv)::

  $ pip install pyramid_metrics


Setup
=====

Once ``pyramid_metrics`` is installed, you must use the ``config.include``
mechanism to include it into your Pyramid project's configuration.  In your
Pyramid project's ``__init__.py``:

.. code-block:: python

   config = Configurator(.....)
   config.include('pyramid_metrics')

Alternately you can use the ``pyramid.includes`` configuration value in your
``.ini`` file:

.. code-block:: ini

   [app:myapp]
   pyramid.includes = pyramid_metrics


Usage
=====

Pyramid_metrics configuration (values are defaults):

.. code-block:: ini

   [app:myapp]
   metrics.host = localhost
   metrics.port = 8125

   metrics.prefix = application.stage

   metrics.route_performance = true


Route performance
=================

If enabled, the route performance feature will time the request processing.
By using the StatsD Timer type metric, pre-aggregation will provide information
on latency, rate and total number. The information is sent two times: per route
and globally.

The key name is composed of the route name,
the HTTP method and the outcome (as HTTP status code or 'exc' for exception).

- Global key ``request.<HTTP_METHOD>.<STATUS_CODE_OR_EXC>``
- Per route key ``route.<ROUTE_NAME>.request.<HTTP_METHOD>.<STATUS_CODE_OR_EXC>``


API
===

Counter
-------

StatsD type:
https://github.com/etsy/statsd/blob/master/docs/metric_types.md#counting

.. code-block:: python

   # Increment a counter named cache.hit by 1
   request.metrics.incr('cache.hit')

   # Increment by N
   request.metrics.incr(('cache.hit.read.total', count=len(cacheresult)))

   # Stat names can be composed from list or tuple
   request.metrics.incr(('cache', cache_action))


Timer
-----

StatsD type:
https://github.com/etsy/statsd/blob/master/docs/metric_types.md#timing

.. code-block:: python

   # Simple timing
   time_in_ms = requests.get('http://example.net').elapsed.microseconds/1000
   request.metrics.timing('net.example.responsetime', time_in_ms)

   # Using the time marker mechanism
   request.metrics.marker_start('something_slow')
   httpclient.get('http://example.net')
   request.metrics.marker_stop('something_slow')

   # Measure different outcome
   request.metrics.marker_start('something_slow')
   try:
       httpclient.get('http://example.net').raise_for_status()
   except:
       # Send measure to key 'something_slow.error'
       request.metrics.marker_stop('something_slow', suffix='error')
   else:
       # Send measure to key 'something_slow.ok'
       request.metrics.marker_stop('something_slow', suffix='ok')


Currently implemented
=====================

- Collection utility as a request method
- Ability to send metrics per Pyramid route
- Simple time marker mechanism
- Simple counter


TODO
====

- Context manager for Timing metric type
- Full StatsD metric types
- Extensions for automatic metrology (SQLAlchemy, MongoDB, Requests...)
- Whitelist/blacklist of metrics
- Time allocation per subsystem (using the time marker mechanism)


Considerations
==============

- The general error policy is: always failsafe. Pyramid_metrics should NEVER
  break your application.
- The DNS resolution is done during configuration to avoid recurring latencies.
