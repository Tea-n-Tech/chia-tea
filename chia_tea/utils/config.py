import os

import yaml
from google.protobuf.json_format import MessageToDict, ParseDict

from ..protobuf.generated.config_pb2 import ChiaTeaConfig


DEFAULT_CONFIG_FOLDER = os.path.expanduser("~/.chia_tea/config")
DEFAULT_CONFIG_FILEPATH = os.path.join(DEFAULT_CONFIG_FOLDER, "config.yml")

DEFAULT_CONFIG_TEMPLATE = """
version: 0

machine:
  # this name will be used for display
  name: machine name to display

logging:
  # Allowed is: TRACE, DEBUG, INFO, WARNING, ERROR
  loglevel: INFO
  # Whether to print the statements in the console
  log_to_console: True
  # Uses the file logger
  log_to_file: True
  # These settings give control on the size of
  # the logfiles.
  max_logfiles: 10
  max_logfile_size_mb: 15

# This controls from where data is copied
# with the CLI copy tool. The copy process
# selects disks smartly. Also it can deal
# with disconnects and other issues.
copy:
  source_folders:
    - "/some/plotting/folder"
    - "/another/plotting/folder"
  target_folders:
    - "/some/harvester/folder"
    - "/another/harvester/folder"

# General chia-related settings
chia:
  # Filepath at which the chia logfile resides.
  logfile_filepath: ~/.chia/mainnet/log/debug.log
  # Filepath to the logfile of the madmax plotter.
  # This tracks the plotting progress. Leave empty
  # if not used.
  madmax_logfile: ""

discord:
  token: YOUR_DISCORD_TOKEN
  channel_id: 123456789

monitoring:
  auth:
    cert_filepath: {cert_filepath}
    key_filepath: {key_filepath}

  # settings for the monitoring server receiving
  # and storing monitoring data
  server:
    port: 43200
    # filepath where the monitoring database will
    # be stored on disk.
    db_filepath: ./monitoring.db

  # settings for the monitoring client, collecting
  # and sending data
  client:
    # Address of the server to send data to.
    # On the very same machine this is 127.0.0.1.
    address: 127.0.0.1
    port: 43200

    # Depending on the system the data collection
    # can be quite fast and may use too much cpu.
    # This option throttles the general data
    # collection. If the data collection takes
    # longer than specified here the waiting time
    # is ignored.
    collect_data_every: 1.5 # seconds

    # To not spam the database with too much data
    # we can set a limit here to send updates no
    # faster than specified.
    # Note that if nothing changed such as disk space
    # then no update is sent at all to keep stay
    # efficient.
    send_update_every:
      # For hardware it is recommended to choose
      # 1-5 minutes
      cpu: 60 # seconds
      ram: 60 # seconds
      disk: 60 # seconds
      process: 60 # seconds

      # Chia data is not limited by default since
      # we want to know asap if something is up.
      # Note though that 'collect_data_every'
      # applies and automatically rate limits
      # chia data.

      # farmer: 2
      # connected_harvester: 2
      # harvester: 2
      # wallet: 2
      # plotting_plot: 2
      # harvester_plot: 2

# Enables development mode. This currently disables
# encryption and also the discord bot does not send
# send messages but they are printed to console.
development:
  testing: False
"""


def create_default_config(filepath: str = DEFAULT_CONFIG_FILEPATH, overwrite: bool = False):
    """Creates a default config on the system

    Parameters
    ----------
    filepath : str
        path where to create the default config
    overwrite : bool
        overwrite an existing config file

    Raises
    ------
    FileExistsError
        If the file already exists and overwrite is False then an exception is
        raised.

    Notes
    -----
        If no filepath is specified, the config is created by default
        in `~/.chia_tea/config/config.yml`.
    """
    if not filepath:
        raise ValueError("No filepath specified")

    filepath = os.path.abspath(filepath)

    folder = os.path.dirname(filepath)
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(filepath) or overwrite:
        certificate_directory = os.path.dirname(filepath)
        with open(filepath, "w", encoding="utf-8") as fp:
            fp.write(get_default_config_as_string(certificate_folder=certificate_directory))
    else:
        raise FileExistsError(f"Config file already exists: {filepath}")


def get_default_config_as_string(certificate_folder: str) -> str:
    """Get the default config for chia tea as a string

    Parameters
    ----------
    certificate_folder : str
        directory of the certificates

    Returns
    -------
    config : str
        default config as a string
    """
    key_filepath = os.path.join(certificate_folder, "server.key")
    cert_filepath = os.path.join(certificate_folder, "server.crt")

    config_as_yml = DEFAULT_CONFIG_TEMPLATE.format(
        cert_filepath=cert_filepath, key_filepath=key_filepath
    )

    return config_as_yml


def get_default_config(certificate_folder: str) -> ChiaTeaConfig:
    """Get the default config for chia tea

    Parameters
    ----------
    certificate_folder : str
        directory of the certificates

    Returns
    -------
    config : ChiaTeaConfig
        default config
    """

    config_dict = yaml.safe_load(get_default_config_as_string(certificate_folder))
    config = ParseDict(
        js_dict=config_dict,
        message=ChiaTeaConfig(),
    )

    return config


def read_config(filepath: str) -> ChiaTeaConfig:
    """Reads the config file

    Parameters
    ----------
    filepath : str
        path to the config file

    Returns
    -------
    config : ChiaTeaConfig
        read config file

    Raises
    ------
    yaml.YAMLError
        In case of any issues with yaml parsing
    ValueError
        If config values are invalid
    """
    with open(filepath, "r", encoding="utf8") as stream:
        config_dict = yaml.safe_load(stream)

    config = ParseDict(
        js_dict=config_dict,
        message=ChiaTeaConfig(),
    )

    # pylint: disable=global-statement
    global __GLOBAL_CONFIG
    global __IS_LOADED
    __GLOBAL_CONFIG = config
    __IS_LOADED = True

    return config


def config_is_loaded() -> bool:
    """Checks whether a config was loaded

    Returns
    -------
    is_loaded : bool
        whether the config is loaded
    """
    return __IS_LOADED


def save_config(filepath: str, config: ChiaTeaConfig):
    """Save the config to a file

    Parameters
    ----------
    filepath : str
        path to save the config
    config : ChiaTeaConfig
        config to save
    """

    with open(filepath, "w", encoding="utf8") as file_handle:
        file_handle.write(
            yaml.dump(
                MessageToDict(
                    message=config,
                    including_default_value_fields=True,
                    use_integers_for_enums=False,
                    preserving_proto_field_name=True,
                )
            )
        )


# This is the global application config
__GLOBAL_CONFIG = get_default_config(DEFAULT_CONFIG_FILEPATH)
__IS_LOADED = False


def get_config() -> ChiaTeaConfig:
    """Get the global application config

    Returns
    -------
    config : ChiaTeaConfig
        global config
    """
    return __GLOBAL_CONFIG
