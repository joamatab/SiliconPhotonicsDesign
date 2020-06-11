""" grating coupler 2D Lumerical FDTD simulation

You can specify any grating coupler geomery and simulation parameters for a 2D FDTD Lumerical simulation.

There is 2 ways to define a grating coupler:

- Define period, fill_factor and n_gratings
- Define a list of (gap, width) for the grating teeth
"""
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
    gap_width_list=None,
    n_gratings=50,
    wg_height=220e-9,
    etch_depth=70e-9,
    box_height=2e-6,
    clad_height=2e-6,
    substrate_height=2e-6,
    material="Si (Silicon) - Palik",
    material_clad="SiO2 (Glass) - Palik",
    gc_xmin=-3e-6,
    fiber_angle_deg=20,
    wavelength=1550e-9,
    wavelength_span=300e-9,  # wavelength span
    base_fsp_path=str(CONFIG["grating_coupler_2D"]),
):
    """ draw 2D grating coupler

    gap_width_list overrides (period, ff and n_gratings)

    """
    import lumapi

    assert ff < 1, f"fill factor {ff:.3f} is the ratio of period/maxHeigh"

    s = session or lumapi.FDTD(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()

    s.load(base_fsp_path)

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
    gap_width_list = gap_width_list or [(gap, ff * period)] * n_gratings
    xmin = gc_xmin

    for gap, width in gap_width_list:
        s.addrect()
        s.set("name", "GC_tooth")
        s.set("material", material)
        s.set("y min", 0)
        s.set("y max", wg_height)
        s.set("x min", xmin + gap)
        s.set("x max", xmin + gap + width)
        xmin += gap + width
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


def load_sparameters_from_kwargs(
    draw_function=gc2d, dirpath=CONFIG["workspace"], **kwargs
):
    """ returns dict with grating coupler Sparameters """
    function_name = draw_function.__name__
    filename = get_function_name(function_name, **kwargs)

    dirpath = pathlib.Path(dirpath) / function_name
    filepath = dirpath / filename
    filepath_json = filepath.with_suffix(".json")

    return json.loads(open(filepath_json).read())


def test_load(data_regression):
    simdict = load_sparameters_from_kwargs()
    data_regression.check(simdict)


def load_sparameters(filepath_json):
    """ returns dict with grating coupler Sparameters """
    filepath_json = pathlib.Path(filepath_json)
    if filepath_json.suffix == ".dat":
        filepath_json = filepath_json.with_suffix(".json")

    assert filepath_json.exists(), f"{filepath_json} does not exist"
    return json.loads(open(filepath_json).read())


def write_sparameters(
    session=None,
    draw_function=gc2d,
    dirpath=CONFIG["workspace"],
    overwrite=False,
    run=True,
    **kwargs,
):
    """Write grating coupler Sparameters
    returns early if filepath_sp exists and overwrite flag is False

    Returns:
        Sparameters filepath in interconnect format

    Args:
        session
        draw_function:
        dirpath: where to store all the simulation files
        overwrite: run even if simulation exists

    Kwargs:
        period (m): 0.66e-6
        ff: 0.5 fill factor
        n_gratings: 50
        gap_width_list: [(gap1, width1), (gap2, width2) ...] overrides (period, ff and n_gratings)
        wg_height: 220e-9
        etch_depth: 70e-9
        box_height: 2e-6
        clad_height: 2e-6
        substrate_height: 2e-6
        material: "Si (Silicon) - Palik"
        material_clad: "SiO2 (Glass) - Palik"
        wavelength: 1550e-9
        wavelength_span: 0.3e-6
        gc_xmin: 3e-6
        fiber_angle_deg: 20

    """
    import lumapi

    function_name = draw_function.__name__
    filename = get_function_name(function_name, **kwargs)

    dirpath = pathlib.Path(dirpath) / function_name
    dirpath.mkdir(exist_ok=True)
    filepath = dirpath / filename
    filepath_sim_settings = filepath.with_suffix(".settings.json")
    filepath_json = filepath.with_suffix(".json")
    filepath_fsp = filepath.with_suffix(".fsp")
    filepath_sp = filepath.with_suffix(".dat")

    if filepath_sp.exists() and not overwrite and run:
        return filepath_sp

    s = session or lumapi.FDTD(hide=False)
    simdict = draw_function(session=s, **kwargs)
    s.save(str(filepath_fsp))

    if not run:
        return filepath_sp

    s.runsweep("S-parameters")

    sp = s.getsweepresult("S-parameters", "S parameters")
    s.exportsweep("S-parameters", str(filepath_sp))
    print(f"wrote sparameters to {filepath_sp}")

    keys = [key for key in sp.keys() if key.startswith("S")]
    ra = {f"{key}a": list(np.unwrap(np.angle(sp[key].flatten()))) for key in keys}
    rm = {f"{key}m": list(np.abs(sp[key].flatten())) for key in keys}

    sp_dict = dict(wavelength_nm=list(sp["lambda"].flatten() * 1e9))
    sp_dict.update(ra)
    sp_dict.update(rm)
    with open(filepath_json, "w") as f:
        json.dump(sp_dict, f)
    settings = simdict.get("settings")
    if settings:
        with open(filepath_sim_settings, "w") as f:
            json.dump(settings, f)
    return filepath_sp


def plot(sp_dict, logscale=True, keys=None):
    """plots Sparameters dict"""
    r = sp_dict
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


def max_transmission(sp_dict, key="S12m"):
    return max(sp_dict[key])


def max_transmission_dB(sp_dict, key="S12m"):
    return 10 * np.log10(max(sp_dict[key]))


def max_transmission_wavelength(sp_dict, key="S12m"):
    """ returns wavelength for max transmission"""
    S = sp_dict[key]
    return sp_dict["wavelength_nm"][np.argmax(S)]


if __name__ == "__main__":
    # import lumapi

    # s = lumapi.FDTD()
    # d = gc(session=s)
    # sp_dict = sparameters(session=s)
    # plot(sp_dict)
    # print(r)

    r = load_sparameters_from_kwargs()

    print(r.keys())
