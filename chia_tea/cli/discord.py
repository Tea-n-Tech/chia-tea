import typer

from ..discord.bot import run_discord_bot
from ..utils.config import DEFAULT_CONFIG_FILEPATH, read_config

discord_cmd = typer.Typer(invoke_without_command=True)


@discord_cmd.callback()
def discord_callback(config: str = DEFAULT_CONFIG_FILEPATH):
    """
    Start the discord bot watching the monitoring database.
    """

    # load config
    config = read_config(config)

    discord_token = config.discord.token
    channel_id = config.discord.channel_id

    run_discord_bot(discord_token, channel_id)
