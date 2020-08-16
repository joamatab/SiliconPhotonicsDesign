"""
loads a configuration from 3 files, high priority overwrites low priority:

1. A config.yml found in the current working directory (high priority)
2. ~/.config/pylum.yml specific for the machine
3. the default config is in this file (lowest priority)

"""

__all__ = ["CONFIG"]

import logging
import pathlib

import hiyapyco

default_config = """
keySample: valueSample
"""

home = pathlib.Path.home()
cwd = pathlib.Path.cwd()
cwd_config = cwd / "config.yml"

home_config = home / ".config" / "pylum.yml"
module_path = pathlib.Path(__file__).parent.absolute()
repo_path = module_path.parent

CONFIG = hiyapyco.load(
    str(default_config),
    str(home_config),
    str(cwd_config),
    failonmissingfiles=False,
    loglevelmissingfiles=logging.DEBUG,
)
CONFIG["module_path"] = module_path
CONFIG["repo_path"] = repo_path
CONFIG["templates"] = repo_path / "templates"
CONFIG["repo_workspace"] = repo_path / "workspace"
CONFIG["workspace"] = pathlib.Path(
    CONFIG.get("workspace", repo_path / "workspace")
).absolute()

CONFIG["grating_coupler"] = repo_path / "templates" / "fiber_coupler"
CONFIG["grating_coupler_2D"] = CONFIG["grating_coupler"] / "grating_coupler_2D.fsp"
CONFIG["grating_coupler_2D_base"] = CONFIG["grating_coupler"] / "grating_base.fsp"
CONFIG["dbr"] = repo_path / "templates" / "dbr" / "dbr_cell.fsp"
CONFIG["materials"] = repo_path / "templates" / "waveguide" / "materials.lsf"

CONFIG["workspace"].mkdir(exist_ok=True)

CONFIG[
    "run_fdtd_script"
] = """
dirpath = pathlib.Path(__file__).parent.absolute()

s = lumapi.FDTD()
s.cd(str(dirpath))
h.eval("main.lsf")

"""

# materials = [
#     "Si (Silicon) - Palik",
#     "SiO2 (Glass) - Palik",
#     "Si3N4 (Silicon Nitride) - Phillip",
#     ]

materials = {
    "si": "Si (Silicon) - Palik",
    "sio2": "SiO2 (Glass) - Palik",
    "sin": "Si3N4 (Silicon Nitride) - Phillip",
}


materials2 = [
    "Ag (Silver) - CRC",
    "Ag (Silver) - Johnson and Christy",
    "Ag (Silver) - Palik (0-2um)",
    "Ag (Silver) - Palik (1-10um)",
    "Al (Aluminium) - CRC",
    "Al (Aluminium) - Palik",
    "Al2O3 - Palik",
    "Au (Gold) - CRC",
    "Au (Gold) - Johnson and Christy",
    "Au (Gold) - Palik",
    "C (graphene) - Falkovsky (mid-IR)",
    "Cr (Chromium) - CRC",
    "Cr (Chromium) - Palik",
    "Cu (Copper) - CRC",
    "Cu (Copper) - Palik",
    "Fe (Iron) - CRC",
    "Fe (Iron) - Palik",
    "GaAs - Palik",
    "Ge (Germanium) - CRC",
    "Ge (Germanium) - Palik",
    "H2O (Water) - Palik",
    "In (Indium) - Palik",
    "InAs - Palik",
    "InP - Palik",
    "Ni (Nickel) - CRC",
    "Ni (Nickel) - Palik",
    "PEC (Perfect Electrical Conductor)",
    "Pd (Palladium) - Palik",
    "Pt (Platinum) - Palik",
    "Rh (Rhodium) - Palik",
    "Si (Silicon) - Palik",
    "Si3N4 (Silicon Nitride) - Kischkat",
    "Si3N4 (Silicon Nitride) - Phillip",
    "SiO2 (Glass) - Palik",
    "Sn (Tin) - Palik",
    "Ta (Tantalum) - CRC",
    "Ti (Titanium) - CRC",
    "Ti (Titanium) - Palik",
    "TiN - Palik",
    "V (Vanadium ) - CRC",
    "W (Tungsten) - CRC",
    "W (Tungsten) - Palik",
]

if __name__ == "__main__":
    print(CONFIG["workspace"])
