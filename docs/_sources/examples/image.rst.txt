Image domain
============

Overview
--------
This example uses the microsystem from the :doc:`../configuration_file` page,
``microsystem.png``, and the default ``parameters.toml``. The image is available
in the repository ``examples`` folder.

Command
-------

.. code-block:: console

   pymm -i microsystem.png -p parameters.toml -t all

Because ``image`` is the default mode and ``gmsh`` is the default executable,
no additional flags are required. The reported execution time was approximately
20 minutes.

Results
-------

.. figure:: ../figs/pressure.png
   :alt: Pressure field for the image-domain example

.. figure:: ../figs/velocity.png
   :alt: Velocity field for the image-domain example

.. figure:: ../figs/tracer.png
   :alt: Tracer concentration for the image-domain example

   Pressure, velocity, and tracer concentration.

Reproduce
---------

.. code-block:: console

   . ./tests/scripts/docs_image.sh

`View script <https://github.com/cssr-tools/pymm/blob/main/tests/scripts/docs_image.sh>`__
| `View raw script <https://raw.githubusercontent.com/cssr-tools/pymm/main/tests/scripts/docs_image.sh>`__

.. button-ref:: ../examples
   :color: primary

   Back to examples gallery
