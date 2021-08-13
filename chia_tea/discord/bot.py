
import os
import sqlite3
from datetime import datetime
from typing import Tuple

from discord.ext import commands

from ..protobuf.to_sqlite.sql_cmds import (
    get_machine_infos_from_db,
    get_cpu_for_machine_from_db,
    get_ram_for_machine_from_db,
)
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


def _open_database_read_only() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """ Open a sqlite database read only

    Returns
    -------
    connection : sqlite3.Connection
        connection object
    cursor : sqlite3.Cursor
        sqlite cursor
    """
    global db_filepath
    connection = sqlite3.connect(
        f"file:{db_filepath}?mode=ro",
        uri=True,
    )
    cursor = connection.cursor()

    return connection, cursor


@bot.command(name="hi")
async def _bot_hi(ctx):
    await ctx.send("Hi!")


@bot.command(name="wallets")
async def _wallets(ctx):

    # open the database read only
    connection, cursor = _open_database_read_only()

    machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
        cursor
    )
    messages = []

    for _, (machine, computer_info) in machine_and_computer_info_dict.items():
        wallet = computer_info.wallet
        if wallet.is_running:
            icon = "🟢" if wallet.is_synced else "🟠"
            not_msg = "" if wallet.is_synced else "not "
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

    connection.close()


@bot.command(name="machines")
async def _bot_machines(ctx):

    # open the database read only
    connection, cursor = _open_database_read_only()

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

        cpus, _ = get_cpu_for_machine_from_db(
            cursor,
            machine_info.machine_id,
        )
        cpu_msgs = [
            """   __CPU__
      name:  {name}
      cores: {cores}
      usage: {usage:.1f}%
      temp:  {temperature:.0f} deg
      clock: {speed:.0f} Mhz""".format(
                name=cpu.name,
                cores=cpu.n_vcores,
                usage=cpu.usage,
                temperature=cpu.temperature,
                speed=cpu.clock_speed,
            )
            for cpu in cpus
        ]

        rams, _ = get_ram_for_machine_from_db(
            cursor,
            machine_info.machine_id,
        )
        ram_msgs = []
        for ram in rams:
            used_percent = 0.
            try:
                used_percent = ram.used_ram / ram.total_ram * 100
            except ZeroDivisionError:
                pass
            swap_percent = 0.
            try:
                swap_percent = ram.used_swap / ram.total_swap * 100
            except ZeroDivisionError:
                pass

            ram_msgs.append(
                """   __RAM__
      total: {total}
      used:  {used:.1f}%
      swap:  {swap:.1f}%
      """.format(
                    total=format_memory_size(ram.total_ram),
                    used=used_percent,
                    swap=swap_percent,
                )
            )

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

    connection.close()


@ bot.command(name="farmers")
async def _farmer(ctx):

    # open the database read only
    connection, cursor = _open_database_read_only()

    machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
        cursor
    )

    messages = []

    for _, (machine, computer_info) in machine_and_computer_info_dict.items():
        farmer_is_running = computer_info.farmer.is_running

        # TODO synced status
        # TODO harvesters don't show yet

        # a farmer is running, create a message
        if farmer_is_running:
            messages += [
                f"\n🧑‍🌾 *{get_machine_info_name(machine)}*:"
            ]

            # list up connected harvesters
            now_timestamp = datetime.now().timestamp()
            for harvester in computer_info.farmer_harvesters:
                messages.append(
                    """
  Harvester *{harvester_id}*
     🌐 ip address:  {ip_address}
     📡 last answer: {last_answer} ago
     🚆 missed challenges: {missed_challenges}
     🌾 plots: {n_plots}""".format(
                        ip_address=harvester.ip_address,
                        last_answer=format_timedelta_from_secs(
                            now_timestamp - harvester.time_last_msg_received),
                        harvester_id=harvester.id[:8],
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

    connection.close()


def format_memory_size(n_bytes: float, suffix: str = 'B'):
    """ Formats a memory size number

    Parameters
    ----------
    n_bytes : float
        bytes to format
    suffix : string
        suffix of the memory

    Notes
    -----
        Thanks Fred @ Stackoverflow:
        https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
    """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(n_bytes) < 1024.0:
            return "%3.1f%s%s" % (n_bytes, unit, suffix)
        n_bytes /= 1024.0
    return "%.1f%s%s" % (n_bytes, 'Yi', suffix)


@ bot.command(name="harvesters")
async def _harvester(ctx):

    connection, cursor = _open_database_read_only()

    machine_and_computer_info_dict = get_current_computer_and_machine_infos_from_db(
        cursor
    )

    messages = []

    for _, (machine, computer_info) in machine_and_computer_info_dict.items():
        harvester = computer_info.harvester
        plots = computer_info.harvester_plots
        total_size = sum(plot.filesize for plot in plots)

        # disk messages
        disk_msgs = []
        for disk in computer_info.disks:
            usage_percent = 0
            try:
                usage_percent = disk.used_space / disk.total_space * 100
            except ZeroDivisionError:
                pass
            disk_msgs.append(
                f"        {usage_percent:3.1f}% {disk.id}"
            )

        # full msg
        messages.append(
            """
  🚜 Harvester {machine}
     🍀 proofs: {n_proofs}
     🌾 plots: {n_plots}
     🌾 size of plots: {total_size}
     💽 disks:
{disk_msgs}
     """.format(
                machine=get_machine_info_name(machine),
                n_plots=len(plots),
                n_proofs=harvester.n_proofs,
                total_size=format_memory_size(total_size),
                disk_msgs="\n".join(disk_msgs)
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

    connection.close()


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


@ bot.event
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
