"""Draw waveguide with non dispersive materials.
"""


def waveguide_fixed_index(
    session=None,
    wg_width=500e-9,
    wg_height=220e-9,
    slab_height=0,
    box_height=2e-6,
    clad_height=2e-6,
    margin_wg_height=1e-6,
    margin_wg_width=2e-6,
    nclad=1.44,
    nbox=1.44,
    nwg=3.47,
    nwafer=3.47,
    wavelength=1550e-9,
    mesh_size=10e-9,
    modes=4,
):
    """Draws a waveguide 2D mode solver with non dispersive materials.

    Args:
        session: None
        wg_width: 500e-9
        wg_height: 220e-9
        slab_height: 0
        box_height: 2e-6
        clad_height: 2e-6
        margin_wg_height: 1e-6
        margin_wg_width: 2e-6
        substrate_height: 2e-6
        nwg: "si"
        nwafer: "si"
        nclad: "sio2"
        nbox: "sio2"
        wavelength: 1550e-9
        mesh_size: 10e-9
        modes: 4

    """
    material = "<Object defined dielectric>"

    import lumapi

    s = session or lumapi.MODE(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()

    xmin = -2e-6
    xmax = 2e-6
    zmin = -margin_wg_height
    zmax = wg_height + margin_wg_height
    dy = 2 * margin_wg_width + wg_width

    s.addrect()
    s.set("name", "clad")
    s.set("material", material)
    s.set("index", nclad)
    s.set("z min", 0)
    s.set("z max", clad_height)
    s.set("y", 0)
    s.set("y span", dy)
    s.set("x min", xmin)
    s.set("x max", xmax)
    s.set("override mesh order from material database", 1)
    s.set(
        "mesh order", 3
    )  # similar to "send to back", put the cladding as a background.
    s.set("alpha", 0.05)

    s.addrect()
    s.set("name", "box")
    s.set("material", material)
    s.set("index", nbox)
    s.set("z min", -box_height)
    s.set("z max", 0)
    s.set("y", 0)
    s.set("y span", dy)
    s.set("x min", xmin)
    s.set("x max", xmax)
    s.set("alpha", 0.05)

    s.addrect()
    s.set("name", "wafer")
    s.set("material", material)
    s.set("index", nwafer)
    s.set("z min", -box_height - 2e-6)
    s.set("z max", -box_height)
    s.set("y", 0)
    s.set("y span", dy)
    s.set("x min", xmin)
    s.set("x max", xmax)
    s.set("alpha", 0.1)

    s.addrect()
    s.set("name", "waveguide")
    s.set("material", material)
    s.set("index", nwg)
    s.set("z min", 0)
    s.set("z max", wg_height)
    s.set("y", 0)
    s.set("y span", wg_width)
    s.set("x min", xmin)
    s.set("x max", xmax)

    if slab_height > 0:
        s.addrect()
        s.set("name", "waveguide")
        s.set("material", material)
        s.set("index", nwg)
        s.set("z min", 0)
        s.set("z max", slab_height)
        s.set("y", 0)
        s.set("y span", dy)
        s.set("x min", xmin)
        s.set("x max", xmax)

    s.addfde()
    s.set("solver type", "2D X normal")
    s.set("x", 0)
    s.set("z max", zmax)
    s.set("z min", zmin)
    s.set("y", 0)
    s.set("y span", dy)
    s.set("wavelength", wavelength)
    s.set("solver type", "2D X normal")
    s.set("y min bc", "PML")
    s.set("y max bc", "PML")

    # radiation loss
    s.set("z min bc", "metal")
    s.set("z max bc", "metal")
    s.set("define y mesh by", "maximum mesh step")
    s.set("dy", mesh_size)
    s.set("define z mesh by", "maximum mesh step")
    s.set("dz", mesh_size)
    s.set("number of trial modes", modes)
    s.cleardcard()

    return s


if __name__ == "__main__":
    import lumapi

    s = lumapi.MODE()
    s = waveguide_fixed_index(session=s)
