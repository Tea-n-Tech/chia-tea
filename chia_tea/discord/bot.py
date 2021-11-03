import os
import sys

from discord.ext import commands

from chia_tea.discord.commands.plotters import plotters_cmd

from ..utils.cli import parse_args
from ..utils.config import get_config, read_config
from ..utils.logger import get_logger
from .commands.farmers import farmers_cmd
from .commands.harvesters import harvesters_cmd
from .commands.machines import machines_cmd
from .commands.sql import sql_cmd
from .commands.wallets import wallets_cmd
from .notifications.run_notifiers import log_and_send_msg_if_any, run_notifiers

# setup log handler
module_name = os.path.splitext(os.path.basename(__file__))[0]

# =========================
#         DISCORD
# =========================

bot = commands.Bot(command_prefix="$")
channel_id = ""


@bot.command(name="hi")
async def bot_hi(ctx):
    """Says hi to the user"""
    await ctx.send("Hi!")


@bot.command(name="wallets")
async def bot_wallets(ctx):
    """Prints all wallets"""
    db_filepath = get_config().monitoring.server.db_filepath

    messages = await wallets_cmd(db_filepath)

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


@bot.command(name="machines")
async def bot_machines(ctx):
    """Prints all machines"""
    db_filepath = get_config().monitoring.server.db_filepath

    messages = await machines_cmd(db_filepath)

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


@bot.command(name="farmers")
async def bot_farmers(ctx):
    """Prints all farmers"""
    db_filepath = get_config().monitoring.server.db_filepath

    messages = await farmers_cmd(db_filepath)

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


@bot.command(name="harvesters")
async def bot_harvester(ctx):
    """Prints all harvesters"""
    db_filepath = get_config().monitoring.server.db_filepath

    messages = await harvesters_cmd(db_filepath)

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


@bot.command(name="plotters")
async def bot_plotters(ctx):
    """Prints all plotters"""
    db_filepath = get_config().monitoring.server.db_filepath

    messages = await plotters_cmd(db_filepath)

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


@bot.command(name="sql")
async def bot_sql(ctx, *cmds):
    """Let's the user execute arbitrary sql statements"""
    db_filepath = get_config().monitoring.server.db_filepath

    cmd = " ".join(cmds)
    messages = await sql_cmd(db_filepath, cmd)

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


def get_discord_channel_id() -> int:
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
    channel_id_cfg = get_config().discord.channel_id

    # yaml sometimes returns a str depending on how
    # the user put the value in, but we need an int
    if not isinstance(channel_id_cfg, int):
        try:
            channel_id_cfg = int(channel_id_cfg)
        except ValueError:
            err_msg = "Cannot convert discord channel id '{0}' to number."
            get_logger(module_name).error(err_msg, channel_id_cfg)
            sys.exit(1)

    return channel_id_cfg


@bot.event
async def on_ready():
    """Function run when the bot is ready"""
    db_filepath = get_config().monitoring.server.db_filepath

    get_logger(module_name).info("Bot started.")

    # get discord channel
    channel = bot.get_channel(channel_id)

    config = get_config()
    is_testing = config.development.testing

    await run_notifiers(db_filepath, channel, is_testing)


def main():
    """Main function for the discord bot"""
    args = parse_args(
        name="Chia Tea Discord Bot",
        description="Start a discord bot to keep an eye on your Chia farm.",
    )

    # load config
    config = read_config(args.config)

    discord_token = config.discord.token

    # pylint: disable=global-statement
    global channel_id
    channel_id = get_discord_channel_id()

    # initiate bot and event loop
    # create_task must come first!!!!
    bot.run(discord_token)


if __name__ == "__main__":
    main()
