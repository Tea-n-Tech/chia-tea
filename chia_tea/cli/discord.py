import typer

from ..protobuf.generated.config_pb2 import ChiaTeaConfig

from ..utils.logger import get_logger
from ..utils.config import DEFAULT_CONFIG_FILEPATH, read_config
from ..discord.bot import bot

# globals
channel_id = ""

discord_cmd = typer.Typer(invoke_without_command=True)


@discord_cmd.callback()
def discord_callback(config: str = DEFAULT_CONFIG_FILEPATH):
    """
    Start the discord bot watching the monitoring database.
    """

    # load config
    config = read_config(config)

    discord_token = config.discord.token

    # pylint: disable=global-statement
    global channel_id
    channel_id = get_discord_channel_id(config)

    # initiate bot and event loop
    # create_task must come first!!!!
    bot.run(discord_token)


def get_discord_channel_id(config: ChiaTeaConfig) -> int:
    """Get the discord channel id from the config

    Returns
    -------
    channel_id_cfg : int
        discord channel id

    Raises
    ------
    ValueError
        In case that the channel id cannot be converte to a string
    """
    channel_id_cfg = config.discord.channel_id

    # yaml sometimes returns a str depending on how
    # the user put the value in, but we need an int
    if not isinstance(channel_id_cfg, int):
        try:
            channel_id_cfg = int(channel_id_cfg)
        except ValueError:
            err_msg = "Cannot convert discord channel id '{0}' to number."
            get_logger("discord").error(err_msg, channel_id_cfg)
            typer.Exit(1)

    return channel_id_cfg
