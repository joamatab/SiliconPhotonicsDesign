import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np

from pylum.autoname import autoname
from pylum.autoname import get_function_name
from pylum.config import CONFIG


@autoname
def gc2d(
    session=None,
    period=0.66e-6,
    ff=0.5,
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
    wavelength_span=300e-9,  # wavelength span
    mesh_accuracy=3,  # FDTD simulation mesh accuracy
    frequency_points=100,  # global frequency points
    simulation_time=1000e-15,  # maximum simulation time [s]
    base_fsp_path=str(CONFIG["grating_coupler_2D"]),
):
    """ draw 2D grating coupler """
    import lumapi

    s = session or lumapi.FDTD(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()

    s.load(base_fsp_path)
    s.select("GC")
    s.delete()
    s.select("WG")
    s.delete()

    s.select("fiber")
    s.set("theta", fiber_angle_deg)

    s.select("")
    s.set("lambda0", wavelength)

    s.setglobalsource("center wavelength", wavelength)
    s.setglobalsource("wavelength span", wavelength_span)
    # s.select("FDTD")
    # s.set("set simulation bandwidth", True)
    # s.set("simulation wavelength min", wavelength - wavelength_span / 2)
    # s.set("simulation wavelength max", wavelength + wavelength_span / 2)

    gap = period * (1 - ff)
    # etched region of the grating

    s.addrect()
    s.set("name", "GC_base")
    s.set("material", material)
    s.set("x min", gc_xmin)
    s.set("x max", (n_gratings + 1) * period + gc_xmin)
    s.set("y", 0.5 * (wg_height - etch_depth))
    s.set("y span", wg_height - etch_depth)

    # add GC teeth;
    for i in range(n_gratings):
        s.addrect()
        s.set("name", "GC_tooth")
        s.set("material", material)
        s.set("y min", 0)
        s.set("y max", wg_height)
        s.set("x min", gc_xmin + gap + i * period)
        s.set("x max", gc_xmin + period + i * period)
    s.selectpartial("GC")
    s.addtogroup("GC")

    # draw silicon substrate;
    s.addrect()
    s.set("name", "substrate")
    s.set("material", material)
    s.set("x max", 30e-6)
    s.set("x min", -20e-6)
    s.set("y", -1 * (box_height + 0.5 * substrate_height))
    s.set("y span", substrate_height)
    s.set("alpha", 0.2)

    s.addrect()
    # draw burried oxide;
    s.set("name", "BOX")
    s.set("material", material_clad)
    s.set("x max", 30e-6)
    s.set("x min", -20e-6)
    s.set("y min", -box_height)
    s.set("y max", clad_height)
    s.set("override mesh order from material database", True)
    s.set("mesh order", 3)
    s.set("alpha", 0.3)

    s.addrect()
    # draw waveguide;
    s.set("name", "WG")
    s.set("material", material)
    s.set("x min", -20e-6)
    s.set("x max", gc_xmin)
    s.set("y min", 0)
    s.set("y max", wg_height)

    return dict(session=s)


def sparameters(
    session=None,
    draw_function=gc2d,
    filepath=None,
    dirpath=CONFIG["workspace"],
    overwrite=False,
    **kwargs,
):
    """Draws and Run Sparameter sweep
    returns early if filepath_json exists and overwrite flag is False

    Args:
        session
        draw_function:
        dirpath: where to store all the simulation files
        filepath: where to store a copy of the Sparameters
        overwrite: run even if simulation exists

    Kwargs:
        period: 0.66e-6 (m)
        ff: 0.5 fill factor
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
        wavelength_span=0.3e-6
        gc_xmin=-3e-6,
        fiber_angle_deg=20,
        mesh_accuracy=3,  # FDTD simulation mesh accuracy
        frequency_points=100,  # global frequency points
        simulation_time=1000e-15,  # maximum simulation time [s]
        base_fsp_path=str(CONFIG["grating_coupler_2D"]),

    """

    function_name = draw_function.__name__
    filename = get_function_name(function_name, **kwargs)

    dirpath = pathlib.Path(dirpath) / function_name
    dirpath.mkdir(exist_ok=True)
    filepath = dirpath / filename
    filepath_sim_settings = filepath.with_suffix(".settings.json")
    filepath_json = filepath.with_suffix(".json")
    filepath_fsp = str(filepath.with_suffix(".fsp"))
    filepath_sp = str(filepath.with_suffix(".dat"))

    if filepath_json.exists() and not overwrite:
        return json.loads(open(filepath_json).read())

    s = session
    simdict = draw_function(session=s, **kwargs)
    s.save(filepath_fsp)
    s.runsweep("S-parameters")

    sp = s.getsweepresult("S-parameters", "S parameters")
    s.exportsweep("S-parameters", filepath_sp)
    print(f"wrote sparameters to {filepath_sp}")

    if filepath:
        s.exportsweep("S-parameters", filepath)
        print(f"wrote sparameters to {filepath}")

    keys = [key for key in sp.keys() if key.startswith("S")]
    ra = {f"{key}a": list(np.unwrap(np.angle(sp[key].flatten()))) for key in keys}
    rm = {f"{key}m": list(np.abs(sp[key].flatten())) for key in keys}

    results = {"wavelength_nm": list(sp["lambda"].flatten() * 1e9)}
    results.update(ra)
    results.update(rm)
    with open(filepath_json, "w") as f:
        json.dump(results, f)
    settings = simdict.get("settings")
    if settings:
        with open(filepath_sim_settings, "w") as f:
            json.dump(settings, f)
    return results


def plot(results, logscale=True, keys=None):
    """plots Sparameters"""
    r = results
    w = r["wavelength_nm"]

    if keys:
        assert isinstance(keys, list)
        for key in keys:
            assert key in r, f"{key} not in {r.keys()}"
    else:
        keys = [key for key in r.keys() if key.startswith("S") and key.endswith("m")]

    for key in keys:
        if logscale:
            y = 20 * np.log10(r[key])
        else:
            y = r[key]

        plt.plot(w, y, label=key[:-1])
    plt.legend()
    plt.xlabel("wavelength (nm)")


if __name__ == "__main__":
    import lumapi

    s = lumapi.FDTD()
    # d = gc(session=s)
    results = sparameters(session=s)
    plot(results)

    # print(r)
