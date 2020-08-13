""" draw waveguide bend. calculate bend loss
"""
import matplotlib.pyplot as plt
import numpy as np

from pylum.autoname import autoname
from pylum.waveguide import waveguide


@autoname
def waveguide_bend(radius=np.array([2, 5]) * 1e-6, session=None, **kwargs):
    """ computes bend loss for waveguide bend radius

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
        material_wg: "si"
        material_wafer: "si"
        material_clad: "sio2"
        material_box: "sio2"
        wavelength: 1550e-9
        mesh_size: 10e-9
        modes: 4

    """
    s = waveguide(session=session, **kwargs)
    if 0 not in radius:
        radius = list(radius)
        radius.insert(0, 0)

    neff = np.zeros_like(radius)
    loss_dB_m = np.zeros_like(radius)
    loss_per_bend = np.zeros_like(radius)
    power_coupling = np.zeros_like(radius)

    for i, r in enumerate(radius):
        if r > 0:
            s.setanalysis("bent waveguide", 1)
            s.setanalysis("bend radius", r)
        else:
            s.setanalysis("bent waveguide", 0)
        nn = s.findmodes()
        if nn > 0:
            neff[i] = abs(s.getdata("FDE::data::mode1", "neff").squeeze())
            loss_dB_m[i] = s.getdata("FDE::data::mode1", "loss")
            loss_per_bend[i] = loss_dB_m[i] * 2 * np.pi * r / 4
            s.copydcard("mode1", f"radius{r}")

            # Perform mode-overlap calculations between the straight and bent waveguides
            if r > 0:
                out = s.overlap("::radius0", f"::radius{r}").squeeze()
                power_coupling[i] = out[1]  # power coupling

    loss = -10 * np.log10(
        power_coupling ** 2
    )  # 2X couplings per 90 degree bend vs radius (^2 for two)

    return dict(
        session=s,
        neff=neff,
        radius_all=radius,
        radius=radius[1:],
        loss=loss[1:],
        loss_dB_m=loss_dB_m[1:],
        loss_per_bend=loss_per_bend[1:],
    )


if __name__ == "__main__":
    import lumapi

    s = lumapi.MODE()
    d = waveguide_bend(session=s)
