import json
import pathlib

from pylum.autoname import get_function_name
from pylum.config import CONFIG
from pylum.gc import gc2d


def gc_sweep(
    session=None,
    draw_function=gc2d,
    dirpath=CONFIG["workspace"],
    overwrite=False,
    run=True,
    base_fsp_path=str(CONFIG["grating_coupler_2D_base"]),
    **kwargs
):
    """ grating coupler sweep

    grating_coupler_2D_base optimizes Transmission and does not calculate Sparameters
    """
    import lumapi

    function_name = draw_function.__name__ + "_sweep"
    filename = kwargs.pop("name", get_function_name(function_name, **kwargs))

    dirpath = pathlib.Path(dirpath) / function_name
    dirpath.mkdir(exist_ok=True)
    filepath = dirpath / filename
    filepath_sim_settings = filepath.with_suffix(".settings.json")
    filepath_json = filepath.with_suffix(".json")
    filepath_fsp = str(filepath.with_suffix(".fsp"))

    if filepath_json.exists() and not overwrite and run:
        return json.loads(open(filepath_json).read())

    s = session or lumapi.FDTD(hide=False)
    simdict = draw_function(session=s, base_fsp_path=base_fsp_path, **kwargs)
    s.save(filepath_fsp)
    if not run:
        return
    s.run()
    T = s.getresult("fom", "T")
    results = dict(wavelength_nm=list(T["lambda"].ravel() * 1e9), T=list(T["T"]))

    with open(filepath_json, "w") as f:
        json.dump(results, f)
    settings = simdict.get("settings")
    if settings:
        with open(filepath_sim_settings, "w") as f:
            json.dump(settings, f)
    return results


if __name__ == "__main__":
    import lumapi

    s = lumapi.FDTD()
    s = gc_sweep(session=s)
