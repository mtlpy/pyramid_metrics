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
   :linenos:

   [app:myapp]
   metrics.host = localhost
   metrics.port = 8125

   metrics.prefix = application.stage

   metrics.route_performance = true


Currently implemented
=====================

- Collection utility as a request method
- Ability to send metrics per Pyramid route
- Simple time marker mechanism
- Simple counter


TODO
====

- Full StatsD metric types
- Extensions for automatic metrology (SQLAlchemy, MongoDB, Requests...)
- Whitelist/blacklist of metrics
- Time allocation per subsystem (using the time marker mechanism)


Considerations
==============

- The general error policy is: always failsafe. Pyramid_metrics should NEVER
  break your application.
- The DNS resolution is done during configuration to avoid recurring latencies.
