import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np


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
    gc_xmin=0,
    fiber_position=4.5e-6,
    fiber_angle_deg=20,
    wl_span=0.3e-6,  # wavelength span
    mesh_accuracy=3,  # FDTD simulation mesh accuracy
    frequency_points=100,  # global frequency points
    simulation_time=1000e-15,  # maximum simulation time [s]
    core_index=1.4682,
    cladding_index=1.4629,
    core_diameter=8.2e-6,
    cladding_diameter=100e-6,
    d=0.2e-6,
):

    import lumapi

    s = session or lumapi.FDTD(hide=False)
    s.newproject()
    s.selectall()
    s.deleteall()

    gap = period * (1 - ff)
    # etched region of the grating

    s.addrect()
    s.set("name", "GC_base")
    s.set("material", material)
    s.set("x max", (n_gratings + 1) * period)
    s.set("x min", gc_xmin)
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

    # add simulation region;
    s.addfdtd(
        dimension="2D",
        x_max=15e-6,
        x_min=-3.5e-6,
        y_min=-(box_height + 0.2e-6),
        y_max=clad_height + 2e-6,
        mesh_accuracy=mesh_accuracy,
        simulation_time=simulation_time,
    )

    # add waveguide mode source;
    s.addmode()
    s.set("name", "waveguide_source")
    s.set("x", -3e-6)
    s.set("y", 0.5 * wg_height)
    s.set("y span", 2e-6)
    s.set("direction", "Forward")
    s.set("use global source settings", True)
    s.set("enabled", False)

    # add fibre;
    theta = np.arcsin(np.sin(fiber_angle_deg * np.pi / 180) / core_index) * 180 / np.pi
    r1 = core_diameter / 2
    r2 = cladding_diameter / 2
    span = 15 * r1
    if theta > 89:
        theta = 89
    if theta < -89:
        theta = -89

    thetarad = theta * np.pi / 180
    L = 20e-6 / np.cos(thetarad)

    V1 = [
        (-r1 / np.cos(thetarad), 0),
        (r1 / np.cos(thetarad), 0),
        (r1 / np.cos(thetarad) + L * np.sin(thetarad), L * np.cos(thetarad)),
        (-r1 / np.cos(thetarad) + L * np.sin(thetarad), L * np.cos(thetarad)),
    ]

    V2 = [
        (-r2 / np.cos(thetarad), 0),
        (r2 / np.cos(thetarad), 0),
        (r2 / np.cos(thetarad) + L * np.sin(thetarad), L * np.cos(thetarad)),
        (-r2 / np.cos(thetarad) + L * np.sin(thetarad), L * np.cos(thetarad)),
    ]

    v1 = s.matrix(4, 2)
    v2 = s.matrix(4, 2)

    for i in range(4):
        for j in range(2):
            v1[i][j] = V1[i][j]
            v2[i][j] = V2[i][j]

    s.addpoly()
    s.set("name", "fibre_core")
    s.set("x", 0)
    s.set("y", 0)
    s.set("vertices", v1)
    s.set("index", core_index)

    s.addpoly()
    s.set("name", "fibre_cladding")
    s.set("override mesh order from material database", 1)
    s.set("mesh order", 3)
    s.set("x", 0)
    s.set("y", 0)
    s.set("vertices", v2)
    s.set("index", cladding_index)

    s.addmode()
    s.set("name", "fibre_mode")
    s.set("injection axis", "y-axis")
    s.set("direction", "Backward")
    s.set("use global source settings", 1)
    s.set("theta", -theta)
    s.set("x span", span)
    s.d = 0.4e-6
    s.set("x", d * np.sin(thetarad))
    s.set("y", d * np.cos(thetarad))
    s.set("rotation offset", abs(span / 2 * np.tan(thetarad)))

    s.addpower()
    s.set("name", "fibre_top")
    s.set("x span", span)
    s.set("x", d * np.sin(thetarad))
    s.set("y", d * np.cos(thetarad))

    s.addmodeexpansion()
    s.set("name", "fibre_modeExpansion")
    s.set("monitor type", "2D Y-normal")
    s.setexpansion("fibre_top", "fibre_top")
    s.set("x span", span)
    s.set("x", d * np.sin(thetarad))
    s.set("y", d * np.cos(thetarad))
    s.set("theta", -theta)
    s.set("rotation offset", abs(span / 2 * np.tan(thetarad)))
    s.set("override global monitor settings", False)

    s.selectpartial("fibre")
    s.addtogroup("fibre")
    s.select("fibre::fibre_modeExpansion")
    s.setexpansion("fibre_top", "::model::fibre::fibre_top")

    s.unselectall()
    s.select("fibre")
    s.set("x", fiber_position)
    s.set("y", clad_height + 1e-6)

    s.addpower()
    # add monitor;
    s.set("name", "T")
    s.set("monitor type", "2D X-normal")
    s.set("x", -2.8e-6)
    s.set("y", 0.5 * wg_height)
    s.set("y span", 1e-6)

    s.addmodeexpansion()  # add waveguide mode expansion monitor
    s.set("name", "waveguide")
    s.set("monitor type", "2D X-normal")
    s.setexpansion("T", "T")
    s.set("x", -2.9e-6)
    s.set("y", 0.5 * wg_height)
    s.set("y span", 1e-6)

    if polarization == "TE":
        s.select("fibre::fibre_mode")
        s.set("mode selection", "fundamental TM")
        s.select("fibre::fibre_modeExpansion")
        s.set("mode selection", "fundamental TM")
        s.select("waveguide_source")
        s.set("mode selection", "fundamental TM")
        s.select("waveguide")
        s.set("mode selection", "fundamental TM")
    else:
        s.select("fibre::fibre_mode")
        s.set("mode selection", "fundamental TE")
        s.select("fibre::fibre_modeExpansion")
        s.set("mode selection", "fundamental TE")
        s.select("waveguide_source")
        s.set("mode selection", "fundamental TE")
        s.select("waveguide")
        s.set("mode selection", "fundamental TE")

    # global properties
    s.setglobalmonitor("frequency points", frequency_points)
    s.setglobalmonitor("use wavelength spacing", 1)
    s.setglobalmonitor("use source limits", 1)
    s.setglobalsource("center wavelength", wl)
    s.setglobalsource("wavelength span", wl_span)

    s.save("GC_fibre")

    #########################
    # Compute Sparameters
    #########################

    s.addport()  # fibre port
    # p = "FDTD::ports::port 1"
    s.set("injection axis", "y-axis")
    s.set("x", d * np.sin(thetarad))
    s.set("y", d * np.cos(thetarad) + 3)
    s.set("x span", span)
    s.set("theta", -theta)
    s.set("rotation offset", abs(span / 2 * np.tan(thetarad)))

    s.addport()  # waveguide
    # p = "FDTD::ports::port 2"
    s.set("injection axis", "x-axis")
    s.set("x", -2.9e-6)
    s.set("y", 0.5 * wg_height)
    s.set("y span", 1e-6)

    return dict(session=s)


def run(session, filepath="grating"):
    s = session
    filepath = pathlib.Path(filepath)
    filepath_json = filepath.with_suffix(".json")
    filepath_sp = str(filepath.with_suffix(".dat"))
    # filepath_sim_settings = filepath.with_suffix(".settings.json")
    # filepath_fsp = str(filepath.with_suffix(".fsp"))
    # s.save(filepath_fsp)
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
    d = gc(session=s)
    # results = run(session=d['session'])
    # plot(results)

    # print(r)
