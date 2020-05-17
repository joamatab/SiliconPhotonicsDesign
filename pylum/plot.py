import matplotlib.pyplot as plt
import numpy as np

from pylum.loadmat import loadmat


def log(x):
    return 10 * np.log10(abs(x))


def unity(x):
    return x


def negative(x):
    return -x


def plot_grating_coupler_sweep_spectrum(matlab_file_path, function=log):
    """ plots spectrum from a grating coupler sweep simulation
    """
    d = loadmat(matlab_file_path)
    print(d.keys())

    for i in range(len(d["M_sweep"][0])):
        x = d["WL"][0] * 1e9
        y = function(d["M_T"][i])
        label = str(int(1e9 * d["M_sweep"][0][i]))
        plt.plot(x, y, label=label)

    plt.legend()


def plot_grating_coupler_sweep_center_wavelength(matlab_file_path, function=log):
    """ plots center wavelength from a grating coupler sweep simulation
    """
    d = loadmat(matlab_file_path)
    print(d.keys())

    N = len(d["M_sweep"][0])
    parameter = np.zeros(N)
    w = np.zeros(N)

    for i in range(N):
        parameter[i] = 1e9 * d["M_sweep"][0][i]
        x = d["WL"][0] * 1e9
        y = function(d["M_T"][i])
        index = np.argmax(y)
        w[i] = x[index]

    plt.figure()
    plt.xlabel("waveguide height (nm)")
    plt.ylabel("center wavelength (nm)")
    plt.plot(parameter, w, ".")
    plt.legend()


def plot_grating_coupler_sweep_efficiency(matlab_file_path, function=log):
    """ plots coupling efficiency from a grating coupler sweep simulation
    """
    d = loadmat(matlab_file_path)
    print(d.keys())

    N = len(d["M_sweep"][0])
    parameter = np.zeros(N)
    efficiency = np.zeros(N)

    for i in range(N):
        parameter[i] = 1e9 * d["M_sweep"][0][i]
        # x = d["WL"][0] * 1e9
        y = function(d["M_T"][i])
        efficiency[i] = np.max(y)

    plt.figure()
    plt.xlabel("waveguide height (nm)")
    plt.ylabel("Eficiency (dB)")
    plt.plot(parameter, efficiency, ".")
    plt.legend()


def _plot_sparameters(matlab_file_path, keys=None):
    """ plots Nport Sparameters,
    Needs work
    """
    d = loadmat(matlab_file_path)
    keys = keys or [key for key in d.keys() if key.startswith("S")]
    # nports = np.sqrt((len(d["Sdata"]) - 1) / 2)
    smod = {
        f"S{i+1}": 10 * np.log10(np.array(s)) for i, s in enumerate(d["Sdata"][1::2])
    }

    x = 3e8 / d["f"] * 1e9

    for i, key in enumerate(keys):
        # y = d[key + "m"]
        y = smod[f"S{i+1}"]
        plt.plot(x, y, label=key)

    plt.xlabel("wavelength (nm)")
    plt.ylabel("|S| (dB)")
    plt.legend()


def plot_sparameters_gc(
    matlab_file_path, keys=["s12", "s21", "s11", "s22"], function=log
):
    """ plots grating coupler Sparameters
    """
    d = loadmat(matlab_file_path)

    x = 3e8 / d["f"].ravel() * 1e9

    for key in keys:
        y = function(d[key + "m"].ravel())
        plt.plot(x, y, label=key)

    plt.xlabel("wavelength (nm)")
    plt.ylabel("S")
    plt.legend()


if __name__ == "__main__":
    # plot_grating_coupler_sweep("grating_coupler_sweep2")
    # plot_grating_coupler_sweep_center_wavelength("grating_coupler_sweep2")
    # plot_grating_coupler_sweep_efficiency("grating_coupler_sweep2")

    from pylum.grating_coupler import sparameters

    scripts = sparameters()
    plot_sparameters_gc(scripts)
    plt.show()
