# SPDX-FileCopyrightText: 2022-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0902,R0912,R0913,R0914,R0915,R0917,E1102,E1123,C0103,C0302

"""Command-line entry point and top-level workflow coordination for pymm.

pymm supports four connected workflows for microsystem models:

* Image processing segments grains, voids, and the external boundary.
* Mesh generation creates Gmsh geometry and mesh files.
* Flow simulation runs a steady incompressible OpenFOAM model.
* Tracer simulation runs transient transport using the computed flow field.

This module parses and validates command-line arguments and TOML parameters,
processes images, extracts and tags boundaries, writes mesh input, dispatches the
selected simulations, and reports generated files. It also provides the shared
terminal helpers used for errors, progress messages, and successful results."""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tomllib
from contextlib import nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import skimage.transform
from alive_progress import alive_bar
from mako.template import Template
from matplotlib.collections import LineCollection
from numpy.typing import NDArray
from skimage import io, measure
from skimage.morphology import remove_small_objects

ADD_BORDER = 50  # Add arbitrary border to extract the image boundaries
ANSI_BOLD_RED = "1;31"
ANSI_BOLD_YELLOW = "1;33"
ANSI_BOLD_GREEN = "1;32"
ANSI_BOLD_BLUE = "1;34"
ANSI_BOLD_MAGENTA = "1;35"
ANSI_YELLOW = "1;33"
ANSI_GREEN = "1;32"
ANSI_CYAN = "36"
ANSI_RED = "31"
ANSI_BLUE = "1;34"


@dataclass(slots=True, frozen=True)
class PymmConfig:
    """Store the shared pymm configuration loaded from TOML.

    The top-level TOML values populate this frozen data class. The configuration is
    validated by :func:`check_toml` and then shared by the image, mesh, flow, and
    tracer workflows.

    Attributes
    ----------
    length : float
        Physical length used to scale the Gmsh geometry.
    width : float
        Physical width used to scale the Gmsh geometry.
    thickness : float
        Extrusion thickness used by the Gmsh template.
    grainMeaning : int
        Grain convention: ``0`` for light grains or ``1`` for dark grains.
    threshold : float
        Grayscale segmentation threshold in the closed interval ``[0, 1]``.
    rescale : float
        Positive image rescaling factor.
    grainsSize : int
        Maximum size, in pixels, of small grain objects to remove.
    borderTol : float
        Polygon-approximation tolerance for the external boundary.
    grainsTol : float
        Polygon-approximation tolerance for interior grains.
    lineWidth : float
        Line width used in the diagnostic figures.
    channelWidth : float
        Channel width passed to the Gmsh template.
    meshSize : float
        Target mesh size passed to the Gmsh template.
    viscosity : float
        Viscosity written to the OpenFOAM physical properties.
    diffusion : float
        Tracer diffusion value written to the OpenFOAM case.
    inletLocation : str
        Inlet side: ``left``, ``top``, ``right``, or ``bottom``.
    inletValue : float
        Inlet value written to the OpenFOAM pressure field.
    tracerTime : float
        End time for the tracer simulation.
    tracerWrite : float
        Output interval for the tracer simulation.
    pressureConv : float
        Pressure convergence tolerance for the flow solver.
    velocityConv : float
        Velocity convergence tolerance for the flow solver.
    iterationsMax : int
        Maximum number of steady-flow iterations.
    tracerStep : float
        Time step for the tracer simulation.

    Notes
    -----
    Physical units are defined by the Gmsh and OpenFOAM templates and must be
    consistent across the configuration."""

    length: float
    width: float
    thickness: float
    grainMeaning: int
    threshold: float
    rescale: float
    grainsSize: int
    borderTol: float
    grainsTol: float
    lineWidth: float
    channelWidth: float
    meshSize: float
    viscosity: float
    diffusion: float
    inletLocation: str
    inletValue: float
    tracerTime: float
    tracerWrite: float
    pressureConv: float
    velocityConv: float
    iterationsMax: int
    tracerStep: float


def main(argv: list[str] | None = None) -> None:
    """Run the pymm command-line workflow.

    Parse and validate CLI arguments and TOML parameters, then dispatch the selected
    image, mesh, flow, and tracer operations.

    Parameters
    ----------
    argv : list[str] | None, optional
        Arguments to parse instead of ``sys.argv[1:]``. This is primarily used by
        tests and programmatic callers.

    Raises
    ------
    SystemExit
        If command-line or TOML validation fails.
    tomllib.TOMLDecodeError
        If the parameter file is not valid TOML.
    subprocess.CalledProcessError
        If an external command fails."""
    cmdargs = parse_args(argv)
    check_cmdargs(cmdargs)
    pat = Path(__file__).resolve().parent.parent
    fol = Path(cmdargs.output).resolve()
    gmsh = cmdargs.gmsh
    mode = cmdargs.mode
    kind = cmdargs.type
    image_path = cmdargs.image
    parameters_path = Path(cmdargs.parameters)
    with open(parameters_path, "rb") as f:
        toml = tomllib.load(f)
    cfg = PymmConfig(**toml)
    check_toml(cfg)
    if kind in {"all", "pngs", "mesh", "mesh_flow"}:
        generated_files = [
            "binary_image.png",
            "extracted_border.png",
            "interior_grains_border.png",
            "interior_grains.png",
        ]
        pymm_info("Generating the files, please wait...")
        # Generate the image
        imH, imL, cn_grains, boundary = process_image(cfg, fol, mode, image_path)
        # Extract the coordinates of the image borders
        pl, pt, pr, pb, bb, bl, bt, br = extract_borders(boundary)
        if kind in {"all", "mesh", "mesh_flow"}:
            if cfg.inletLocation.lower() not in {"left", "top", "right", "bottom"}:
                pymm_error(
                    f"Invalid inletLocation {cli_error_value(cfg.inletLocation)}."
                )
            bdnL: list[int] = []
            bdnT: list[int] = []
            bdnR: list[int] = []
            bdnB: list[int] = []
            wall: list[int] = []
            if mode == "image":
                # Set the boundary tags
                points = np.vstack([pl, pt[1:], pr, pb])
                points = np.vstack([points, points[0]])
                bdnL, bdnT, index = boundary_tags_left_top(points, pl, pt, bl, bt, wall)
                bdnR, bdnB = boundary_tags_right_bottom(
                    points, index, pr, pb, bb, br, wall
                )
            # Write the .geo file
            write_geo(
                cfg,
                fol,
                pat,
                mode,
                gmsh,
                imH,
                imL,
                cn_grains,
                pl,
                pt,
                pr,
                pb,
                bdnL,
                bdnT,
                bdnR,
                bdnB,
                wall,
            )
            generated_files += ["mesh.geo", "mesh.msh"]
        pymm_success("", str(fol), generated_files)
    if kind in {"all", "mesh_flow", "flow", "flow_tracer"}:
        # Set up of the files for the Flow simulations and run them
        pymm_info("Processing the flow simulations, please wait...")
        if not (fol / "mesh.msh").exists():
            pymm_error(
                f"Run first either {cli_correct_value('-t all')} or {cli_correct_value('-t mesh')}."
            )
        run_stokes(cfg, fol, pat)
        pymm_success(
            f"Results written to {fol}/OpenFOAM/flowStokes/ and\n               "
            f"{fol}/VTK_flowSTokes/",
            "",
            [],
        )
    if kind in {"all", "flow_tracer", "tracer"}:
        pymm_info("Processing the tracer simulations, please wait...")
        if not (fol / "OpenFOAM" / "flowStokes").exists():
            pymm_error(
                f"Run first either {cli_correct_value('-t all')} or "
                f"{cli_correct_value('-t mesh_flow')}."
            )
        # Set up of the files for the Tracer simulations and run them
        run_tracer(cfg, fol, pat)
        pymm_success(
            f"Results written to {fol}/OpenFOAM/tracerTransport/ and\n               "
            f"{fol}/VTK_tracerTransport/",
            "",
            [],
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Create the CLI parser and parse pymm arguments.

    Parameters
    ----------
    argv : list[str] | None, optional
        Arguments to parse instead of ``sys.argv[1:]``.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Main script to run the workflow on a microsystem configuration.",
    )
    parser.add_argument(
        "-i",
        "--image",
        type=str.strip,
        default="microsystem.png",
        help="The base name of the image",
    )
    parser.add_argument(
        "-p",
        "--parameters",
        type=str.strip,
        default="parameters.toml",
        help="The base name of the parameter file",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str.strip,
        choices=["image", "device"],
        default="image",
        help="The setup configuration of the microsystem",
    )
    parser.add_argument(
        "-t",
        "--type",
        type=str.strip,
        choices=["pngs", "mesh", "flow", "mesh_flow", "flow_tracer", "tracer", "all"],
        default="mesh",
        help="Run the whole framework ('all'), only the generation of the PNG figures "
        "with the segmentation to grains, voids, and boundary ('pngs'), the mesh files "
        "for Gmsh ('mesh'), keep the current mesh and only simulate the flow velocity "
        "field ('flow'), mesh and flow ('mesh_flow'), flow and tracer ('flow_tracer'), "
        "or only tracer simulations ('tracer')",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str.strip,
        default="output",
        help="The base name of the output folder",
    )
    parser.add_argument(
        "-g",
        "--gmsh",
        type=str.strip,
        default="gmsh",
        help="The full path to the gmsh executable or simple Gmsh if it runs from the "
        "terminal",
    )
    return parser.parse_args(argv)


def check_cmdargs(cmdargs: argparse.Namespace) -> None:
    """Validate command-line values and incompatible operations.

    Validation covers required paths, file extensions, mode-dependent image input,
    and Gmsh availability for workflows that generate a mesh.

    Parameters
    ----------
    cmdargs : argparse.Namespace
        Parsed command-line arguments.

    Raises
    ------
    SystemExit
        If an input value is invalid or a required executable is unavailable."""
    image = cmdargs.image
    parameters = cmdargs.parameters
    output = cmdargs.output
    gmsh = cmdargs.gmsh
    mode = cmdargs.mode
    workflow = cmdargs.type

    if not parameters:
        pymm_error(
            f"Invalid value for {cli_error_value('-p')}, the parameter file cannot be empty."
        )

    parameter_path = Path(parameters)
    if parameter_path.suffix.lower() != ".toml":
        pymm_error(
            f"Invalid extension for parameter file {cli_error_value(f'-p {parameters}')}, "
            f"the expected extension is {cli_correct_value('.toml')}."
        )

    if not parameter_path.is_file():
        pymm_error(
            f"The parameter file {cli_error_value(f'-p {parameters}')} does not exist or is not "
            "a regular file."
        )

    if not output:
        pymm_error(
            f"Invalid value for {cli_error_value('-o')}, the output folder cannot be empty."
        )

    output_path = Path(output)
    if output_path.exists() and not output_path.is_dir():
        pymm_error(
            f"Invalid value {cli_error_value(f'-o {output}')}, the output path exists and is not "
            "a directory."
        )

    if mode == "image":
        if not image:
            pymm_error(
                f"Invalid value for {cli_error_value('-i')}, an image file is required with "
                f"{cli_correct_value('-m image')}."
            )

        image_path = Path(image)
        if image_path.suffix.lower() != ".png":
            pymm_error(
                f"Invalid extension for image file {cli_error_value(f'-i {image}')}, the expected "
                f"extension is {cli_correct_value('.png')}."
            )

        if not image_path.is_file():
            pymm_error(
                f"The image file {cli_error_value(f'-i {image}')} does not exist or is not a "
                "regular file."
            )

    mesh_workflows = {
        "mesh",
        "mesh_flow",
        "all",
    }
    if workflow in mesh_workflows:
        if not gmsh:
            pymm_error(
                f"Invalid value for {cli_error_value('-g')}, a Gmsh command is required for "
                f"{cli_correct_value('-t {workflow}')}."
            )

        try:
            gmsh_arguments = shlex.split(gmsh)
        except ValueError:
            gmsh_arguments = []

        if not gmsh_arguments:
            pymm_error(f"Invalid Gmsh command {cli_error_value(f'-g {gmsh}')}.")

        try:
            gmsh_result = subprocess.run(
                [*gmsh_arguments, "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                check=False,
            )
        except OSError:
            gmsh_result = None

        if gmsh_result is None or gmsh_result.returncode != 0:
            pymm_error(
                f"The Gmsh executable {cli_error_value(f'-g {gmsh}')} is not available or not "
                "working."
            )


def check_toml(cfg: PymmConfig) -> None:
    """Validate the TOML configuration values.

    Parameters
    ----------
    cfg : PymmConfig
        Shared runtime configuration.

    Raises
    ------
    SystemExit
        If a value has an invalid type, range, or accepted value."""
    positive_values = {
        "length": cfg.length,
        "width": cfg.width,
        "thickness": cfg.thickness,
        "rescale": cfg.rescale,
        "lineWidth": cfg.lineWidth,
        "channelWidth": cfg.channelWidth,
        "meshSize": cfg.meshSize,
        "viscosity": cfg.viscosity,
        "diffusion": cfg.diffusion,
        "tracerTime": cfg.tracerTime,
        "tracerWrite": cfg.tracerWrite,
        "pressureConv": cfg.pressureConv,
        "velocityConv": cfg.velocityConv,
        "iterationsMax": cfg.iterationsMax,
        "tracerStep": cfg.tracerStep,
    }
    for name, value in positive_values.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            pymm_error(
                f"The configured value for {name} must be a positive number, but "
                f"{value!r} was provided."
            )
    nonnegative_values = {
        "grainsSize": cfg.grainsSize,
        "borderTol": cfg.borderTol,
        "grainsTol": cfg.grainsTol,
        "inletValue": cfg.inletValue,
    }
    for name, value in nonnegative_values.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            pymm_error(
                f"The configured value for {name} must be a nonnegative number, but "
                f"{value!r} was provided."
            )
    if cfg.grainMeaning not in [0, 1] or isinstance(cfg.grainMeaning, bool):
        pymm_error(
            "The configured value for grainMeaning must be either 0 for light grains "
            f"or 1 for dark grains, but {cfg.grainMeaning!r} was provided."
        )
    if (
        not isinstance(cfg.threshold, (int, float))
        or isinstance(cfg.threshold, bool)
        or not 0 <= cfg.threshold <= 1
    ):
        pymm_error(
            "The configured value for threshold must be between 0 and 1, but "
            f"{cfg.threshold!r} was provided."
        )
    valid_inlet_locations = ["left", "top", "right", "bottom"]
    if cfg.inletLocation not in valid_inlet_locations:
        pymm_error(
            "The configured value for inletLocation must be one of "
            f"{valid_inlet_locations}, but {cfg.inletLocation!r} was provided."
        )
    integer_values = {
        "grainsSize": cfg.grainsSize,
        "iterationsMax": cfg.iterationsMax,
    }
    for name, value in integer_values.items():
        if not isinstance(value, int) or isinstance(value, bool):
            pymm_error(
                f"The configured value for {name} must be an integer, but "
                f"{value!r} was provided."
            )


def process_image(
    cfg: PymmConfig, fol: Path, mode: str, in_image: str
) -> tuple[int, int, list[NDArray[np.float64]], NDArray[np.float64]]:
    """Segment the input image and extract its contours.

    Write diagnostic PNG files and return the rescaled dimensions, interior-grain
    contours, and external boundary.

    Parameters
    ----------
    cfg : PymmConfig
        Shared runtime configuration.
    fol : pathlib.Path
        Output directory for generated figures.
    mode : str
        Microsystem setup, ``image`` or ``device``.
    in_image : str
        Path to the input PNG image.

    Returns
    -------
    tuple[int, int, list[numpy.ndarray], numpy.ndarray]
        Image height, image width, grain contours, and external boundary."""
    # Read the image
    im0 = np.array(io.imread(in_image, as_gray=True))
    # Convert the image to binary (black and white) and rescale
    meaning = 1 - 2 * cfg.grainMeaning
    threshold_scaled = meaning * cfg.threshold
    flipped = im0[::-1]
    im = ~(meaning * flipped < threshold_scaled)
    im[0, :] = True
    im[-1, :] = True
    im[:, 0] = True
    im[:, -1] = True
    if mode == "device" and im.shape[0] > 2 and im.shape[1] > 2:
        im[1, 1:-1] = False
        im[-2, 1:-1] = False
    im = skimage.transform.rescale(im, cfg.rescale)
    imH, imL = im.shape[0], im.shape[1]

    im = np.pad(im, ADD_BORDER, pad_with, padder=1)

    # Save the binary image for visualization
    fol.mkdir(parents=True, exist_ok=True)
    fig, axis = plt.subplots()
    axis.imshow(
        im[ADD_BORDER:-ADD_BORDER, ADD_BORDER:-ADD_BORDER],
        cmap=mpl.colormaps["gray_r"],
    )
    axis.axis("image")
    axis.set_xticks([])
    axis.set_yticks([])
    fig.savefig(f"{fol}/binary_image.png", dpi=600)

    # Extract the contour of the grains on the image border and interior
    border = remove_small_objects(im, max_size=(imH + 2 * imL) * ADD_BORDER)
    grains = remove_small_objects(~(border) & im, max_size=cfg.grainsSize)
    cn_border = measure.find_contours(
        border, 0.5, fully_connected="high", positive_orientation="high"
    )
    grains = grains[ADD_BORDER:-ADD_BORDER, ADD_BORDER:-ADD_BORDER]
    cn_grains = measure.find_contours(
        grains, 0.5, fully_connected="high", positive_orientation="high"
    )
    boundary = make_figures(cfg, fol, im, border, cn_grains, cn_border)
    return imH, imL, cn_grains, boundary


def make_figures(
    cfg: PymmConfig,
    fol: Path,
    im: NDArray[np.bool_],
    border: NDArray[np.bool_],
    cn_grains: list[NDArray[np.float64]],
    cn_border: list[NDArray[np.float64]],
) -> NDArray[np.float64]:
    """Create diagnostic figures for the grains and external boundary.

    Parameters
    ----------
    cfg : PymmConfig
        Shared runtime configuration.
    fol : pathlib.Path
        Output directory for generated figures.
    im : numpy.ndarray
        Padded binary image.
    border : numpy.ndarray
        Boolean mask containing the external border.
    cn_grains : list[numpy.ndarray]
        Interior-grain contours in ``(row, column)`` order.
    cn_border : list[numpy.ndarray]
        Candidate external-boundary contours.

    Returns
    -------
    numpy.ndarray
        Selected external boundary in reversed point order."""
    slices = slice(ADD_BORDER, -ADD_BORDER)
    image_slice = (slices, slices)
    fig, axis = plt.subplots()
    axis.imshow(border[image_slice], cmap=mpl.colormaps["gray_r"])
    lmax, boundary = 0, np.empty(0)
    for contour in cn_border:
        contour = measure.approximate_polygon(contour, tolerance=cfg.borderTol)
        peri = np.max(
            (contour[:, 0] - np.roll(contour[:, 0], 1)) ** 2
            + (contour[:, 1] - np.roll(contour[:, 1], 1)) ** 2
        )
        if peri > lmax:
            lmax = peri
            boundary = contour
    shifted_border_x = boundary[:, 1] - ADD_BORDER
    shifted_border_y = boundary[:, 0] - ADD_BORDER
    axis.plot(shifted_border_x, shifted_border_y, linewidth=cfg.lineWidth)
    axis.axis("image")
    axis.set_xticks([])
    axis.set_yticks([])
    fig.savefig(f"{fol}/extracted_border.png", dpi=600)

    fig, axis = plt.subplots()
    axis.imshow(im[image_slice], cmap=mpl.colormaps["gray_r"])
    grain_lines = []
    for contour in cn_grains:
        if len(contour) > 3:
            approximated = measure.approximate_polygon(contour, tolerance=cfg.grainsTol)
            grain_lines.append((approximated[:, 1], approximated[:, 0]))
    segments = [np.column_stack((x_vals, y_vals)) for x_vals, y_vals in grain_lines]
    axis.add_collection(LineCollection(segments, linewidths=cfg.lineWidth, color="red"))
    axis.axis("image")
    axis.set_xticks([])
    axis.set_yticks([])
    fig.savefig(f"{fol}/interior_grains.png", dpi=600)

    fig, axis = plt.subplots()
    axis.imshow(im[image_slice], cmap=mpl.colormaps["gray_r"])
    axis.plot(shifted_border_x, shifted_border_y, linewidth=cfg.lineWidth)
    segments = [np.column_stack((x_vals, y_vals)) for x_vals, y_vals in grain_lines]
    axis.add_collection(LineCollection(segments, linewidths=cfg.lineWidth, color="red"))
    axis.axis("image")
    axis.set_xticks([])
    axis.set_yticks([])
    fig.savefig(f"{fol}/interior_grains_border.png", dpi=600)
    return boundary[::-1]


def extract_borders(
    boundary: NDArray[np.float64],
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    float,
    float,
    float,
    float,
]:
    """Split the external contour into four image boundaries.

    Parameters
    ----------
    boundary : numpy.ndarray
        Closed contour in padded-image coordinates.

    Returns
    -------
    tuple
        Left, top, right, and bottom point arrays followed by the four reference
        coordinates used for boundary tagging."""
    shifted = boundary - ADD_BORDER
    aa, dd, cc = 0, 0, 0
    pl_list: list[list[float]] = []
    pt_list: list[list[float]] = []
    pr_list: list[list[float]] = []
    pb_list: list[list[float]] = []
    bb, bl = np.min(boundary[:, 0]), np.min(boundary[:, 1])
    bt, br = np.max(boundary[:, 0]), np.max(boundary[:, 1])
    for idx in range(len(boundary) - 1):
        x_val = boundary[idx, 0]
        y_val = boundary[idx, 1]
        sx = shifted[idx, 0]
        sy = shifted[idx, 1]
        if x_val > bb + 1 and aa == 0:
            pr_list.append([sy, sx])
        else:
            aa = 1
        if (y_val > bl + 1 and aa == 1) and not pl_list:
            pb_list.append([sy, sx])
        if y_val < bl + 1:
            dd = 1
        if (x_val > bb - 1 and dd == 1) and (cc == 0 and pb_list):
            pl_list.append([sy, sx])
        if x_val > bt - 1 and aa == 1:
            cc = 1
        if len(pl_list) > 1 and cc == 1:
            pt_list.append([sy, sx])
    pl = np.array(pl_list, dtype=np.float64)
    pt = np.array(pt_list, dtype=np.float64)
    pr = np.array(pr_list, dtype=np.float64)
    pb = np.array(pb_list, dtype=np.float64)
    return pl, pt, pr, pb, bb, bl, bt, br


def pad_with(
    vector: NDArray[np.float64], pad_width: tuple[int, int], _iaxis: int, kwargs: dict
) -> None:
    """Fill NumPy padding regions with a constant value.

    Parameters
    ----------
    vector : numpy.ndarray
        One-dimensional array view modified in place.
    pad_width : tuple[int, int]
        Number of values padded before and after the original array.
    _iaxis : int
        Axis supplied by :func:`numpy.pad`; unused.
    kwargs : dict
        Callback options. ``padder`` selects the fill value."""
    pad_value = kwargs.get("padder", 10)
    vector[: pad_width[0]] = pad_value
    vector[-pad_width[1] :] = pad_value


def _assign_boundary(
    point: NDArray[np.float64],
    start_index: int,
    number_of_segments: int,
    reference_value: float,
    coordinate_index: int,
    target: list[int],
    wall: list[int],
) -> int:
    """Assign contour segments to an opening or wall.

    Parameters
    ----------
    point : numpy.ndarray
        Closed boundary-point array.
    start_index : int
        First segment index to inspect.
    number_of_segments : int
        Number of consecutive segments to classify.
    reference_value : float
        Coordinate of the target image edge.
    coordinate_index : int
        Coordinate column used for comparison.
    target : list[int]
        Target-boundary indices updated in place.
    wall : list[int]
        Wall-boundary indices updated in place.

    Returns
    -------
    int
        First segment index after the processed range."""
    shifted_reference = reference_value - ADD_BORDER
    indices = np.arange(start_index, start_index + number_of_segments)
    values0 = point[indices, coordinate_index]
    values1 = point[indices + 1, coordinate_index]
    mask = (np.abs(shifted_reference - values0) < 1) & (
        np.abs(shifted_reference - values1) < 1
    )
    target.extend(indices[mask].tolist())
    wall.extend(indices[~mask].tolist())
    return start_index + number_of_segments


def boundary_tags_left_top(
    point: NDArray[np.float64],
    pl: NDArray[np.float64],
    pt: NDArray[np.float64],
    bl: float,
    bt: float,
    wall: list[int],
) -> tuple[list[int], list[int], int]:
    """Assign boundary tags for the left and top edges.

    Parameters
    ----------
    point : numpy.ndarray
        Closed boundary-point array.
    pl : numpy.ndarray
        Left-boundary points.
    pt : numpy.ndarray
        Top-boundary points.
    bl : float
        Left reference coordinate.
    bt : float
        Top reference coordinate.
    wall : list[int]
        Wall indices updated in place.

    Returns
    -------
    tuple[list[int], list[int], int]
        Left tags, top tags, and the first unprocessed segment index."""
    bdnL: list[int] = []
    bdnT: list[int] = []
    index: int = 0
    index = _assign_boundary(point, index, len(pl) - 1, bl, 0, bdnL, wall)
    index = _assign_boundary(point, index, len(pt), bt, 1, bdnT, wall)
    return bdnL, bdnT, index


def boundary_tags_right_bottom(
    point: NDArray[np.float64],
    start_index: int,
    pr: NDArray[np.float64],
    pb: NDArray[np.float64],
    bb: float,
    br: float,
    wall: list[int],
) -> tuple[list[int], list[int]]:
    """Assign boundary tags for the right and bottom edges.

    Parameters
    ----------
    point : numpy.ndarray
        Closed boundary-point array.
    start_index : int
        First segment index to inspect.
    pr : numpy.ndarray
        Right-boundary points.
    pb : numpy.ndarray
        Bottom-boundary points.
    bb : float
        Bottom reference coordinate.
    br : float
        Right reference coordinate.
    wall : list[int]
        Wall indices updated in place.

    Returns
    -------
    tuple[list[int], list[int]]
        Right and bottom boundary tags."""
    bdnR: list[int] = []
    bdnB: list[int] = []
    index: int = start_index
    index = _assign_boundary(point, index, len(pr), br, 0, bdnR, wall)
    if pb.size == 0:
        bdnB.append(index)
    else:
        index = _assign_boundary(point, index, len(pb), bb, 1, bdnB, wall)
    return bdnR, bdnB


def write_geo(
    cfg: PymmConfig,
    fol: Path,
    pat: Path,
    mode: str,
    gmsh: str,
    imH: int,
    imL: int,
    cn_grains: list[NDArray[np.float64]],
    pl: NDArray[np.float64],
    pt: NDArray[np.float64],
    pr: NDArray[np.float64],
    pb: NDArray[np.float64],
    bdnL: list[int],
    bdnT: list[int],
    bdnR: list[int],
    bdnB: list[int],
    wall: list[int],
) -> None:
    """Write the Gmsh geometry file and generate the mesh.

    Convert image contours to Gmsh points and physical boundaries, render the
    mode-specific Mako template, and execute Gmsh.

    Parameters
    ----------
    cfg : PymmConfig
        Shared runtime configuration.
    fol : pathlib.Path
        Output directory.
    pat : pathlib.Path
        Project root containing the templates.
    mode : str
        Microsystem setup, ``image`` or ``device``.
    gmsh : str
        Gmsh executable or command.
    imH : int
        Rescaled image height in pixels.
    imL : int
        Rescaled image width in pixels.
    cn_grains : list[numpy.ndarray]
        Interior-grain contours.
    pl, pt, pr, pb : numpy.ndarray
        Left, top, right, and bottom boundary points.
    bdnL, bdnT, bdnR, bdnB : list[int]
        Segment indices for the physical boundaries.
    wall : list[int]
        Segment indices for wall boundaries.

    Raises
    ------
    subprocess.CalledProcessError
        If Gmsh exits with a nonzero status."""
    mapping = {
        "left": ("L", "R"),
        "top": ("T", "B"),
        "right": ("R", "L"),
        "bottom": ("B", "T"),
    }
    inlet, outlet = mapping[cfg.inletLocation.lower()]

    pl -= 0.5
    pr += np.array([0.5, -0.5])

    if mode == "device":

        point_left_lines: list[str] = []
        append = point_left_lines.append
        for i, (x, y) in enumerate(pl, 1):
            append(f"Point(#Tp[]+{i}) = {{{x}*rL/L, {y}*rH/H, 0, hb}};")
        point_right_lines: list[str] = []
        append = point_right_lines.append
        for i, (x, y) in enumerate(pr, 1):
            append(f"Point(#Tp[]+{i}) = {{{x}*rL/L, {y}*rH/H, 0, hb}};")
    else:
        pt += np.array([0.5, -0.5])
        pb += np.array([0.5, -0.5])
        point_lines: list[str] = []
        append = point_lines.append
        idx = 1
        for arr, sl in (
            (pl, slice(None)),
            (pt, slice(1, None)),
            (pr, slice(None)),
            (pb, slice(None)),
        ):

            sub = arr[sl]
            for i in range(sub.shape[0]):
                x = sub[i, 0]
                y = sub[i, 1]
                append(f"Point(#Tp[]+{idx}) = {{{x}*rL/L, {y}*rH/H, 0, hb}};")
                idx += 1

        bdn_lines: list[str] = []
        bdn_lines_append = bdn_lines.append

        for idx in bdnL:
            val = idx + 2
            bdn_lines_append(f"bdnL[] += {{out[{val}]}};")
        for idx in bdnT:
            val = idx + 2
            bdn_lines_append(f"bdnT[] += {{out[{val}]}};")
        for idx in bdnR:
            val = idx + 2
            bdn_lines_append(f"bdnR[] += {{out[{val}]}};")
        for idx in bdnB:
            val = idx + 2
            bdn_lines_append(f"bdnB[] += {{out[{val}]}};")
        wall_slice = wall[:-1]
        for idx in wall_slice:
            val = idx + 2
            bdn_lines_append(f"bdnW[] += {{out[{val}]}};")

    grain_lines = []
    nog = 0
    show_progress = sys.stdout.isatty()
    if show_progress:
        bar_ctx = alive_bar(len(cn_grains), bar="fish")
    else:
        bar_ctx = nullcontext()
    with bar_ctx as bar_animation:
        for contour in cn_grains:
            if show_progress:
                bar_animation()
            contour = measure.approximate_polygon(contour, tolerance=cfg.grainsTol)
            points = contour[:-1][:, [1, 0]]
            if points.shape[0] > 2:
                nog += 1
                grain_lines.append('Tp[] = Point "*";')
                grain_lines.append(f"h({nog}) = hs;")
                for idx, (x, y) in enumerate(points, 1):
                    grain_lines.append(
                        f"Point(#Tp[]+{idx}) = {{(rL/L)*{x}, {y}*rH/H, 0, h({nog})}};"
                    )
                grain_lines.extend(
                    [
                        'Tp1[] = Point "*";',
                        "For i In {#Tp[]+1 : #Tp1[] - 1}",
                        "  Line(i)={i, i + 1};",
                        "EndFor",
                        "Line(#Tp1[])={#Tp1[], #Tp[]+1};",
                        "Line Loop(1+n+1)={#Tp[]+1: #Tp1[]};",
                        "n = n+1;",
                    ]
                )

    template_path = pat / f"templates/grid/{mode}.mako"
    geo_path = fol / "mesh.geo"

    mytemplate = Template(filename=str(template_path))
    if mode == "image":
        point_lines_str = "\n".join(point_lines)
        bdn_lines_str = "\n".join(bdn_lines)
    else:
        point_lines_str = None
        bdn_lines_str = None
    if mode == "device":
        point_left_lines_str = "\n".join(point_left_lines)
        point_right_lines_str = "\n".join(point_right_lines)
    else:
        point_left_lines_str = None
        point_right_lines_str = None
    grain_lines_str = "\n".join(grain_lines)
    filledtemplate = mytemplate.render(
        imL=imL,
        imH=imH,
        length=cfg.length,
        width=cfg.width,
        thickness=cfg.thickness,
        meshSize=cfg.meshSize,
        channelWidth=cfg.channelWidth,
        inlet=inlet,
        outlet=outlet,
        point_lines=point_lines_str,
        point_left_lines=point_left_lines_str,
        point_right_lines=point_right_lines_str,
        grain_lines=grain_lines_str,
        bdn_lines=bdn_lines_str,
    )

    with open(geo_path, "w", encoding="utf8") as file:
        file.write(filledtemplate)
    pymm_info("Executing Gmsh")
    subprocess.run([gmsh, str(geo_path), "-3"], check=True)


def copy_and_replace(src: Path, dst: Path, replacements: dict[str, Any]) -> None:
    """Copy a text template and replace its placeholders.

    Parameters
    ----------
    src : pathlib.Path
        Source template file.
    dst : pathlib.Path
        Destination file.
    replacements : dict[str, Any]
        Literal placeholders and replacement values."""
    text = src.read_text(encoding="utf8")
    for key, value in replacements.items():
        text = text.replace(key, str(value))
    dst.write_text(text, encoding="utf8")


def run_stokes(cfg: PymmConfig, fol: Path, pat: Path) -> None:
    """Write and run the steady incompressible-flow case.

    Create the OpenFOAM case, convert the Gmsh mesh, run the flow solver, export VTK
    results, and copy them to the pymm output directory.

    Parameters
    ----------
    cfg : PymmConfig
        Shared runtime configuration.
    fol : pathlib.Path
        Output directory containing ``mesh.msh``.
    pat : pathlib.Path
        Project root containing the OpenFOAM templates.

    Raises
    ------
    SystemExit
        If ``gmshToFoam`` is unavailable.
    subprocess.CalledProcessError
        If an OpenFOAM command fails."""
    template_base = f"{pat}/templates/OpenFOAM/flowStokes"
    flow_path = fol / "OpenFOAM/flowStokes"
    vtk_target = fol / "VTK_flowStokes"

    fol.mkdir(parents=True, exist_ok=True)
    (fol / "OpenFOAM").mkdir(parents=True, exist_ok=True)

    for name in ["OpenFOAM/flowStokes", "VTK_flowStokes"]:
        path = fol / name
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)

    for name in ["0", "constant", "system"]:
        (flow_path / name).mkdir(parents=True, exist_ok=True)

    for file_name in [
        Path("0/U"),
        Path("constant/momentumTransport"),
        Path("system/fvSchemes"),
    ]:
        shutil.copy2(template_base / file_name, flow_path / file_name)
    where = Path("0/p")
    copy_and_replace(
        template_base / where,
        flow_path / where,
        {
            "@inletValue@": cfg.inletValue,
        },
    )
    where = Path("constant/physicalProperties")
    copy_and_replace(
        template_base / where,
        flow_path / where,
        {
            "@viscosity@": cfg.viscosity,
        },
    )
    where = Path("system/controlDict")
    copy_and_replace(
        template_base / where,
        flow_path / where,
        {
            "@iterationsMax@": cfg.iterationsMax,
        },
    )
    where = Path("system/fvSolution")
    copy_and_replace(
        template_base / where,
        flow_path / where,
        {
            "@pressureConv@": cfg.pressureConv,
            "@velocityConv@": cfg.velocityConv,
        },
    )

    shutil.copy2(fol / "mesh.msh", flow_path)

    pymm_info("Executing gmshToFoam")
    if shutil.which("gmshToFoam") is None:
        pymm_error(
            f"executable {cli_error_value('gmshToFoam')} was not found in PATH; "
            "load or install OpenFOAM before running the flow workflow."
        )
    subprocess.run(["gmshToFoam", "mesh.msh"], cwd=flow_path, check=True)

    boundary_path = flow_path / "constant/polyMesh/boundary"
    lines = boundary_path.read_text(encoding="utf8").splitlines()
    lines[20] = "type      empty;"
    boundary_path.write_text("\n".join(lines) + "\n", encoding="utf8")

    # Running the steady-state flow simulation
    pymm_info("Executing foamRun")
    subprocess.run(
        ["foamRun", "-solver", "incompressibleFluid"], cwd=flow_path, check=True
    )
    pymm_info("Executing foamToVTK")
    subprocess.run(["foamToVTK"], cwd=flow_path, check=True)

    vtk_source = flow_path / "VTK"
    for item in vtk_source.iterdir():
        target = vtk_target / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy(item, target)


def run_tracer(cfg: PymmConfig, fol: Path, pat: Path) -> None:
    """Write and run the transient tracer-transport case.

    Create the OpenFOAM case, copy the latest flow fields and mesh, run the tracer
    solver, export VTK results, and copy them to the pymm output directory.

    Parameters
    ----------
    cfg : PymmConfig
        Shared runtime configuration.
    fol : pathlib.Path
        Output directory containing a completed flow case.
    pat : pathlib.Path
        Project root containing the OpenFOAM templates.

    Raises
    ------
    SystemExit
        If ``topoSet`` is unavailable.
    subprocess.CalledProcessError
        If an OpenFOAM command fails."""
    template_base = f"{pat}/templates/OpenFOAM/tracerTransport"
    tracer_path = fol / "OpenFOAM/tracerTransport"
    flow_stokes_path = fol / "OpenFOAM/flowStokes"

    for name in ["VTK_tracerTransport", "OpenFOAM/tracerTransport"]:
        path_obj = fol / name
        if path_obj.exists():
            shutil.rmtree(path_obj)
        path_obj.mkdir(parents=True, exist_ok=True)

    for name in ["0", "constant", "system"]:
        (tracer_path / name).mkdir(parents=True, exist_ok=True)

    for file_name in [
        Path("0/T"),
        Path("constant/fvConstraints"),
        Path("constant/momentumTransport"),
        Path("system/fvSchemes"),
        Path("system/fvSolution"),
        Path("system/topoSetDict"),
    ]:
        shutil.copy2(template_base / file_name, tracer_path / file_name)
    where = Path("constant/physicalProperties")
    copy_and_replace(
        template_base / where,
        tracer_path / where,
        {
            "@viscosity@": cfg.viscosity,
        },
    )
    where = Path("system/controlDict")
    copy_and_replace(
        template_base / where,
        tracer_path / where,
        {
            "@tracerTime@": cfg.tracerTime,
            "@tracerStep@": cfg.tracerStep,
            "@tracerWrite@": cfg.tracerWrite,
            "@diffusion@": cfg.diffusion,
        },
    )

    folders = [path for path in flow_stokes_path.iterdir() if path.is_dir()]
    latest_folder = max(folders, key=lambda path: path.stat().st_ctime)
    folders.remove(latest_folder)
    latest_folder = max(folders, key=lambda path: path.stat().st_ctime)

    shutil.copy2(latest_folder / "U", tracer_path / "0/")
    shutil.copy2(latest_folder / "p", tracer_path / "0/")
    shutil.copytree(
        flow_stokes_path / "constant/polyMesh",
        tracer_path / "constant/polyMesh",
        dirs_exist_ok=True,
    )
    pymm_info("Executing topoSet")
    if shutil.which("topoSet") is None:
        pymm_error(
            f"executable {cli_error_value('topoSet')} was not found in PATH; "
            "load or install OpenFOAM before running the tracer workflow."
        )
    subprocess.run(["topoSet"], cwd=tracer_path, check=True)

    # Running the simulation of tracer transport
    pymm_info("Executing foamRun")
    subprocess.run(["foamRun"], cwd=tracer_path, check=True)
    pymm_info("Executing foamToVTK")
    subprocess.run(["foamToVTK"], cwd=tracer_path, check=True)
    vtk_source = tracer_path / "VTK"
    for item in vtk_source.iterdir():
        target = fol / "VTK_tracerTransport" / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy(item, target)


def _supports_color(stream: object = sys.stderr) -> bool:
    """Check whether an output stream supports ANSI colors.

    Parameters
    ----------
    stream : object, optional
        Output stream to inspect.

    Returns
    -------
    bool
        Whether ANSI color output is enabled."""
    return (
        hasattr(stream, "isatty")
        and stream.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM") != "dumb"
    )


def _colorize(
    text: str,
    code: str,
    stream: object = sys.stderr,
) -> str:
    """Wrap text in an ANSI color sequence when supported.

    Parameters
    ----------
    text : str
        Text to format.
    code : str
        ANSI color code.
    stream : object, optional
        Output stream used to determine color support.

    Returns
    -------
    str
        Colored or unchanged text."""
    if not _supports_color(stream):
        return text
    return f"\033[{code}m{text}\033[0m"


def cli_error_value(value: str) -> str:
    """Format an invalid CLI option or value.

    Parameters
    ----------
    value : str
        Option or value to format.

    Returns
    -------
    str
        Quoted value, colored red when supported."""
    return _colorize(repr(value), ANSI_RED)


def pymm_error(message: str) -> NoReturn:
    """Raise a fatal pymm command-line error.

    Parameters
    ----------
    message : str
        Error message to display.

    Raises
    ------
    SystemExit
        Always raised with the formatted error message."""
    label = _colorize("error", ANSI_BOLD_RED)
    raise SystemExit(f"{pymm_name()}: {label}: {message}")


def pymm_info(message: str) -> None:
    """Display an informational pymm message.

    Parameters
    ----------
    message : str
        Progress or workflow message."""
    label = _colorize("info", ANSI_BOLD_BLUE, sys.stdout)
    print(f"{pymm_name()}: {label}: {message}")


def cli_info_value(value: str) -> str:
    """Format an informational CLI option or value.

    Parameters
    ----------
    value : str
        Option or value to format.

    Returns
    -------
    str
        Quoted value, colored blue when supported."""
    return _colorize(repr(value), ANSI_BLUE)


def cli_correct_value(value: str) -> str:
    """Format a valid CLI option or value.

    Parameters
    ----------
    value : str
        Accepted option, value, or example.

    Returns
    -------
    str
        Quoted value, colored green when supported."""
    return _colorize(repr(value), ANSI_GREEN)


def pymm_success(msg: str, output_dir: str, filenames: list[str]) -> None:
    """Display generated output files and locations.

    Parameters
    ----------
    msg : str
        Optional success message.
    output_dir : str
        Directory containing the generated files.
    filenames : list[str]
        Generated filenames."""
    label = _colorize("success", ANSI_BOLD_GREEN, sys.stdout)
    if not filenames:
        print(f"{pymm_name()}: {label}: {msg}{output_dir}")
    elif len(filenames) == 1:
        print(f"{pymm_name()}: {label}: {msg}{output_dir}/{filenames[0]}")
    elif len(filenames) <= 5:
        print(f"{pymm_name()}: {label}{msg}")
        print(f"      Output directory: {output_dir}")
        print(f"      Files ({len(filenames)}): {', '.join(filenames)}")
    else:
        print(f"{pymm_name()}: {label}{msg}")
        print(f"      Output directory: {output_dir}")
        print(f"      Files ({len(filenames)}):")
        for filename in filenames:
            print(f"        - {filename}")


def pymm_name(stream: object = sys.stderr) -> str:
    """Format the pymm program name.

    Parameters
    ----------
    stream : object, optional
        Output stream used to determine color support.

    Returns
    -------
    str
        Formatted program name."""
    characters = [("pymm", "1")]
    return "".join(
        _colorize(character, color, stream) for character, color in characters
    )


if __name__ == "__main__":
    main(sys.argv[1:])

# {
# Copyright 2022-2026, NORCE Research AS, Computational
# Geosciences and Modelling.

# This file is part of the pymm module.

# pymm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pymm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this file.  If not, see <http://www.gnu.org/licenses/>.
# }
