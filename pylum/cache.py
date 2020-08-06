import h5py
import numpy as np

from pylum.config import CONFIG


def test_cache():
    filepath = CONFIG["workspace"] / "test.h5"
    d = dict(string="Hello!", array=np.array([1, 2, 3]))

    write_cache(d, filepath)
    d2 = read_cache(filepath)
    for k in d2.keys():
        assert np.array_equal(d[k], d2[k].value), f"{k} {d[k]} and {d2[k]} do not match"


def write_cache(d, filepath):
    """ writes dict to cache """

    f = h5py.File(filepath, "w")

    for k, v in d.items():
        try:
            f.create_dataset(k, data=v)
        except Exception:
            pass

    f.close()


def read_cache(filepath):
    return h5py.File(filepath, "r")


if __name__ == "__main__":
    test_cache()
