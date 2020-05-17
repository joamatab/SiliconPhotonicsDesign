import json

import jinja2

from pylum.autoname import autoname
from pylum.config import CONFIG

settings = dict(
    period=0.66e-6,
    ff=0.5,
    n_gratings=50,
    wg_height=220e-9,
    etch_depth=70e-9,
    box_height=2e-6,
    clad_height=2e-6,
    substrate_height=2e-6,
    material="Si (Silicon) - Dispersive & Lossless",
    wg_width=500e-9,
    polarization="TE",
    wavelength=1550e-9,
    gc_position=4.5e-6,
    fiber_angle_deg=20,
    draw_source_script_name="GC_setup_Gaussian",
    sweep_variable="period",
    sweep_start=0.62e-6,
    sweep_stop=0.7e-6,
    sweep_points=5,
)

sweep_variables = [
    "period",
    "ff",
    "Position",
    "theta0",
    "thick_BOX",
    "thick_Clad",
    "thick_Si",
    "etch_depth",
]
draw_source_script_names = ["GC_setup_Gaussian", "GC_setup_fibre"]


@autoname
def sweep(**kwargs):
    """ returns a dictionary with scripts for a grating coupler sweep

    Args:
        period: 0.66e-6
        ff: 0.5
        n_gratings: 50
        wg_height: 220e-9
        etch_depth: 70e-9
        box_height: 2e-6
        clad_height: 2e-6
        substrate_height: 2e-6
        material: Si (Silicon) - Dispersive & Lossless"
        wg_width: 500e-9
        polarization: TE"
        wavelength: 1550e-9
        gc_position: 4.5e-6
        fiber_angle_deg: 20
        draw_source_script_name: GC_setup_Gaussian"
        sweep_variable: period"
        sweep_start: 0.62e-6
        sweep_stop: 0.7e-6
        sweep_points: 5

    """
    if "sweep_variable" in kwargs:
        assert (
            kwargs.get("sweep_variable") in sweep_variables
        ), f"sweep_variable {kwargs.get('sweep_variable')} not in {sweep_variables}"
    if "draw_source_script_name" in kwargs:
        assert (
            kwargs.get("draw_source_script_name") in draw_source_script_names
        ), f"draw_source_script_name {kwargs.get('draw_source_script_name')} not in {draw_source_script_names}"

    s = settings.copy()
    s.update(**kwargs)

    template = jinja2.Template(open(CONFIG["grating_coupler"] / "GC_init.lsf").read())
    init = template.render(**s)

    template = jinja2.Template(open(CONFIG["grating_coupler"] / "GC_sweeps.lsf").read())
    GC_sweeps = template.render(**s)

    materials = open(CONFIG["materials"]).read()
    GC_draw = open(CONFIG["grating_coupler"] / "GC_draw.lsf").read()
    GC_setup_Gaussian = open(CONFIG["grating_coupler"] / "GC_setup_Gaussian.lsf").read()
    main = "\n".join(["GC_init;", "GC_sweeps;"])

    return {
        "GC_init.lsf": init,
        "GC_sweeps.lsf": GC_sweeps,
        "materials.lsf": materials,
        "GC_draw.lsf": GC_draw,
        "GC_setup_Gaussian.lsf": GC_setup_Gaussian,
        "main.lsf": main,
        "settings.json": json.dumps(s),
    }


@autoname
def sparameters(**kwargs):
    """ returns a dictionary with scripts for calculating the Sparameters of a grating coupler

    Args:
        period: 0.66e-6
        ff: 0.5
        n_gratings: 50
        wg_height: 220e-9
        etch_depth: 70e-9
        box_height: 2e-6
        clad_height: 2e-6
        substrate_height: 2e-6
        material: Si (Silicon) - Dispersive & Lossless"
        wg_width: 500e-9
        polarization: TE"
        wavelength: 1550e-9
        gc_position: 4.5e-6
        fiber_angle_deg: 20
        draw_source_script_name: GC_setup_Gaussian"
        sweep_variable: period"
        sweep_start: 0.62e-6
        sweep_stop: 0.7e-6
        sweep_points: 5
    """
    d = sweep(**kwargs)
    d.pop("GC_sweeps.lsf")
    d["main.lsf"] = "\n".join(["GC_init;", "GC_S_extraction;"])
    d["GC_S_extraction.lsf"] = open(
        CONFIG["grating_coupler"] / "GC_S_extraction.lsf"
    ).read()
    d["GC_setup_fibre.lsf"] = open(
        CONFIG["grating_coupler"] / "GC_setup_fibre.lsf"
    ).read()
    d[
        "main.py"
    ] = """

import pathlib
import json
import lumapi


dirpath = pathlib.Path(__file__).parent.absolute()

s = lumapi.FDTD()
s.cd(str(dirpath))
s.eval("main;")

d = {k: list(abs(s.getv(k).flatten())) for k in ["S11", "S12", "S21", "S22", "f"]}

with open(dirpath / "GC_sparameters.json", "w") as f:
    f.write(json.dumps(d))

    """
    return d


def _demo_sweep():
    import pylum

    scripts = sweep(
        sweep_variable="thick_Si",
        sweep_start=205e-9,
        sweep_stop=240e-9,
        sweep_points=3,
    )
    pylum.write_scripts(scripts)


def test_sweep(data_regression):
    data_regression.check(sweep())


def test_sparameters(data_regression):
    data_regression.check(sparameters())


def sparameters_te():
    """ for gdsfactory default TE grating """
    return sparameters(fiber_angle_deg=15, period=682e-9, ff=343 / 682)


if __name__ == "__main__":
    import pylum

    scripts = sweep(
        sweep_variable="thick_Si",
        sweep_start=205e-9,
        sweep_stop=240e-9,
        sweep_points=3,
    )
    scripts = sparameters()

    scripts = sparameters_te()
    pylum.write_scripts(scripts)

    # print(scripts['main.py'])
    # print(scripts["dirpath"])
    # print(scripts)
    # pylum.run_fdtd(scripts)
