""" dry run
"""
import json
import pathlib

from autoname import autoname
from config import CONFIG


@autoname
def draw_gc(
    session=None,
    period=0.66e-6,
    ff=0.5,
    wl=1550e-9,
    n_gratings=50,
    wg_height=220e-9,
    etch_depth=70e-9,
    box_height=2e-6,
    clad_height=2e-6,
    substrate_height=2e-6,
    material="Si (Silicon) - Palik",
    material_clad="SiO2 (Glass) - Palik",
    wg_width=500e-9,
    polarization="TE",
    wavelength=1550e-9,
    gc_xmin=-3e-6,
    fiber_angle_deg=20,
    wl_span=300e-9,  # wavelength span
    mesh_accuracy=3,  # FDTD simulation mesh accuracy
    frequency_points=100,  # global frequency points
    simulation_time=1000e-15,  # maximum simulation time [s]
    core_index=1.4682,
    cladding_index=1.4629,
    core_diameter=8.2e-6,
    cladding_diameter=100e-6,
    d=0.2e-6,
):

    s = session
    return dict(session=s)


def sparameters(
    session=None, draw_function=draw_gc, dirpath=CONFIG["workspace"], **kwargs,
):

    s = session
    simdict = draw_gc(session=s, **kwargs)

    dirpath = pathlib.Path(dirpath) / simdict["name_function"]
    dirpath.mkdir(exist_ok=True)
    filepath = dirpath / simdict["name"]
    filepath_sim_settings = filepath.with_suffix(".settings.json")
    # filepath_json = filepath.with_suffix(".json")
    # filepath_fsp = str(filepath.with_suffix(".fsp"))
    # filepath_sp = str(filepath.with_suffix(".dat"))

    print(f"wroting sparameters to {filepath}")

    if simdict.get("settings"):
        with open(filepath_sim_settings, "w") as f:
            json.dump(simdict.get("settings"), f)
    return simdict.get("name")
    return simdict.get("settings")


if __name__ == "__main__":
    session = None
    # d = gc(session=session)
    # r = sparameters(session=d["session"], settings=d["settings"])

    r = sparameters(wl=1540e-9, wg_height=220e-9)
    print(r)
