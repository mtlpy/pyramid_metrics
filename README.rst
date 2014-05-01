===============
Pyramid_metrics
===============

Performance metrics for Pyramid using StatsD. The project aims at providing
ways to instrument a Pyramid application in a least intrusive way.


Usage
=====

Pyramid_metrics configuration (values are defaults)::

   pyramid.includes = pyramid_metrics

   metrics.host = 127.0.0.1
   metrics.port = 8125

   metrics.prefix = "application.stage"

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
