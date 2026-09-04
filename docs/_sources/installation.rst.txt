Installation
============

The documented Linux setup uses ``apt-get``. Conda, Miniforge, and Mamba may
work, but are not currently tested. pymm supports Python 3.12 through 3.14.

Python package
--------------

Install the development version directly:

.. code-block:: console

   pip install git+https://github.com/cssr-tools/pymm.git

Source installation
-------------------

.. code-block:: console

   # Clone the repository
   git clone https://github.com/cssr-tools/pymm.git

   # Enter the repository
   cd pymm

   # Optional: select a release, or skip this step to use the development version
   git checkout v2026.04

   # Create a virtual environment
   # To select a Python executable, use for example: python3.13 -m venv pymm
   python3 -m venv vpymm

   # Activate the virtual environment
   source vpymm/bin/activate

   # Upgrade the packaging tools
   pip install --upgrade pip setuptools wheel

   # Install pymm in editable mode
   pip install -e .

   # Optional: install requirements for contributions, testing, and linting
   pip install -r dev-requirements.txt

Install development tools when contributing:

.. code-block:: console

   pip install -r dev-requirements.txt

.. tip::

   Run ``git tag -l`` to list available releases.

OpenFOAM
--------

The project documentation and CI use OpenFOAM 14. OpenFOAM has been available
through Ubuntu packages since version 12. Follow the `OpenFOAM 14 Ubuntu guide
<https://openfoam.org/download/14-ubuntu/>`_, then load and verify it:

.. code-block:: console

   source /opt/openfoam14/etc/bashrc
   foamRun -help
   gmshToFoam -help
   topoSet -help

The flow and tracer workflows require the OpenFOAM commands to be available in
``PATH``. Image processing and mesh generation do not run these utilities.

Gmsh
----

Install Gmsh from its `download page <https://gmsh.info/#Download>`_ or your
system package manager. Verify the executable with:

.. code-block:: console

   gmsh -version

Use ``--gmsh`` when the executable is not named ``gmsh`` or is outside ``PATH``:

.. code-block:: console

   pymm -g /full/path/to/gmsh -t mesh

Verification
------------

.. code-block:: console

   pymm --help
   gmsh -version
   foamRun -help

The project CI workflow demonstrates installation of pymm, Gmsh, and OpenFOAM
14 on Ubuntu 26.04 with Python 3.14.

Next steps
----------

Continue with :doc:`tutorial` or review the complete
:doc:`configuration_file`.
