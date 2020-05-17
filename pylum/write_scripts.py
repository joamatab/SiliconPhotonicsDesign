import pathlib

from pylum.config import CONFIG


def mkdir(scripts_dict):
    """ creates a folder and returns the Path
    """
    assert (
        "name" in scripts_dict
    ), "the scripts dict needs a name, make sure you use the @autoname decorator in the function that returns your dict of scripts"
    dirpath = CONFIG["workspace"] / scripts_dict["name"]
    dirpath.mkdir(exist_ok=True)
    scripts_dict["dirpath"] = dirpath
    return dirpath


def write_scripts(scripts_dict):
    """ saves a dict of scripts into a dirpath folder
    the dirpath folder needs to be defined in the dict of scripts
    """
    dirpath = scripts_dict.get("dirpath", mkdir(scripts_dict))
    dirpath = pathlib.Path(dirpath)
    dirpath.mkdir(exist_ok=True)

    for script_name, script in scripts_dict.items():
        if script_name.endswith((".lsf", ".json", ".py")):
            with open(dirpath / script_name, "w") as f:
                f.write(script)
    print(f"write scripts in {dirpath}")
    return dirpath


if __name__ == "__main__":
    pass
