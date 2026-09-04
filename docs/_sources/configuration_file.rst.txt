Configuration reference
=======================

pymm reads a top-level TOML file. The following reference preserves the units,
accepted values, validation rules, and physical meaning used by the current
implementation.

Microsystem used in the examples
--------------------------------

The image below can be extracted from Fig. 52 in `Benali (2019)
<https://hdl.handle.net/1956/21300>`_ and Fig. 1c in `Liu et al. (2023)
<https://doi.org/10.1016/j.ijggc.2023.103885>`_.

.. figure:: figs/microsystem.png
   :alt: Grains and pore space in the example microsystem

   Grains and pore-space configuration.

The two-dimensional image has 805 × 252 pixels. Its physical dimensions are
``6.74e-3 × 2.5e-3 × 0.03e-3 m``. The pattern used in the cited numerical
simulations has a substantially higher resolution.

.. toctree::
   :maxdepth: 1

   configuration/image
   configuration/geometry
   configuration/flow
   configuration/tracer
   configuration/complete
