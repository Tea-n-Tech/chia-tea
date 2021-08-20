import os
import sys
from datetime import datetime

from discord.ext import commands

from ..protobuf.to_sqlite.sql_cmds import (get_cpu_for_machine_from_db,
                                           get_machine_infos_from_db,
                                           get_ram_for_machine_from_db)
from ..utils.cli import parse_args
from ..utils.config import get_config, read_config
from ..utils.logger import get_logger
from .notifications.common import get_machine_info_name, open_database_read_only
from .notifications.formatting import (cpu_pb2_as_markdown,
                                       farmer_harvester_pb2_as_markdown,
                                       harvester_pb2_as_markdown,
                                       ram_pb2_as_markdown)
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

    with open_database_read_only(db_filepath) as cursor:
        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
            cursor
        )
        messages = []

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            wallet = computer_info.wallet
            if wallet.is_running:
                icon = "🟢" if wallet.is_synced else "🟠"
                not_msg = "" if wallet.is_synced else "not "
                messages.append(
                    f"\nWallet 👛 *{get_machine_info_name(machine)}*")
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

    with open_database_read_only(db_filepath) as cursor:

        # get all machine infos from the database
        machine_infos, _ = get_machine_infos_from_db(cursor)

        # convert the infos into messages
        messages = []
        for machine_info in machine_infos:
            seconds_since_last_contact = (
                datetime.now() - datetime.fromtimestamp(machine_info.time_last_msg)).total_seconds()
            is_connected = seconds_since_last_contact < 60
            icon = "🟢" if is_connected else "🟠"

            cpus, _ = get_cpu_for_machine_from_db(
                cursor,
                machine_info.machine_id,
            )
            cpu_msgs = [
                cpu_pb2_as_markdown(cpu)
                for cpu in cpus
            ]

            rams, _ = get_ram_for_machine_from_db(
                cursor,
                machine_info.machine_id,
            )
            ram_msgs = [
                ram_pb2_as_markdown(ram) for ram in rams
            ]

            machine_name = get_machine_info_name(machine_info)
            messages += [
                f"{icon} {machine_name} responded {seconds_since_last_contact:.1f} seconds ago",
            ] + cpu_msgs + ram_msgs

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

    with open_database_read_only(db_filepath) as cursor:

        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
            cursor
        )

        messages = []

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            farmer_is_running = computer_info.farmer.is_running

            # a farmer is running, create a message
            if farmer_is_running:
                messages += [
                    f"\n🧑‍🌾 *{get_machine_info_name(machine)}*:"
                ]

                # list up connected harvesters
                messages = [
                    farmer_harvester_pb2_as_markdown(harvester)
                    for harvester in computer_info.farmer_harvesters
                ]

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

    with open_database_read_only(db_filepath) as cursor:

        machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
            cursor
        )

        messages = []

        for _, (machine, computer_info) in machine_and_computer_info_dict.items():
            messages.append(
                harvester_pb2_as_markdown(
                    machine,
                    computer_info.harvester,
                    computer_info.plots,
                    computer_info.disks,
                )
            )

        if messages:
            messages.insert(0, "**Harvesters:**")
        else:
            messages.append("No Harvesters 🚜 around.")

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
    """ Function run when the bot is ready
    """
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
    """ Main function for the discord bot
    """
    args = parse_args(
        name="Chia Tea Discord Bot",
        description="Start a discord bot to keep an eye on your Chia farm."
    )

    # load config
    config = read_config(args.config)

    discord_token = config.discord.token

    # pylint: disable=global-statement
    global channel_id
    channel_id = get_discord_channel_id()

    global db_filepath
    db_filepath = config.monitoring.server.db_filepath

    # initiate bot and event loop
    # create_task must come first!!!!
    bot.run(discord_token)


if __name__ == "__main__":
    main()
