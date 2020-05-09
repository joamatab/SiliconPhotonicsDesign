""" pylut: lumerical templates for simulations"""

import pylut.plot as plot
from pylut.autoname import autoname
from pylut.config import CONFIG
from pylut.loadmat import loadmat
from pylut.write_scripts import exists, mkdir, write_scripts


def run_mode(scripts_dict, session=None, return_session=False):
    """ runs a dict of scripts in a Lumerical session
    """
    import lumapi

    dirpath = scripts_dict.get("dirpath", write_scripts(scripts_dict))

    s = session or lumapi.MODE()
    s.cd(str(dirpath))

    s.eval(scripts_dict["main.lsf"])

    if return_session:
        return s


def run_fdtd(scripts_dict, session=None, return_session=False):
    """ runs a dict of scripts in a Lumerical session
    """
    import lumapi

    dirpath = scripts_dict.get("dirpath", write_scripts(scripts_dict))

    s = session or lumapi.FDTD()
    s.cd(str(dirpath))

    s.eval(scripts_dict["main.lsf"])

    if return_session:
        return s


__version__ = "0.0.1"
__author__ = "Joaquin <j>"
__all__ = [
    "CONFIG",
    "autoname",
    "exists",
    "loadmat",
    "mkdir",
    "run_fdtd",
    "run_mode",
    "plot",
    "write_scripts",
]


if __name__ == "__main__":
    mkdir("joaquin")
