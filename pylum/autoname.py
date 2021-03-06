import functools
import hashlib
from inspect import signature

import numpy as np

from pylum.cache import read_cache
from pylum.cache import write_cache
from pylum.config import CONFIG

MAX_NAME_LENGTH = 255

ignore_keys = ["session", "base_fsp_path"]


def get_function_name(function_name, **kwargs):
    name = function_name

    suffix = []
    for key in sorted(kwargs):
        if key not in ignore_keys:
            value = kwargs[key]
            key = join_first_letters(key)
            value = clean_value(value)
            suffix += [f"{key.upper()}{value}"]
    suffix = "_".join(suffix)

    if kwargs:
        name += "_" + suffix

    # If the name is too long, fall back on hashing the longuest arguments
    if len(name) > MAX_NAME_LENGTH:
        name = "{}_{}".format(function_name, hashlib.md5(name.encode()).hexdigest())

    return name


def dict2name(prefix=None, **kwargs):
    """ returns name from a dict """
    if prefix:
        label = [prefix]
    else:
        label = []
    return clean_name(label)


def clean_name(name):
    """Ensures that names are composed of [a-zA-Z0-9]

    FIXME: only a few characters are currently replaced.
        This function has been updated only on case-by-case basis
    """
    replace_map = {
        "=": "",
        ",": "_",
        ")": "",
        "(": "",
        ":": "_",
        "[": "",
        "]": "",
        " ": "_",
    }
    for k, v in list(replace_map.items()):
        name = name.replace(k, v)
    return name


def clean_value(value):
    """returns more readable value (integer)
    if number is < 1:
        returns number units in nm (integer)
    """

    if isinstance(value, int):  # integer
        value = str(value)
    elif type(value) in [float, np.float64]:  # float
        if 1e9 > value > 1e12:
            value = f"{int(value/1e9)}G"
        elif 1e6 > value > 1e9:
            value = f"{int(value/1e6)}M"
        elif 1e3 > value > 1e6:
            value = f"{int(value/1e3)}K"
        elif 1 > value > 1e-3:
            value = f"{int(value*1e3)}m"
        elif 2e-6 <= value < 1e-3:
            value = f"{int(value*1e6)}u"
        elif 1e-9 < value < 2e-6:
            value = f"{int(value*1e9)}n"
        elif 1e-12 < value < 1e-9:
            value = f"{int(value*1e12)}p"
        else:
            value = f"{value:.2f}"
    elif isinstance(value, list):
        value = "_".join(clean_value(v) for v in value)
    elif isinstance(value, tuple):
        value = "_".join(clean_value(v) for v in value)
    elif isinstance(value, dict):
        value = dict2name(**value)
    elif callable(value):
        value = value.__name__
    else:
        value = clean_name(str(value))
    if len(value) > MAX_NAME_LENGTH:
        value = hashlib.md5(value.encode()).hexdigest()
    return value


def join_first_letters(name):
    """ join the first letter of a name separated with underscores (taper_length -> TL) """
    return "".join([x[0] for x in name.split("_") if x])


def autoname(function):
    """decorator for auto-naming functions
    if no Keyword argument `name`  is passed it creates a name by concenating all Keyword arguments

    .. plot::
      :include-source:

      import pylum

      @pp.autoname
      def grating_coupler(wg_width=0.5):
        ...

      ms = grating_coupler(wg_width=1)
      print(ms['name'])
      >> mode_solver_WW1

    """

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        if args:
            raise ValueError("autoname supports only Keyword args")
        cache = kwargs.pop("cache", True)
        name = kwargs.pop("name", get_function_name(function.__name__, **kwargs))

        sig = signature(function)
        if "args" not in sig.parameters and "kwargs" not in sig.parameters:
            for key in kwargs.keys():
                assert (
                    key in sig.parameters.keys()
                ), f"{key} key not in {list(sig.parameters.keys())}"

        filepath = CONFIG["workspace"] / f"{name}.h5"

        if cache and filepath.exists():
            # simdict = dict(results=read_cache(filepath))
            results = read_cache(filepath)
            simdict = {k: v[()] for k, v in results.items()}

        else:
            simdict = function(**kwargs)
            assert isinstance(
                simdict, dict
            ), f"Function {function.name} needs to return a dict"
            write_cache(simdict, filepath)
        simdict["name"] = name
        simdict["function_name"] = function.__name__
        settings = kwargs.copy()

        settings.update(**{p.name: p.default for p in sig.parameters.values()})
        simdict["settings"] = settings
        simdict["settings"].pop("session", "")
        return simdict

    return wrapper


@autoname
def _dummy(
    plot=True,
    length=3,
    wg_width=0.5,
    radius=[2e-3, 3e-3],
    material_wg="Si (Silicon) - Palik",
):
    d = dict(string="Hello!", array=np.array([1, 2, 3]))
    print("im running")
    return d


def test_autoname():
    name_base = _dummy()["name"]
    assert name_base == "_dummy"
    name_int = _dummy(length=3)["name"]
    assert name_int == "_dummy_L3"
    name_float = _dummy(wg_width=0.5)["name"]
    assert name_float == "_dummy_WW500m"


def test_clean_value():
    print(clean_value(1.55))
    print(clean_value(2e-6))
    # print(clean_value(2.222222))
    # print(clean_value(0.5))
    # print(clean_value(2e-6))
    # print(clean_value(2e-9))
    # print(clean_value(2e-12))

    assert clean_value(2.222222222) == "2.22"
    assert clean_value(2) == "2"
    assert clean_value(0.2) == "200m"
    assert clean_value(2e-06) == "2u"
    assert clean_value(2e-09) == "2n"
    assert clean_value(2e-12) == "2p"


def test_clean_name():
    assert clean_name("mode_solver(:_=_2852") == "mode_solver___2852"


if __name__ == "__main__":
    # print(clean_name("mode_solver(:_=_2852"))
    # print(clean_value(0.5))
    # test_autoname()
    # test_clean_value()
    # print(_dummy(radius = [1e-3, 5e-3])['name'])
    # print(_dummy(cache=False, material_wg="SiO2 (Glass) - Palik")["name"])
    # print(_dummy(cache=False, material_wg="SiO2 (Glass) - Palik"))
    print(_dummy(material_wg="SiO2 (Glass) - Palik")["results"].keys())
