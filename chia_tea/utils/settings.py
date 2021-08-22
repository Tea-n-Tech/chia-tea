from typing import Dict, Any
import os
import json

settings_dir = os.path.expanduser(
    "~/.chia_tea"
)
path_to_settings = os.path.join(
    settings_dir,
    "settings.json"
)

# for caching settings locally
SETTINGS_CACHE = {}
SETTINGS_ARE_LOADED = False


def ensure_chia_settings_file():
    """ Ensure the chia settings file exists
    """
    if not os.path.isdir(settings_dir):
        os.makedirs(settings_dir, exist_ok=True)

    if not os.path.isfile(path_to_settings):
        with open(path_to_settings, "w", encoding="utf8") as file_handle:
            file_handle.write(json.dumps(SETTINGS_CACHE))


def read_settings_file() -> Dict[str, str]:
    """ Reads the settings File and puts its content to the settings variable
    """
    ensure_chia_settings_file()

    with open(path_to_settings, "r", encoding="utf8") as file_handle:
        return json.loads(file_handle.read())


def write_settings_file():
    """ Writes the settings File to disc
    """
    with open(path_to_settings, "w", encoding="utf8") as settings_file:
        json.dump(SETTINGS_CACHE, settings_file)


def ensure_settings_are_loaded():
    """ Checks that the settings are loaded
    """
    if not SETTINGS_ARE_LOADED:
        # pylint: disable=global-statement
        global SETTINGS_CACHE
        SETTINGS_CACHE = read_settings_file()


def get_settings_value(key: str, default: Any) -> Any:
    """ Returns the value of a key in the settings Dict

    Parameters
    ----------
    key : str
        key of which the value is returned of
    default : str
        default value to get

    Returns
    -------
    value : Any
        Either value from settings or default value
    """
    ensure_settings_are_loaded()

    value = SETTINGS_CACHE.get(key)

    if value is None:
        set_settings_value(key, default)
        value = default

    return value


def set_settings_value(name: str, value: Any):
    """ Sets the value of the Dict and writes settings to disc

    Parameters
    ----------
    name : str
        name of the attribute to set
    value : Any
        value to set
    """
    ensure_settings_are_loaded()
    SETTINGS_CACHE[name] = value
    write_settings_file()
