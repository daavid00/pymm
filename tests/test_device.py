# SPDX-FileCopyrightText: 2022-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Test the device mode functionality"""

import subprocess
from pathlib import Path


def test_device(tmp_path, monkeypatch):
    """See configs/whiteish_grains.toml"""
    repo_root = Path(__file__).parents[1]
    monkeypatch.chdir(tmp_path)
    subprocess.run(
        [
            "pymm",
            "-i",
            f"{repo_root}/tests/configs/whiteish_grains.png",
            "-p",
            f"{repo_root}/tests//configs/whiteish_grains.toml",
            "-g",
            "gmsh",
            "-t",
            "mesh",
            "-m",
            "device",
            "-o",
            ".",
        ],
        check=True,
    )
    mesh = tmp_path / "mesh.msh"
    assert (mesh).is_file()

    with open(mesh, "r", encoding="utf8") as f:
        lines = f.readlines()

    num_nodes = int(lines[lines.index("$Nodes\n") + 1])
    num_lines = len(lines)
    num_elements = int(lines[lines.index("$Elements\n") + 1])

    assert num_lines > 2220000
    assert num_nodes > 500000
    assert num_elements > 1600000
    subprocess.run(
        [
            "pymm",
            "-i",
            f"{repo_root}/tests/configs/whiteish_grains.png",
            "-p",
            f"{repo_root}/tests//configs/whiteish_grains.toml",
            "-g",
            "gmsh",
            "-t",
            "flow_tracer",
            "-m",
            "device",
            "-o",
            ".",
        ],
        check=True,
    )
    last_vtk = tmp_path / "VTK_tracerTransport" / "tracerTransport_5.vtk"
    assert last_vtk.is_file()
    assert last_vtk.stat().st_size > 0
