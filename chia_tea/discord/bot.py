
import os
import sqlite3
from datetime import datetime

from discord.ext import commands

from ..protobuf.to_sqlite.sql_cmds import get_machine_infos_from_db
from ..utils.cli import parse_args
from ..utils.config import get_config, read_config
from ..utils.logger import get_logger
from ..utils.timing import format_timedelta_from_secs
from .notifications.common import get_machine_info_name
from .notifications.run_notifiers import (
    get_current_computer_and_machine_infos_from_db, log_and_send_msg_if_any,
    run_notifiers)

# setup log handler
module_name = os.path.splitext(os.path.basename(__file__))[0]

# =========================
#         DISCORD
# =========================

bot = commands.Bot(command_prefix="$")
channel_id = ""
db_filepath = ""


@bot.command(name="hi")
async def _bot_hi(ctx):
    await ctx.send("Hi!")


@bot.command(name="wallets")
async def _wallets(ctx):

    # open the database read only
    global db_filepath
    connection = sqlite3.connect(
        f"file:{db_filepath}?mode=ro",
        uri=True,
    )
    cursor = connection.cursor()

    machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
        cursor
    )
    messages = []

    for _, (machine, computer_info) in machine_and_computer_info_dict.items():
        wallet_info = computer_info.wallet_info
        if wallet_info.is_running:
            icon = "🟢" if wallet_info.is_synced else "🟠"
            not_msg = "" if wallet_info.is_synced else "not "
            messages.append(f"\nWallet 👛 *{get_machine_info_name(machine)}*")
            messages.append(f"   {icon} {not_msg}synchronized")

    # Heading in case there is anything to report
    if not messages:
        messages.append("No wallets 👛 found.")

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


@bot.command(name="machines")
async def _bot_machines(ctx):

    # open the database read only
    global db_filepath
    connection = sqlite3.connect(
        f"file:{db_filepath}?mode=ro",
        uri=True,
    )
    cursor = connection.cursor()

    # get all machine infos from the database
    machine_infos, _ = get_machine_infos_from_db(cursor)

    # convert the infos into messages
    # TODO move this elsewhere
    messages = []
    for machine_info in machine_infos:
        dt = datetime.fromtimestamp(machine_info.time_last_msg)
        seconds_since_last_contact = (datetime.now() - dt).total_seconds()
        is_connected = seconds_since_last_contact < 60
        icon = "🟢" if is_connected else "🟠"
        machine_name = get_machine_info_name(machine_info)
        messages.append(
            f"{icon} {machine_name} responded {seconds_since_last_contact:.1f} seconds ago")

    # Heading in case there is anything to report
    if messages:
        messages.insert(0, "**Machines being Monitored 🧐:**")
    else:
        messages.append("No machines being monitored 😴")

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


@bot.command(name="farmers")
async def _farmer(ctx):

    # open the database read only
    global db_filepath
    connection = sqlite3.connect(
        f"file:{db_filepath}?mode=ro",
        uri=True,
    )
    cursor = connection.cursor()

    machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
        cursor
    )

    messages = []

    for _, (machine, computer_info) in machine_and_computer_info_dict.items():
        farmer_is_running = computer_info.farmer_info.is_running

        # TODO synced status
        # TODO harvesters don't show yet

        # a farmer is running, create a message
        if farmer_is_running:
            messages += [
                f"\n🧑‍🌾 *{get_machine_info_name(machine)}*:"
            ]

            # list up connected harvesters
            now_timestamp = datetime.now().timestamp()
            for harvester in computer_info.connected_harvesters:
                messages.append(
                    """
  Harvester *{harvester_id}*
     🌐 ip address:  {ip_address}
     📡 last answer: {last_answer} ago
     🔌 Timeouts: {n_timeouts}
     🚆 missed challenges: {missed_challenges}
     🌾 plots: {n_plots}""".format(
                        ip_address=harvester.ip_address,
                        last_answer=format_timedelta_from_secs(
                            now_timestamp - harvester.last_message_time),
                        harvester_id=harvester.id[:8],
                        n_timeouts=harvester.n_timeouts,
                        missed_challenges=harvester.missed_challenges,
                        n_plots=harvester.n_plots,
                    )
                )

    if messages:
        messages.insert(0, "**Farmers:**")
    else:
        messages.append("No farmers 🧑‍🌾 around.")

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )

@bot.command(name="harvesters")
async def _harvester(ctx):

    # open the database read only
    global db_filepath
    connection = sqlite3.connect(
        f"file:{db_filepath}?mode=ro",
        uri=True,
    )
    cursor = connection.cursor()

    machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
        cursor
    )

    messages = []

    for _, (machine, computer_info) in machine_and_computer_info_dict.items():
        messages += [
            f"\n🧑‍🌾 *{get_machine_info_name(machine)}*:"
        ]

        # list up connected harvesters
        now_timestamp = datetime.now().timestamp()
        for harvester in computer_info.connected_harvesters:
            messages.append(
                    """
  Harvester *{harvester_id}*
     🌐 ip address:  {ip_address}
     📡 last answer: {last_answer} ago
     🔌 Timeouts: {n_timeouts}
     🚆 missed challenges: {missed_challenges}
     🌾 plots: {n_plots}""".format(
                        ip_address=harvester.ip_address,
                        last_answer=format_timedelta_from_secs(
                            now_timestamp - harvester.last_message_time),
                        harvester_id=harvester.id[:8],
                        n_timeouts=harvester.n_timeouts,
                        missed_challenges=harvester.missed_challenges,
                        n_plots=harvester.n_plots,
                    )
                )

    if messages:
        messages.insert(0, "**Harvesters:**")
    else:
        messages.append("No Harvesters 🧑‍🌾 around.")

    await log_and_send_msg_if_any(
        messages=messages,
        logger=get_logger(__file__),
        channel=ctx.channel,
        is_testing=get_config().development.testing,
    )


def get_discord_channel_id() -> int:
    """ Get the discord channel id from the config

    Returns
    -------
    channel_id : int
        discord channel id

    Raises
    ------
    ValueError
        In case that the channel id cannot be converte to a string
    """
    channel_id = get_config().discord.channel_id

    # yaml sometimes returns a str depending on how
    # the user put the value in, but we need an int
    if not isinstance(channel_id, int):
        try:
            channel_id = int(channel_id)
        except ValueError:
            err_msg = "Cannot convert discord channel id '{0}' to number."
            get_logger(module_name).error(err_msg.format(
                channel_id
            ))
            exit(1)

    return channel_id


@bot.event
async def on_ready():
    get_logger(module_name).info("Bot started.")

    # get discord channel
    channel = bot.get_channel(channel_id)

    config = get_config()
    is_testing = config.development.testing

    await run_notifiers(
        db_filepath,
        channel,
        is_testing
    )


def main():
    args = parse_args(
        name="Chia Tea Discord Bot",
        description="Start a discord bot to keep an eye on your Chia farm."
    )

    # load config
    config = read_config(args.config)

    discord_token = config.discord.token
    global channel_id
    channel_id = get_discord_channel_id()

    global db_filepath
    db_filepath = config.monitoring.server.db_filepath

    # initiate bot and event loop
    # create_task must come first!!!!
    bot.run(discord_token)


if __name__ == "__main__":
    main()
