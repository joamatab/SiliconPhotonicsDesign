import json
import pathlib

import h5py
import numpy as np

from pylum.config import CONFIG
from pylum.write_scripts import write_scripts


def loadmat(matlab_file_path="results.mat"):
    """ reads a dirpath or a matlab file path
    it can also accept a dict of scripts containing dirpath
    returns a dict with the results

    you have to make sure that in your scripts you save the results in resuls.mat
    """

    if not str(matlab_file_path).endswith(".mat"):
        dirpath = matlab_file_path.get("dirpath", write_scripts(matlab_file_path))
        matlab_file_path = dirpath / "results.mat"

    matlab_file_path = pathlib.Path(matlab_file_path)
    assert matlab_file_path.exists(), f"{matlab_file_path} does not exist"
    f = h5py.File(matlab_file_path, "r")

    d = {fi.name.strip("/"): fi[()] for fi in f.values() if hasattr(fi, "value")}
    strings = {
        fi.name.strip("/"): fi[()]
        for fi in f.values()
        if hasattr(fi, "value") and fi.dtype == "u2"
    }
    for k, v in strings.items():
        d[k] = "".join([chr(v[i][0]) for i in range(len(v))])

    return d


def write_dict(d, filepath="results.json"):
    """ convert dict to JSON """
    if not filepath.endswith(".mat"):
        filepath = CONFIG["workspace"] / filepath / "results.json"

    for k, v in d.items():
        if isinstance(v, np.array):
            d[k] = v.tolist()

    with open(filepath, "w") as f:
        f.write(json.dumps(d))


def test_loadmat():
    from pylum.grating_coupler import sparameters

    matlab_file_path = (
        CONFIG["repo_path"] / "workspace" / "grating_coupler_sweep" / "results.mat"
    )

    r = loadmat(matlab_file_path)
    # print(r)
    assert r


if __name__ == "__main__":
    # dirname = "grating_coupler_sweep2"
    # d = loadmat(dirname)
    # print(d["polarization"])
    # write_dict(d, dirname)
    test_loadmat()
