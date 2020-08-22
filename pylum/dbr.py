""" DBR cell based on [Lumerical unit cell design](
https://support.lumerical.com/hc/en-us/articles/360042304394-Bragg-Grating-Initial-Design-with-FDTD)

We extract kappa from a DRB unit cell
"""
import numpy as np
from scipy.constants import speed_of_light
from tqdm import tqdm

from pylum.autoname import autoname
from pylum.config import CONFIG
from pylum.config import materials


@autoname
def dbr_sweep(deltas, **kwargs):
    """ simulate DBR unit cell in FDTD

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
        d = dbr(delta=delta, **kwargs)
        w0[i] = d["wavelength0"]
        bw[i] = d["bandwidth"]

    session = d.get("session", None)
    return dict(session=session, dw=deltas, w0=w0, bw=bw)


@autoname
def dbr(
    session=None,
    run=True,
    fsp=str(CONFIG["dbr2"]),
    material_wg="si",
    wg_height=220e-9,
    sim_time=1e-15 * (2500),
    period=318e-9,
    width=500e-9,
    delta=80e-9,
    with_slab=False,
    slab_height=90e-9,
    is_sinusoidal=False,
    material_wg_index=3.45,
):
    """ simulate DBR unit cell in FDTD

    Args:
        session: lumapi.FDTD session
        run: runs or only draws
        material_wg: 'si' or 'sin'
        wg_height: 220e-9
        width: 500e-9
        delta: delta width
        sim_time: depends on grating strength
        with_slab: adds rib slab
        is_sinusoidal: makes grating sinusoidal
        material_wg_index: index for waveguide if material does not exist in database
    """
    if material_wg not in materials:
        raise ValueError(f"{material_wg} not in {list(materials.keys())}")

    material_wg = materials[material_wg]

    with_slab = 1 if with_slab else 0
    is_sinusoidal = 1 if is_sinusoidal else 0

    import lumapi

    s = session or lumapi.FDTD(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()
    s.load(fsp)
    s.switchtolayout()

    if not s.materialexists(material_wg):
        material = s.addmaterial("Dielectric")
        s.setmaterial(material, "Refractive Index", material_wg_index)
        s.setmaterial(material, "name", material_wg)

    s.setnamed("::model", "ax", period)
    s.setnamed("::model", "width", width)
    s.setnamed("::model", "delta", delta)
    s.setnamed("::model", "slab", with_slab)
    s.setnamed("::model", "sinusoidal", is_sinusoidal)
    s.setnamed("bragg", "mat", material_wg)
    s.setnamed("bragg", "height", wg_height)
    s.setnamed("FDTD", "simulation time", sim_time)
    s.setnamed("slab", "z span", slab_height)

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
    d = dbr(cache=False)
