from pylum.write_scripts import write_scripts


def run_mode(scripts_dict, session=None, return_session=False):
    """ runs a dict of scripts in a MODE session
    there should be a main.lsf defined
    """
    import lumapi

    dirpath = scripts_dict.get("dirpath", write_scripts(scripts_dict))

    s = session or lumapi.MODE()
    s.cd(str(dirpath))

    s.eval(scripts_dict["main.lsf"])

    if return_session:
        return s


def run_fdtd(scripts_dict, session=None, return_session=False):
    """ runs a dict of scripts in a FDTD session
    there should be a main.lsf defined

    .. code-block:: python

        import pylum
        from pylum.grating_coupler import sweep

        scripts_dict = sweep()
        run_fdtd(scripts_dict)

    """
    import lumapi

    dirpath = scripts_dict.get("dirpath", write_scripts(scripts_dict))

    s = session or lumapi.FDTD()
    s.cd(str(dirpath))

    s.eval(scripts_dict["main.lsf"])

    if return_session:
        return s


if __name__ == "__main__":
    from pylum.grating_coupler import sweep

    scripts_dict = sweep()
    run_fdtd(scripts_dict)
