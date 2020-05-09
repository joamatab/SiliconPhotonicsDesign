import pylut
from pylut.config import CONFIG


def test_loadmat(
    matlab_file_path=CONFIG["repo_workspace"] / "grating_coupler_sweep" / "results.mat",
):
    d = pylut.loadmat(matlab_file_path)
    # print(d.keys())
    assert d["polarization"] == "TE"


if __name__ == "__main__":
    test_loadmat()
