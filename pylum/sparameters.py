import shutil

from pylum.write_scripts import write_scripts


def cp(scripts_dict, src, dst):
    dirpath = write_scripts(scripts_dict)
    src = dirpath / src
    shutil.copy(src, dst)


if __name__ == "__main__":
    import pp
    from grating_coupler import sparameters_te

    scripts_dict = sparameters_te()
    dirpath = write_scripts(scripts_dict)
    src = dirpath / "GC_Sparam.dat"
    dirpath = pp.CONFIG["gdslib"] / "grating_coupler_te"
    dirpath.mkdir(exist_ok=True)

    dst = dirpath / "grating_coupler_te.dat"
    shutil.copy(src, dst)
