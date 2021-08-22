import os

import yaml
from google.protobuf.json_format import MessageToDict, ParseDict

from ..protobuf.generated.config_pb2 import (INFO, ChiaConfig, ChiaTeaConfig,
                                             CopyConfig, DevelopmentConfig,
                                             DiscordConfig, LoggingConfig,
                                             MachineConfig, MonitoringConfig)


def create_default_config(filepath: str) -> ChiaTeaConfig:
    """ Creates a default config on the system

    Parameters
    ----------
    filepath : str
        path where to create the default config

    Returns
    -------
    config : ChiaTeaConfig
        created default config object

    Notes
    -----
        The config is being stored in the '.chia_tea'
        directory in the home folder.
    """
    config_filepath = os.path.join(filepath, "config.yml",)
    if not os.path.exists(config_filepath):
        config = get_default_config()
        save_config(config_filepath, get_default_config())
    else:
        config = get_config()

    return config


def get_default_config() -> ChiaTeaConfig:
    """ Get the default config for chia tea

    Returns
    -------
    config : ChiaTeaConfig
        default config
    """

    return ChiaTeaConfig(
        version=0,
        # configuration for machine-specific settings
        machine=MachineConfig(
            name="machine_name_to_display",
        ),
        logging=LoggingConfig(
            # Allowed is: TRACE, DEBUG, INFO, WARNING, ERROR
            loglevel=INFO,
            log_to_console=True,
            log_to_file=True,
            max_logfiles=10,
            max_logfile_size_mb=15,
        ),
        # This controls from where data is copied
        # with the CLI copy tool. The copy process
        # selects disks smartly. Also it can deal
        # with disconnects and other issues.
        copy=CopyConfig(
            source_folders=[
                "/some/plotting/folder",
                "/another/plotting/folder",
            ],
            target_folders=[
                "/some/harvester/folder",
                "/another/harvester/folder",
            ]
        ),
        # General chia-related settings
        chia=ChiaConfig(
            # Filepath at which the chia logfile resides.
            logfile_filepath="~/.chia/mainnet/log/debug.log"
        ),
        # Settings to connect to the discord bot and channel
        discord=DiscordConfig(
            token="YOUR_DISCORD_TOKEN",
            channel_id=123456789,
        ),
        # Specify monitoring settings
        monitoring=MonitoringConfig(
            # The communication is secured by certificates.
            # These need to be generated beforehand (see Taskfile).
            # One done you can register them here. The server needs
            # both while the client just needs the cert-file.
            auth=MonitoringConfig.AuthConfig(
                cert_filepath="./server.crt",
                key_filepath="./server.key",
            ),
            # Settings for the monitoring server
            server=MonitoringConfig.ServerConfig(
                port=43200,
                # filepath where the monitoring database will
                # be stored on disk.
                db_filepath="./monitoring.db",
            ),
            # Settings for the client collecting data
            client=MonitoringConfig.ClientConfig(
                # Address of the server to send data to.
                # On the very same machine this is 127.0.0.1.
                address="127.0.0.1",
                port=43200,
                # Depending on the system the data collection
                # can be quite fast and may use too much cpu.
                # This option throttles the general data
                # collection. If the data collection takes
                # longer than specified here the waiting time
                # is ignored.
                collect_data_every=1.5,
                # To not spam the database with too much data
                # we can set a limit here to send updates no
                # faster than specified.
                # Note that if nothing changed such as disk space
                # then no update is sent at all to keep stay
                # efficient.
                send_update_every=MonitoringConfig.ClientConfig.SendUpdateEvery(
                    # For hardware it is recommended to choose
                    # 1-5 minutes
                    cpu=60,
                    ram=60,
                    disk=60,
                    process=60,
                    # Chia data is not limited by default since
                    # we want to know asap if something is up.
                    # Note though that 'collect_data_every'
                    # applies and automatically rate limits
                    # chia data.
                )
            )
        ),
        # Enables development mode. This currently disables
        # encryption and also the discord bot does not send
        # send messages but they are printed to console.
        development=DevelopmentConfig(
            testing=False,
        )
    )


def read_config(filepath: str) -> ChiaTeaConfig:
    """ Reads the config file

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
    with open(filepath, 'r', encoding="utf8") as stream:
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
    """ Checks whether a config was loaded

    Returns
    -------
    is_loaded : bool
        whether the config is loaded
    """
    return __IS_LOADED


def save_config(filepath: str, config: ChiaTeaConfig):
    """ Save the config to a file

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
__GLOBAL_CONFIG = get_default_config()
__IS_LOADED = False


def get_config() -> ChiaTeaConfig:
    """ Get the global application config

    Returns
    -------
    config : ChiaTeaConfig
        global config
    """
    return __GLOBAL_CONFIG
