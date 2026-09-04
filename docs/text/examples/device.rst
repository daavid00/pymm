Device domain
=============

Overview
--------
This case uses the same image and configuration as :doc:`image`, but adds the
implemented device geometry. Flow enters at the top-left and exits at the
bottom-right for the provided configuration.

Command
-------

.. code-block:: console

   pymm -i microsystem.png -p parameters.toml -t all -m device

The reported execution time was approximately 35 minutes.

Results
-------

.. figure:: ../figs/device_pressure.png
   :alt: Pressure field for the device-domain example

.. figure:: ../figs/device_velocity.png
   :alt: Velocity field for the device-domain example

.. figure:: ../figs/device_tracer.png
   :alt: Tracer concentration for the device-domain example

   Pressure, velocity, and tracer concentration.

Reproduce
---------

.. code-block:: console

   . ./tests/scripts/docs_device.sh

`View script <https://github.com/cssr-tools/pymm/blob/main/tests/scripts/docs_device.sh>`__
| `View raw script <https://raw.githubusercontent.com/cssr-tools/pymm/main/tests/scripts/docs_device.sh>`__

.. button-ref:: ../examples
   :color: primary

   Back to examples gallery
