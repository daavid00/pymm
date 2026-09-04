3. Run tracer transport
=======================

Goal
----
Compute transient tracer transport from the previously generated flow field.

Configuration
-------------
The tracer stage uses ``diffusion``, ``tracerTime``, ``tracerWrite``, and
``tracerStep``.

Command
-------

.. code-block:: console

   pymm -p parameters.toml -t tracer

How it works
------------
pymm copies the latest flow fields and mesh, executes ``topoSet`` and
``foamRun``, then converts the result with ``foamToVTK``.

Result
------
Results are written below ``OpenFOAM/tracerTransport`` and
``VTK_tracerTransport``.

Next
----
Continue with :doc:`inspect-results`.
