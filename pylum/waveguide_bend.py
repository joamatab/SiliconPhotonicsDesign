"""
- draw waveguide bend
- calculate bend loss
- plot bend loss vs radius
"""
import matplotlib.pyplot as plt
import numpy as np

from pylum.autoname import autoname
from pylum.waveguide import waveguide


@autoname
def waveguide_bend(radius=np.array([3, 5, 10]) * 1e-6, session=None, **kwargs):
    """Computes bend loss for waveguide bend radius.

    Bend losses are caused by:
    - radiation (absorbed by PML)
    - propagation loss
    - 2 mode missmatchs from the radial to straight and back to radial

    Args:
        radius: waveguide bend radius (m)
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

    Returns:
        session: lumapi.MODE session
        neff: bend effective index iterable (includes zero)
        radius_all: bend radius iterable (includes zero)
        radius: bend radius (m) iterable
        loss: mode missmatch loss per bend
        loss_dB_m: propagation loss
        loss_per_bend: total propagation loss

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

    loss_mode = -10 * np.log10(
        power_coupling[1:] ** 2
    )  # 2X couplings per 90 degree bend vs radius (^2 for two)
    loss_radiation = loss_per_bend[1:] - loss_per_bend[0]
    loss_propagation = (
        2 * 100 * 2 * np.pi * np.array(radius[1:]) / 4
    )  # quarter turn propagation (assuming 2dB/cm)

    return dict(
        session=s,
        neff=neff,
        radius=radius[1:],
        loss_mode=loss_mode,
        loss_propagation=loss_propagation,
        loss_radiation=loss_radiation,
    )


def plot_waveguide_bend_loss(d):
    """bend loss (propagation and mode missmatch) for different bend radius
    values are loaded from `waveguide_bend_loss` dictionary d
    """
    f, ax = plt.subplots()
    plt.plot(
        np.array(d["radius"]) * 1e6, abs(d["loss_mode"]), "o-", label="mode missmatch"
    )
    plt.plot(
        np.array(d["radius"]) * 1e6,
        abs(d["loss_propagation"]),
        "o-",
        label="propagation",
    )
    plt.plot(
        np.array(d["radius"]) * 1e6, abs(d["loss_radiation"]), "o-", label="radiation"
    )
    plt.xlabel("bend radius (um)")
    plt.ylabel("loss (dB)")
    plt.legend()
    return f, ax


if __name__ == "__main__":
    # import lumapi
    # s = lumapi.MODE()

    d = waveguide_bend(cache=False)
    plot_waveguide_bend_loss(d)
    plt.show()
