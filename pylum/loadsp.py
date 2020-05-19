import pathlib
import re

import numpy as np
from autoname import get_function_name
from config import CONFIG


def loadsp(function_name="draw_gc", dirpath=CONFIG["workspace"], numports=2, **kwargs):
    name = kwargs.pop("name", get_function_name(function_name, **kwargs))

    dirpath = pathlib.Path(dirpath) / function_name
    filepath = dirpath / name
    filepath_sp = str(filepath.with_suffix(".dat"))

    assert filepath_sp.exists(), f"Sparameters  not found in {filepath_sp}"

    F = []
    S = []
    port_names = []

    with open(filepath_sp, "r") as fid:
        for i in range(numports):
            port_line = fid.readline()
            m = re.search('\[".*",', port_line)
            if m:
                port = m.group(0)
                port_names.append(port[2:-2])
        line = fid.readline()
        line = fid.readline()
        numrows = int(tuple(line[1:-2].split(","))[0])
        S = np.zeros((numrows, numports, numports), dtype="complex128")
        r = m = n = 0
        for line in fid:
            if line[0] == "(":
                continue
            data = line.split()
            data = list(map(float, data))
            if m == 0 and n == 0:
                F.append(data[0])
            S[r, m, n] = data[1] * np.exp(1j * data[2])
            r += 1
            if r == numrows:
                r = 0
                m += 1
                if m == numports:
                    m = 0
                    n += 1
                    if n == numports:
                        break
    return (port_names, F, S)
