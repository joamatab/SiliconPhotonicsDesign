"""Compute and plot group and effective index over wavelength
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.constants import speed_of_light as c

from pylum.autoname import autoname
from pylum.waveguide import waveguide


@autoname
def waveguide_dispersion(
    waveguide_function=waveguide,
    wavelength=1.55e-6,
    mode_number=1,
    nmodes=5,
    wavelength_min=1.5e-6,
    session=None,
    **kwargs
):
    """Computes effective and group index over wavelength.

    Args:
        wavelength: 1550e-9
        mode_number: 1 for fundamental, 2 for 2nd order ...
        nmodes: number of modes
        wavelength_min: for sweeping wavelength
        session: lumapi.MODE Session (for debugging)
        wg_width: 500e-9
        wg_height: 220e-9
        slab_height: 0
        box_height: 2e-6
        clad_height: 2e-6
        margin_wg_height: 1e-6
        margin_wg_width: 2e-6
        substrate_height: 2e-6
        material_wg: "si"
        material_wafer: "si"
        material_clad: "sio2"
        material_box: "sio2"
        mesh_size: 10e-9
        modes: 4

    Returns:
        wavelengths: for detailed dispersion calculation
        neff: effective index iterable (includes zero)
        ng: group index

    """
    s = waveguide_function(session=session, wavelength=wavelength, **kwargs)

    s.run()
    s.setanalysis("wavelength", wavelength)
    s.findmodes()
    s.selectmode(mode_number)

    s.setanalysis("track selected mode", mode_number)
    s.setanalysis("number of test modes", nmodes)
    s.setanalysis("detailed dispersion calculation", 0)

    # This feature is useful for higher-order dispersion.
    s.setanalysis("stop wavelength", wavelength_min)
    s.frequencysweep()

    # perform sweep of wavelength and plot
    f = s.getdata("frequencysweep", "f")
    neff = s.getdata("frequencysweep", "neff")
    ng = c / s.getdata("frequencysweep", "vg")
    # f_vg = s.getdata("frequencysweep", "f_vg")

    wavelengths = c / f
    wavelengths = wavelengths.flatten()
    neff = abs(neff.flatten())
    ng = abs(ng.flatten())
    return dict(wavelengths=wavelengths, neff=neff, ng=ng)


def get_neff_ng(**kwargs):
    """returns the average group index for a particular waveguide"""
    d = waveguide_dispersion(**kwargs)
    return np.mean(d["neff"]), np.mean(d["ng"])


def wim_paper():
    """reproduce Yufei and Wim paper."""
    w0 = 470e-9
    h0 = 215e-9
    dwmax = 30e-9
    dhmax = 20e-9
    steps = 11
    dw = np.linspace(-dwmax, dwmax, steps)
    dh = np.linspace(-dhmax, dhmax, steps)
    print(dw * 1e9, dh * 1e9)
    print((dw + w0) * 1e9, (dh + h0) * 1e9)

    ngs = []
    neffs = []
    dws = []
    dhs = []

    for dwi in dw:
        for dhi in dh:
            # neff = np.random.rand()
            # ng = np.random.rand()
            neff, ng = get_neff_ng(wg_width=w0 + dwi, wg_height=h0 + dhi)

            neffs.append(neff)
            ngs.append(ng)
            dws.append(dwi)
            dhs.append(dhi)

    df = pd.DataFrame(dict(dw=dws, dh=dhs, neff=neffs, ng=ngs))
    df.to_csv("dw_dw.csv")
    plt.plot(neffs, ngs, "o")
    plt.xlabel("neff")
    plt.ylabel("ng")
    return neffs, ngs


def plot_waveguide_dispersion(d):
    """Waveguide effective index and group index
    values are loaded from `waveguide_ng` dictionary d
    """
    plt.figure()
    w = d["wavelengths"] * 1e9
    plt.plot(w[:-1], abs(d["neff"]))
    plt.xlabel("wavelengths (nm)")
    plt.ylabel("neff)")

    plt.figure()
    plt.plot(w, abs(d["ng"]))
    plt.xlabel("wavelengths (nm)")
    plt.ylabel("ng)")


if __name__ == "__main__":
    neffs, ngs = wim_paper()
    plt.show()

    # neff, ng = get_neff_ng(wg_width=440e-9)
    # print(neff)
    # print(ng)
    # d = waveguide_dispersion(wg_width=500e-9)
    # plot_waveguide_dispersion(d)
    # plt.show()
