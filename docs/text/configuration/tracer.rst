Tracer transport
================

``diffusion``
-------------

**Type:** positive number. **Units:** m²/s. Tracer diffusion coefficient.

``tracerTime``
--------------

**Type:** positive number. **Units:** seconds. End time for tracer transport.

``tracerWrite``
---------------

**Type:** positive number. **Units:** seconds. Interval between written tracer
results.

``tracerStep``
--------------

**Type:** positive number. **Units:** seconds. Numerical time step for tracer
transport.

Tracer simulation requires an existing ``OpenFOAM/flowStokes`` case. Run
``-t all``, ``-t flow_tracer``, or first create the flow result before using
``-t tracer``.
