import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np

from pylum.autoname import autoname
from pylum.config import CONFIG


@autoname
def gc(
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
    wl_span=0.3e-6,  # wavelength span
    mesh_accuracy=3,  # FDTD simulation mesh accuracy
    frequency_points=100,  # global frequency points
    simulation_time=1000e-15,  # maximum simulation time [s]
):
    import lumapi

    s = session or lumapi.FDTD(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()

    s.load(str(CONFIG["grating_coupler_2D"]))
    s.select("GC")
    s.delete()
    s.select("WG")
    s.delete()

    s.select("fiber")
    s.set("theta", fiber_angle_deg)

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
        s.set("y", 0.5 * wg_height)
        s.set("y span", wg_height)
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
    s.set("y", 0.11e-6)
    s.set("y span", wg_height)

    return dict(session=s)


def sparameters(
    session=None, draw_function=gc, dirpath=CONFIG["workspace"], **kwargs,
):

    s = session
    simdict = draw_function(session=s, **kwargs)
    settings = simdict.get("settings")

    dirpath = pathlib.Path(dirpath) / simdict["function_name"]
    dirpath.mkdir(exist_ok=True)
    filepath = dirpath / simdict["name"]
    filepath_sim_settings = filepath.with_suffix(".settings.json")
    filepath_json = filepath.with_suffix(".json")
    filepath_fsp = str(filepath.with_suffix(".fsp"))
    filepath_sp = str(filepath.with_suffix(".dat"))

    s.save(filepath_fsp)
    # s.run()
    # s.save(filepath_fsp)

    # if a sweep task named s-parameter sweep already exists, remove it
    s.deletesweep("s-parameter sweep")

    # add s-parameter sweep task
    s.addsweep(3)

    # un-check "Excite all ports" option
    s.setsweep("s-parameter sweep", "Excite all ports", 0)

    # use auto-symmetry to populate the S-matrix setup table
    s.setsweep("S sweep", "auto symmetry", True)

    # run s-parameter sweep
    s.runsweep("s-parameter sweep")

    # collect results
    # S_matrix = s.getsweepresult("s-parameter sweep", "S matrix")
    sp = s.getsweepresult("s-parameter sweep", "S parameters")

    # visualize results
    # s.visualize(S_matrix);
    # s.visualize(S_parameters);
    # s.visualize(S_diagnostic);

    # export S-parameter data to file named s_params.dat to be loaded in INTERCONNECT
    s.exportsweep("s-parameter sweep", filepath_sp)
    print(f"wrote sparameters to {filepath_sp}")

    keys = [key for key in sp.keys() if key.startswith("S")]

    ra = {f"{key}a": list(np.unwrap(np.angle(sp[key].flatten()))) for key in keys}
    rm = {f"{key}m": list(np.abs(sp[key].flatten())) for key in keys}

    results = {"wavelength_nm": list(sp["lambda"].flatten() * 1e9)}
    results.update(ra)
    results.update(rm)
    with open(filepath_json, "w") as f:
        json.dump(results, f)
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
