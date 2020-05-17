""" pylum: lumerical templates for simulations"""
import pylum.plot as plot
from pylum.autoname import autoname
from pylum.config import CONFIG
from pylum.loadmat import loadmat
from pylum.run import run_fdtd
from pylum.run import run_mode
from pylum.write_scripts import mkdir
from pylum.write_scripts import write_scripts

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
