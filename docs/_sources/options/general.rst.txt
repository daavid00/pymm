General options
===============

.. program:: pymm

.. option:: -i <path>, --image <path>

   Input PNG image. Default: ``microsystem.png``. Required in ``image`` mode.

.. option:: -p <path>, --parameters <path>

   TOML parameter file. Default: ``parameters.toml``. The path must exist and
   use the ``.toml`` extension.

.. option:: -m <mode>, --mode <mode>

   Microsystem setup. Choices: ``image`` and ``device``. Default: ``image``.

.. option:: -t <workflow>, --type <workflow>

   Workflow to execute. Choices: ``pngs``, ``mesh``, ``flow``, ``mesh_flow``,
   ``flow_tracer``, ``tracer``, and ``all``. Default: ``mesh``.

.. option:: -o <path>, --output <path>

   Output directory. Default: ``output``. An existing path must be a directory.

.. option:: -g <command>, --gmsh <command>

   Gmsh executable or command. Default: ``gmsh``. It is checked only for mesh-
   generating workflows. Quoted commands are parsed with :mod:`shlex`.
