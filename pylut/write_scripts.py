import pathlib

from pylut.config import CONFIG


def mkdir(scripts_dict):
    """ creates a folder and returns the Path
    """
    dirpath = CONFIG["workspace"] / scripts_dict["name"]
    dirpath.mkdir(exist_ok=True)
    scripts_dict["dirpath"] = dirpath
    return dirpath


def exists(scripts_dict):
    dirpath = CONFIG["workspace"] / scripts_dict["name"]
    return dirpath.exists()


def write_scripts(scripts_dict):
    """ saves a dict of scripts into a path
    """
    dirpath = scripts_dict.get("dirpath", mkdir(scripts_dict))
    dirpath = pathlib.Path(dirpath)
    dirpath.mkdir(exist_ok=True)

    for script_name, script in scripts_dict.items():
        if script_name.endswith(".lsf") or script_name.endswith(".py"):
            with open(dirpath / script_name, "w") as f:
                f.write(script)
    return dirpath


if __name__ == "__main__":
    pass
