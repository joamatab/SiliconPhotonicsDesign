""" DBR cell based on [Lumerical unit cell design](
https://support.lumerical.com/hc/en-us/articles/360042304394-Bragg-Grating-Initial-Design-with-FDTD)

We extract kappa from a DRB unit cell
"""
import numpy as np
import pp
from pp.components.dbr import dbr_cell
from scipy.constants import speed_of_light
from tqdm import tqdm

from pylum.autoname import autoname
from pylum.config import CONFIG
from pylum.config import materials


def dbr_gds_sweep(deltas, **kwargs):
    """ simulate DBR unit cell in FDTD from a gdsfactory DBR

    Args:
        deltas: teeth have [width + delta/2, width - delta/2]
        session: lumapi.FDTD session
        run: runs or only draws
        material_wg: 'si' or 'sin'
        wg_height: 220e-9
        width: 500e-9
        sim_time: depends on grating strength
        with_slab: adds rib slab
        is_sinusoidal: makes grating sinusoidal
    """
    deltas = np.array(deltas)
    w0 = np.zeros_like(deltas)
    bw = np.zeros_like(deltas)

    for i, delta in tqdm(enumerate(deltas)):
        d = dbr_gds(delta=delta, **kwargs)
        w0[i] = d["wavelength0"]
        bw[i] = d["bandwidth"]

    session = d.get("session", None)
    return dict(session=session, dw=deltas, w0=w0, bw=bw)


def unity(x, **kwargs):
    return x


@autoname
def dbr_gds(
    session=None,
    run=True,
    fsp=str(CONFIG["dbr2"]),
    gdspath=None,
    material_wg="si",
    material_clad="sio2",
    wg_height=220e-9,
    period=318e-9,
    width=500e-9,
    delta=80e-9,
    slab_height=0,
    sim_time=1e-15 * (2500),
    width_margin=1e-6,
    height_margin=1e-6,
    with_slab=False,
    gdsfunction=unity,
    cell_name=None,
    **kwargs,
):
    """ simulate DBR unit cell in FDTD from gdsfactory

    Args:
        session: lumapi.FDTD session
        run: runs or only draws
        material_wg: 'si' or 'sin'
        material_clad: 'sio2'
        wg_height: 220e-9
        width: 500e-9
        delta: delta width
        sim_time: depends on grating strength

    """
    l1 = period / 2 * 1e6
    l2 = period / 2 * 1e6
    w1 = (width - delta / 2) * 1e6
    w2 = (width + delta / 2) * 1e6
    layer = (1, 0)

    if gdspath is None:
        c = pp.c.dbr(w1=w1, w2=w2, l2=l2, l1=l1, n=3)
        c.x = 0
        c.flatten()
        gdspath = pp.write_gds(c)

    cell_name = cell_name or c.name

    gdspath = gdsfunction(gdspath, **kwargs)

    if material_wg not in materials:
        raise ValueError(f"{material_wg} not in {list(materials.keys())}")

    import lumapi

    s = session or lumapi.FDTD(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()

    # x_min = -period / 2
    # x_max = period / 2
    y_max = width / 2 + delta / 2 + width_margin
    y_min = -y_max
    z_min = -height_margin
    z_max = wg_height + height_margin

    x_span = period
    y_span = y_max - y_min
    z_span = z_max - z_min

    s.load(fsp)
    s.switchtolayout()

    # s.addrect(
    #     x_min=x_min,
    #     x_max=x_max,
    #     y_min=y_min,
    #     y_max=y_max,
    #     z_min=z_min,
    #     z_max=z_max,
    #     index=1.5,
    #     name="clad",
    # )
    # s.setnamed("clad", "material", materials[material_clad])
    s.select("bragg")
    s.delete()

    s.setnamed("::model", "ax", period)
    s.setnamed("::model", "width", width)
    s.setnamed("::model", "delta", delta)
    s.setnamed("::model", "slab", with_slab)
    s.setnamed("slab", "z span", slab_height)

    # s.addfdtd(
    #     dimension="3D",
    #     x_min=x_min,
    #     x_max=x_max,
    #     y_min=y_min,
    #     y_max=y_max,
    #     z_min=z_min,
    #     z_max=z_max,
    #     mesh_accuracy=mesh_accuracy,
    #     use_early_shutoff=True,
    # )
    # s.setnamed("FDTD", "simulation time", sim_time)

    silicon = f"GDS_LAYER_{layer[0]}:{layer[1]}"
    s.select(silicon)
    s.delete()
    s.gdsimport(str(gdspath), cell_name, f"{layer[0]}:{layer[1]}")

    s.setnamed(silicon, "z span", wg_height)
    s.setnamed(silicon, "material", materials[material_wg])

    s.setnamed("bandstructure", "x", 0)
    s.setnamed("bandstructure", "x span", x_span)
    s.setnamed("bandstructure", "y span", y_span)
    s.setnamed("bandstructure", "z span", z_span)

    d = dict(session=s)

    if run:
        s.run()

        r = s.getresult("bandstructure", "spectrum")
        fs = r["fs"]
        f = r["f"]
        d["wavelength"] = r["lambda"]

        peaks = s.findpeaks(fs, 2)
        c = speed_of_light
        w1 = c / f[int(peaks[0])]
        w2 = c / f[int(peaks[1])]
        d["wavelength0"] = (w1 + w2) / 2
        d["bandwidth"] = abs(w2 - w1)
        d["fs"] = fs
    return d


if __name__ == "__main__":
    d = dbr_gds(cache=False)
