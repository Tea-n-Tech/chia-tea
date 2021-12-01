from discord.ext import commands

from chia_tea.discord.commands.plotters import plotters_cmd

from ..utils.config import get_config
from ..utils.logger import get_logger
from .commands.farmers import farmers_cmd
from .commands.harvesters import harvesters_cmd
from .commands.machines import machines_cmd
from .commands.sql import sql_cmd
from .commands.wallets import wallets_cmd
from .notifications.run_notifiers import log_and_send_msg_if_any, run_notifiers


bot = commands.Bot(command_prefix="$")
channel_id = -1


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


@bot.event
async def on_ready():
    """Function run when the bot is ready"""
    db_filepath = get_config().monitoring.server.db_filepath

    get_logger(__file__).info("Bot started.")

    # get discord channel
    channel = bot.get_channel(channel_id)

    config = get_config()
    is_testing = config.development.testing

    await run_notifiers(db_filepath, channel, is_testing)


def run_discord_bot(discord_token: str, discord_channel_id: int) -> None:
    """Run the discord bot"""
    # pylint: disable=global-statement
    global channel_id
    channel_id = discord_channel_id

    bot.run(discord_token)
