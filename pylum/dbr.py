""" DBR cell based on [Lumerical unit cell design](
https://support.lumerical.com/hc/en-us/articles/360042304394-Bragg-Grating-Initial-Design-with-FDTD)

We extract kappa from a DRB unit cell
"""
from pylum.autoname import autoname
from pylum.config import CONFIG
from pylum.config import materials


def draw(
    session=None,
    fsp=str(CONFIG["dbr"]),
    material_wg="si",
    wg_height=220e-9,
    w1=550e-9,
    w2=450e-9,
    n_sweep=8,
):
    """ draw DBR unit cell in FDTD
    """
    if material_wg not in materials:
        raise ValueError(f"{material_wg} not in {list(materials.keys())}")

    material_wg = materials[material_wg]

    import lumapi

    s = session if session is not None else lumapi.FDTD(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()

    s.load(fsp)
    s.setnamed("w1", "z span", wg_height)
    s.setnamed("w2", "z span", wg_height)
    s.setnamed("w1", "y span", w1)
    s.setnamed("w2", "y span", w2)
    s.setnamed("w1", "material", material_wg)
    s.setnamed("w2", "material", material_wg)
    s.setsweep("sweep", "number of points", n_sweep)
    return s


@autoname
def dbr(session=None, run=True, **kwargs):
    """ draw DBR unit cell in FDTD

    Args:
        session: lumapi.FDTD session
        material_wg: 'si' or 'sin'
        wg_height: 220e-9
        w1: 550e-9
        w2: 450e-9
    """
    s = draw(session=session, **kwargs)
    d = dict(session=s)

    if run:
        s.runsweep()
        d["w"] = s.getsweepdata("sweep", "w")
        d["kappa"] = s.getsweepdata("sweep", "kappa")
        d["bandwidth"] = s.getsweepdata("sweep", "bandwidth")

    return d


if __name__ == "__main__":
    d = dbr()
