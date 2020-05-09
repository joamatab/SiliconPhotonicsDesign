""" pylut: lumerical templates for simulations"""

import pylut.plot as plot
from pylut.autoname import autoname
from pylut.config import CONFIG
from pylut.loadmat import loadmat
from pylut.run import run_fdtd, run_mode
from pylut.write_scripts import mkdir, write_scripts

__version__ = "0.0.1"
__author__ = "Joaquin <j>"
__all__ = [
    "CONFIG",
    "autoname",
    "loadmat",
    "mkdir",
    "run_fdtd",
    "run_mode",
    "plot",
    "write_scripts",
]


if __name__ == "__main__":
    scripts_dict = dict(name="sample_sim")
    dirpath = mkdir(scripts_dict)
    print(dirpath.exists())
