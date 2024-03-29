[![Build Status](https://github.com/cssr-tools/pymm/actions/workflows/CI.yml/badge.svg)](https://github.com/cssr-tools/pymm/actions/workflows/CI.yml)
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10-blue.svg"></a>
[![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8430989.svg)](https://doi.org/10.5281/zenodo.8430989)

# pymm: An open-source image-based framework for CFD in microsystems 

<img src="docs/text/figs/pymm.gif" width="830" height="700">

This repository provides a workflow to perform computational fluid dynamics (CFD) simulations in microsystems. Given an image of a microsystem and an input text file with few parameters, then the _pymm_ executable process the image and builds the grid using [_Gmsh_](https://gmsh.info) and runs the CFD simulations using [_OpenFOAM_](https://www.openfoam.com).

## Installation
You will first need to install
* OpenFOAM (https://www.openfoam.com) (tested with OpenFOAM-11)
* Gmsh (https://gmsh.info) (tested with Gmsh 4.8.4) 

You will also need to install some Python packages, see ```requirements.txt``` for a complete list. You can install all the required Python packages in a virtual environment with the following commands:
```bash
# Clone the repo
git clone https://github.com/cssr-tools/pymm.git
# Get inside the folder
cd pymm
# Create virtual environment
python3 -m venv vpymm
# Activate virtual environment
source vpymm/bin/activate
# Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel
# Install the pymm package (in editable mode for contributions/modifications; otherwise, pip install .)
pip install -e .
# For contributions/testing/linting, install the dev-requirements
pip install -r dev-requirements.txt
```
Depending on the location where OpenFOAM is installed, then before running pymm (inside the vpymm Python environment), you need to enter the OpenFOAM environment:
```bash
# Check where openFOAM is installed
echo $WM_PROJECT_DIR
# The return value was /opt/openfoam11, then we activate the environment
source /opt/openfoam11/etc/bashrc
# Then, if everything went fine, typing 
gmshToFoam
# should print the argument flags for that OpenFOAM executable.
```

## Running pymm
You can run _pymm_ as a single command line:
```
pymm -i some_input_image.png -p some_input_parameters.txt -o some_output_folder
```
Run `pymm --help` to see all possible command line argument options. Inside the `some_input_parameters.txt` file you provide the framework parameters such as the dimensions of the microsystem, mesh size, inlet pressure, and more. See the .txt files in the examples folder.

## Getting started
See the [_documentation_](https://cssr-tools.github.io/pymm/introduction.html). 

## Journal papers using pymm
The following is a list of journal papers in which _pymm_ is used:

1. Liu, N., Haugen, M., Benali, B., Landa-Marbán, D., Fernø, M.A., 2023. Pore-scale spatiotemporal dynamics of microbial-induced calcium carbonate growth and distribution in porous media.  Int. J. Greenh. Gas Control 125, 103885. https://doi.org/10.1016/j.ijggc.2023.103885
1. Liu, N., Haugen, M., Benali, B., Landa-Marbán, D., Fernø, M.A., 2023. Pore-scale kinetics of calcium dissolution and secondary precipitation during geological carbon storage. Chem. Geol. 641, 121782. https://doi.org/10.1016/j.chemgeo.2023.121782.

## About pymm
The image-based Python package for computational fluid dynamics pymm is funded by [_Center for Sustainable Subsurface Resources_](https://cssr.no) [project no. 331841] and [_NORCE Norwegian Research Centre As_](https://www.norceresearch.no) [project number 101070]. 

Contributions are more than welcome using the fork and pull request approach.