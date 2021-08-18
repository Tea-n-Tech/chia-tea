

from ..generated.computer_info_pb2 import (_UPDATEEVENT, ComputerInfo,
                                           UpdateEvent)
from ..generated.hardware_pb2 import Cpu, Ram
from ..generated.machine_info_pb2 import _MACHINEINFO, MachineInfo
from .custom import (SqliteType,
                     get_event_table_insertion_cmds_for_nested_messages,
                     get_fun_to_collect_latest_update_events_from_db,
                     get_fun_to_collect_pb2_messages_for_nested_submessages,
                     get_function_to_retrieve_pb2_from_sqlite_db,
                     get_state_table_modification_fun_for_nested_messages,
                     sqlite_create_event_tbl_cmd_from_pb2,
                     sqlite_create_state_tbl_cmd_from_pb2,
                     sqlite_insert_into_table_fun_from_pb2)
from .generic import ProtoType

insert_update_event_in_db = get_event_table_insertion_cmds_for_nested_messages(
    _UPDATEEVENT)

update_state_tables_in_db = \
    get_state_table_modification_fun_for_nested_messages(
        _UPDATEEVENT
    )

get_computer_info_from_db = get_fun_to_collect_pb2_messages_for_nested_submessages(
    pb_class=ComputerInfo,
    key_names_and_ops=[("machine_id", "=")],
    table_suffix="",
)

get_update_events_from_db = get_fun_to_collect_latest_update_events_from_db(
    pb_class=UpdateEvent,
    key_names_and_ops=[
        ("timestamp", ">="),
        ("timestamp", "<"),
    ],
    table_suffix="Events",
)

get_machine_infos_from_db = get_function_to_retrieve_pb2_from_sqlite_db(
    table_suffix="",
    pb_class=MachineInfo,
    key_names_and_ops=[],
)

get_cpu_for_machine_from_db = get_function_to_retrieve_pb2_from_sqlite_db(
    table_suffix="",
    pb_class=Cpu,
    key_names_and_ops=[
        ("machine_id", "==")
    ],
)

get_ram_for_machine_from_db = get_function_to_retrieve_pb2_from_sqlite_db(
    table_suffix="",
    pb_class=Ram,
    key_names_and_ops=[
        ("machine_id", "==")
    ],
)

insert_machine_info_in_db = sqlite_insert_into_table_fun_from_pb2(
    table_name=_MACHINEINFO.name,
    meta_attribute_names=[],
    pb_descriptor=_MACHINEINFO,
    fields_to_ignore=[],
)

SQL_CREATE_MACHINE_TBL_CMD = sqlite_create_state_tbl_cmd_from_pb2(
    _MACHINEINFO,
    meta_attributes=[],
    primary_key_names=[
        "machine_id",
    ],
    optional_primary_key_names=["id"]
)


ALL_SQL_CREATE_TABLE_CMDS = (
    # event tables
    tuple(
        sqlite_create_event_tbl_cmd_from_pb2(
            field.message_type,
            [
                ("timestamp", SqliteType.REAL),
                ("machine_id", SqliteType.INTEGER),
                ("event_type", SqliteType.INTEGER),
            ],
            primary_key_names=[
                "timestamp",
                "machine_id",
                # id is sometimes hacked in this is not nice ...
            ],
            optional_primary_key_names=["id"],
        )
        for field in _UPDATEEVENT.fields
        if field.type == ProtoType.MESSAGE.value
    ) +
    # latest state tables
    tuple(
        sqlite_create_state_tbl_cmd_from_pb2(
            field.message_type,
            meta_attributes=[
                ("machine_id", SqliteType.INTEGER),
            ],
            primary_key_names=["machine_id"],
            optional_primary_key_names=["id"],
        )
        for field in _UPDATEEVENT.fields
        if field.type == ProtoType.MESSAGE.value
    ) +
    # machine metadata table
    (SQL_CREATE_MACHINE_TBL_CMD, )
)
