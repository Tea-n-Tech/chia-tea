
import importlib
import sqlite3
from collections.abc import Iterable
from typing import Any, Callable, Dict, List, Tuple

from google.protobuf.descriptor import Descriptor
from google.protobuf.message import Message

from ..generated.computer_info_pb2 import (ADD, DELETE, NONE, UPDATE,
                                           UpdateEvent)
from .generic import (ProtoType, SqliteType, field_descriptor_is_list,
                      get_proto_fields_with_types,
                      sqlite_create_tbl_cmd_from_pb2)

TableInsertionFunc = Callable[[sqlite3.Cursor, Any, Dict[str, Any]], None]
TableDeletionFunc = Callable[[sqlite3.Cursor, Any, int], None]


EVENT_TABLE_META_ATTRIBUTES = [
    ("timestamp", SqliteType.REAL),
    ("machine_id", SqliteType.INTEGER),
    ("event_type", SqliteType.INTEGER),
]

STATE_TABLE_META_ATTRIBUTES = [
    ("machine_id", SqliteType.INTEGER),
]


def sqlite_create_event_tbl_cmd_from_pb2(
    pb_descriptor: Descriptor,
    meta_attributes: List[Tuple[str, SqliteType]],
    primary_key_names: List[str],
    optional_primary_key_names: List[str],
) -> str:
    """ Get a sqlite table creation cmd (if not exists)
    from a proto message descriptor

    Parameters
    ----------
    pb_descriptor: Descriptor
        descriptor from protobuf basically describing a message
    meta_attributes : List[Tuple[str, SqliteType]]
        meta attributes to store besides proto data
    primary_key_names : List[str]
        var names used for the primary key
    optional_primary_key_names : List[str]
        optional primary keys which are added if they are
        contained within the proto msg or meta_attributes
    Returns
    -------
    cmd : str
        command for execution
    """
    table_name = pb_descriptor.name+"Events"

    all_var_names = [
        field.name for field in pb_descriptor.fields
    ] + [
        name for name, _ in meta_attributes
    ]

    for key_name in primary_key_names:
        if key_name not in all_var_names:
            err_msg = "primary key attribute '{0}' does not match any var: {1}"
            raise ValueError(err_msg.format(
                key_name,
                all_var_names
            ))

    for additional_name in optional_primary_key_names:
        for field in pb_descriptor.fields:
            if field.name == additional_name:
                primary_key_names = [
                    *primary_key_names,
                    additional_name,
                ]

    return sqlite_create_tbl_cmd_from_pb2(
        table_name=table_name,
        meta_attributes=meta_attributes,
        primary_key_attribute_names=primary_key_names,
        pb_descriptor=pb_descriptor,
    )


def sqlite_create_state_tbl_cmd_from_pb2(
    pb_descriptor: Descriptor,
    meta_attributes: List[Tuple[str, SqliteType]],
    primary_key_names: List[str],
    optional_primary_key_names: List[str],
) -> str:
    """ Get a sqlite table creation cmd (if not exists)
    from a proto message descriptor

    Parameters
    ----------
    pb_descriptor: Descriptor
        descriptor from protobuf basically describing a message
    meta_attributes : List[Tuple[str, SqliteType]]
        meta attributes to store besides proto data
    primary_key_names : List[str]
        var names used for the primary key
    optional_primary_key_names : List[str]
        optional primary keys which are added if they are
        contained within the proto msg or meta_attributes

    Returns
    -------
    cmd : str
        command for execution
    """
    table_name = pb_descriptor.name

    all_var_names = [
        field.name for field in pb_descriptor.fields
    ] + [
        name for name, _ in meta_attributes
    ]

    for key_name in primary_key_names:
        if key_name not in all_var_names:
            err_msg = "primary key attribute '{0}' does not match any var: {1}"
            raise ValueError(err_msg.format(
                key_name,
                all_var_names
            ))

    for additional_name in optional_primary_key_names:
        for field in pb_descriptor.fields:
            if field.name == additional_name:
                primary_key_names = [
                    *primary_key_names,
                    additional_name,
                ]

    return sqlite_create_tbl_cmd_from_pb2(
        table_name=table_name,
        meta_attributes=meta_attributes,
        primary_key_attribute_names=primary_key_names,
        pb_descriptor=pb_descriptor,
    )


def sqlite_insert_into_table_fun_from_pb2(
    table_name: str,
    meta_attribute_names: List[str],
    pb_descriptor: Descriptor,
    fields_to_ignore: List[str],
) -> TableInsertionFunc:
    """ Create a function to insert a proto msg into sqlite
    from a pb2 message descriptor

    Parameters
    ----------
    table_name : str
        name of the sqlite table
    meta_attribute_names : List[str]
        names of the meta attributes
    pb_descriptor: Descriptor
        descriptor from protobuf basically describing a message
    fields_to_ignore : List[str]
        fields to ignore

    Returns
    -------
    function : Callable[[str, int, Any, sqlite.Cursor], None]
        function to insert a proto message into sqlite3
    """
    field_name_and_type = get_proto_fields_with_types(pb_descriptor)
    field_names = [
        field_name
        for field_name, _ in field_name_and_type
        if field_name not in fields_to_ignore
    ]

    all_attributes = meta_attribute_names+field_names
    all_names = ",".join(all_attributes)

    insertion_cmd = (
        f"INSERT OR REPLACE INTO {table_name} ("
        + all_names
        + ") "
        + "VALUES("
        + ",".join("?"*(len(all_attributes)))
        + ")"
    )

    def _table_insertion_function(
            sql_cursor: sqlite3.Cursor,
            pb_message: Message,
            meta_attributes: Dict[str, Any],
    ):
        if pb_message is None:
            return

        pb_message_iter = (pb_message,) \
            if not isinstance(pb_message, Iterable) \
            else pb_message

        # this must not fail
        meta_attribute_values = (
            meta_attributes[attribute_name]
            for attribute_name in meta_attribute_names
        )

        attributes = []
        for pb_entry in pb_message_iter:
            attributes.append(
                (
                    *meta_attribute_values,
                    *get_pb2_attributes_as_list(
                        pb_entry,
                        pb_descriptor,
                        fields_to_ignore=fields_to_ignore,
                    )
                )
            )

        sql_cursor.executemany(
            insertion_cmd,
            attributes,
        )

    return _table_insertion_function


def sqlite_delete_in_table_fun_from_pb2(
    table_name: str,
    meta_attribute_names: List[str],
    pb_descriptor: Descriptor,
) -> TableDeletionFunc:
    """ Create a function to delete a proto msg in a sqlite table
    from a pb2 message descriptor

    Parameters
    ----------
    table_name : str
        name of the sqlite table
    meta_attribute_names: List[str]
        names of the meta attributes used to
        identify which entry to delete
    pb_descriptor: Descriptor
        descriptor from protobuf describing a message

    Returns
    -------
    function : TableDeletionFunc
        function to insert a proto message into sqlite3
    """

    deletion_attributes = list(meta_attribute_names)

    # pylint: disable=unused-argument
    def _get_pb2_id(pb2_message) -> Tuple[Any, ...]:
        return tuple()

    has_id = any(field.name == "id" for field in pb_descriptor.fields)
    if has_id:
        deletion_attributes.append("id")

        def _get_pb2_id(pb_message: Message) -> Tuple[Any, ...]:  # noqa: F811
            return (pb_message.id,)

    deletion_cmd = (
        f"DELETE FROM {table_name} "
        + " WHERE "
        + " AND ".join(
            f"{name}=?"
            for name in deletion_attributes
        )
    )

    def _table_insertion_function(
            sql_cursor: sqlite3.Cursor,
            pb_message: Message,
            meta_attributes: Dict[str, Any],
    ):
        if pb_message is None:
            return

        pb_message_iter = (pb_message,) \
            if not isinstance(pb_message, Iterable) \
            else pb_message

        # this must not fail
        meta_attribute_values: Tuple[Any, ...] = tuple(
            meta_attributes[attribute_name]
            for attribute_name in meta_attribute_names
        )

        attributes = []
        for pb_entry in pb_message_iter:

            attributes.append(
                (
                    *meta_attribute_values,
                    *_get_pb2_id(
                        pb_entry,
                    )
                )
            )

        sql_cursor.executemany(
            deletion_cmd,
            attributes,
        )

    return _table_insertion_function


def get_pb2_attributes_as_list(
    pb_msg: Message,
    pb_descriptor: Descriptor,
    fields_to_ignore: List[str],
) -> List[Any]:
    """ Extract the attributes of a proto message into a list

    Parameters
    ----------
    pb_msg : Any
        protobuf message (from pb_descriptor)
    pb_descriptor: Descriptor
        descriptor from protobuf basically describing a message
    fields_to_ignore : List[str]
        which fields to ignore

    Returns
    -------
    attributes : List[Any]
        message attributes as list
    """
    return [
        getattr(pb_msg, field.name)
        for field in pb_descriptor.fields
        if field.name not in fields_to_ignore
    ]


def get_table_insertion_function_for_nested_messages(
    table_suffix: str,
    meta_attribute_names: List[str],
    pb_descriptor: Descriptor,
) -> TableInsertionFunc:
    """ Get command to insert nested submessages into their tables

    Parameters
    ----------
    table_suffix : str
        custom suffix for the table
    meta_attribute_names : List[str]
        names of the meta attributes
    pb_descriptor: Descriptor
        descriptor from protobuf basically a message

    Returns
    -------
    insertion_funtion : TableInsertionFunc
        function to insert the main message into the database

    Notes
    -----
        Requires to run `get_event_table_creation_cmds_for_nested_messages`
        first.
    """
    msgs_insertion_functions = {
        field.number: sqlite_insert_into_table_fun_from_pb2(
            field.message_type.name+table_suffix,
            meta_attribute_names,
            field.message_type,
            []
        )
        for field in pb_descriptor.fields
        if field.type == ProtoType.MESSAGE.value
    }

    def _insertion_function(
            sql_cursor: sqlite3.Cursor,
            pb_message: Any,
            meta_attributes: Dict[str, Any],
    ):

        field_name, pb_submessage = get_update_even_data(pb_message)
        field_number = pb_descriptor.fields_by_name[field_name].number

        fun = msgs_insertion_functions[field_number]
        fun(
            sql_cursor,
            pb_submessage,
            meta_attributes,
        )

    return _insertion_function


def get_event_table_insertion_cmds_for_nested_messages(
    pb_descriptor: Descriptor
) -> TableInsertionFunc:
    """ Get command to insert nested submessages into their tables

    Parameters
    ----------
    pb_descriptor: Descriptor
        descriptor from protobuf basically a message

    Returns
    -------
    insertion_funtion : TableInsertionFunc
        function to insert the main message into the database

    Notes
    -----
        Requires to run `get_event_table_creation_cmds_for_nested_messages`
        first.
    """
    return get_table_insertion_function_for_nested_messages(
        table_suffix="Events",
        meta_attribute_names=[
            name for name, _ in EVENT_TABLE_META_ATTRIBUTES
        ],
        pb_descriptor=pb_descriptor,
    )


StateModificationFun = Callable[
    [sqlite3.dbapi2.Cursor,
     Any,
     Dict[str, Any],
     int,
     ], Any]


def get_state_table_modification_fun_for_nested_messages(
    pb_descriptor: Descriptor
) -> StateModificationFun:
    """ Get command to insert nested submessages into their tables

    Parameters
    ----------
    pb_descriptor: Descriptor
        descriptor from protobuf basically a message

    Returns
    -------
    insertion_funtion : TableInsertionFunc
        function to insert the main message into the database
        Requires to run `get_state_table_creation_cmds_for_nested_messages`
        first.
    """
    table_suffix = ""
    meta_attribute_names = [
        name for name, _ in STATE_TABLE_META_ATTRIBUTES
    ]

    msgs_insertion_functions = {
        field.number: sqlite_insert_into_table_fun_from_pb2(
            field.message_type.name+table_suffix,
            meta_attribute_names,
            field.message_type,
            [],
        )
        for field in pb_descriptor.fields
        if field.type == ProtoType.MESSAGE.value
    }

    msgs_deletion_functions = {
        field.number: sqlite_delete_in_table_fun_from_pb2(
            field.message_type.name+table_suffix,
            meta_attribute_names,
            field.message_type)
        for field in pb_descriptor.fields
        if field.type == ProtoType.MESSAGE.value
    }

    def _deletion_function(
            sql_cursor: sqlite3.Cursor,
            pb_message: Any,
            meta_attributes: Dict[str, Any],
            event_type: int,
    ):

        if event_type == NONE:
            return

        field_name, pb_submessage = get_update_even_data(pb_message)
        field_number = pb_descriptor.fields_by_name[field_name].number

        if event_type in (ADD, UPDATE):
            fun = msgs_insertion_functions[field_number]
        elif event_type == DELETE:
            fun = msgs_deletion_functions[field_number]

        fun(
            sql_cursor,
            pb_submessage,
            meta_attributes,
        )

    return _deletion_function


def get_function_to_retrieve_pb2_from_sqlite_db(
    table_suffix: str,
    pb_class: Any,
    key_names_and_ops: List[Tuple[str, str]],
) -> Callable[[sqlite3.Cursor, List[Any]],
              Tuple[List[Message], List[Dict[str, Any]]]]:
    """ Get a function to read entries from the sqlite db
    and convert them abck into pb2 messages

    Parameters
    ----------
    table_suffix : str
        suffix for the table name (prefix is proto name)
    pb_class : Any
        protobuf class used to create a message
    key_names_and_ops : List[Tuple[str, str]]
        name of the columns used for retrieval and the operation
        associated with it such as '=' or '<'.

    Returns
    -------
    func : Callable[[sqlite3.Cursor, List[Any]], List[Message]]
        function for retrieving proto messages from the sqlite db
    """

    pb_descriptor = pb_class.DESCRIPTOR
    table_name = pb_descriptor.name + table_suffix

    selectors = " AND ".join(
        f"{name}{operation}?"
        for name, operation in key_names_and_ops
    )

    comparison_word = " WHERE " if selectors else ""

    cmd = (
        f"SELECT * FROM {table_name}" +
        comparison_word +
        selectors
    )

    def _get_state_as_pb(
        cursor: sqlite3.Cursor,
        *key_values: List[Any],
    ) -> Tuple[List[Message], List[Dict[str, Any]]]:

        cursor.execute(cmd, key_values)
        rows = cursor.fetchall()

        # this contains the names but if nothing is
        # found this is none
        description = cursor.description or tuple()

        entry_names = tuple(
            entry[0]
            for entry in description
        )

        pb_messages: List[Message] = []
        attributes = []
        for row in rows:
            pb_msg = pb_class()
            msg_attributes = {}
            for name, value in zip(entry_names, row):
                if hasattr(pb_msg, name):
                    setattr(pb_msg, name, value)
                else:
                    msg_attributes[name] = value
            pb_messages.append(pb_msg)
            attributes.append(msg_attributes)

        return pb_messages, attributes

    return _get_state_as_pb


def get_fun_to_collect_pb2_messages_for_nested_submessages(
    pb_class: Any,
    key_names_and_ops: List[Tuple[str, str]],
    table_suffix: str,
) -> Callable[[sqlite3.Cursor, List[Any]], Message]:
    """ Get a function to get a proto message with nested messages

    Parameters
    ----------
    pb_class : Any
        protobuf class used to create messages
    key_names_and_ops : List[Tuple[str, str]]
        name of the columns used for retrieval and the operation
        associated with it such as '=' or '<'.
    table_suffix : str
        suffix for the table name. Prefix is the proto class name

    Returns
    -------
    fun : Callable[[sqlite3.Cursor, List[Any]], Message]
        function to retrieve the proto message from the speified
        primary key attributes
    """

    pb_descriptor = pb_class.DESCRIPTOR

    msgs_retrieve_functions = {}
    msg_is_iterable = {}
    for field in pb_descriptor.fields:

        if field.type != ProtoType.MESSAGE.value:
            continue

        # We can only import a proto class here
        # when the module path is set correctly in
        # the proto file.

        # get the class from the proto msg descriptor
        message_descriptor = field.message_type
        module_name, class_name = message_descriptor.full_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        class_constructor = getattr(module, class_name)

        msgs_retrieve_functions[field.number] = \
            get_function_to_retrieve_pb2_from_sqlite_db(
                table_suffix=table_suffix,
                pb_class=class_constructor,
                key_names_and_ops=key_names_and_ops)
        msg_is_iterable[field.number] = \
            field_descriptor_is_list(field)

    def _retrieve_function(
        cursor: sqlite3.Cursor,
        primary_keys: List[Any],
    ):

        kwargs = {}
        for field in pb_descriptor.fields:

            if field.type != ProtoType.MESSAGE.value:
                continue

            fun = msgs_retrieve_functions[field.number]
            messages, attributes = fun(cursor, primary_keys)

            if msg_is_iterable[field.number]:
                kwargs[field.name] = messages
            else:
                kwargs[field.name] = messages[0] if messages else None

            if attributes:
                for attr_name, attr_value in attributes[0].items():
                    if attr_name in pb_descriptor.fields_by_name:
                        kwargs[attr_name] = attr_value

        return pb_class(**kwargs)

    return _retrieve_function


def get_fun_to_collect_latest_update_events_from_db(
    pb_class: Any,
    key_names_and_ops: List[Tuple[str, str]],
    table_suffix: str,
) -> Callable[[sqlite3.Cursor, Dict[str, Any]], Dict[int, List[UpdateEvent]]]:
    """ Get a function to get a proto message with nested messages

    Parameters
    ----------
    pb_class : Any
        protobuf class used to create messages
    key_names_and_ops : List[Tuple[str, str]]
        name of the columns used for retrieval and the operation
        associated with it such as '=' or '<' as string.
    table_suffix : str
        suffix for the table name. Prefix is the proto class name

    Returns
    -------
    fun : Callable[[sqlite3.Cursor, Dict[str, Any]], Dict[int, List[UpdateEvent]]]
        function to retrieve the proto message from the speified
        primary key attributes
    """

    pb_descriptor = pb_class.DESCRIPTOR

    msgs_retrieve_functions = {}
    for field in pb_descriptor.fields:

        if field.type != ProtoType.MESSAGE.value:
            continue

        # We can only import a proto class here
        # when the module path is set correctly in
        # the proto file.

        # get the class from the proto msg descriptor
        message_descriptor = field.message_type
        module_name, class_name = message_descriptor.full_name.rsplit(".", 1)
        module = importlib.import_module(module_name)
        class_constructor = getattr(module, class_name)

        msgs_retrieve_functions[field.number] = \
            get_function_to_retrieve_pb2_from_sqlite_db(
                table_suffix=table_suffix,
                pb_class=class_constructor,
                key_names_and_ops=key_names_and_ops)

    def _retrieve_function(
        cursor: sqlite3.Cursor,
        *key_values: List[Any],
    ) -> Dict[int, List[UpdateEvent]]:

        collected_events: Dict[int, List[UpdateEvent]] = {}

        for field in pb_descriptor.fields:

            if field.type != ProtoType.MESSAGE.value:
                continue

            fun = msgs_retrieve_functions[field.number]
            messages, attributes = fun(cursor, *key_values)

            for pb_submsg, attribute_dict in zip(messages, attributes):
                instance = pb_class(**{
                    field.name: pb_submsg
                })

                for name, value in attribute_dict.items():
                    if hasattr(instance, name):
                        setattr(instance, name, value)

                machine_id = attribute_dict["machine_id"]

                event_list = collected_events.get(machine_id, [])
                event_list.append(instance)
                collected_events[machine_id] = event_list

        return collected_events

    return _retrieve_function


def get_fun_to_update_db_from_pb2_class(
    pb_class: Any,
    key_names_and_ops: List[Tuple[str, str]],
    table_suffix: str,
    attribute_names: List[str],
) -> Callable[[sqlite3.Cursor, Message, Dict[str, Any], Dict[str, Any]], None]:
    """ Get a function to update database entries

    Parameters
    ----------
    pb_class : Any
        protobuf class used to create messages
    key_names_and_ops : List[Tuple[str, str]]
        name of the columns used for retrieval and the operation
        associated with it such as '=' or '<' as string.
    table_suffix : str
        suffix for the table name. Prefix is the proto class name
    attribute_names : List[str],
        additional attributes to modify

    Returns
    -------
    _update_table_fun : Callable[[sqlite3.Cursor, Message, Dict[str, Any], Dict[str, Any]], None]
        function to update table entries
    """

    pb_descriptor = pb_class.DESCRIPTOR
    table_name = pb_descriptor.name + table_suffix

    setter_fields = [
        f"{field.name}=?" for field in pb_descriptor.fields
    ]
    all_fields = attribute_names + setter_fields

    selectors = " AND ".join(
        f"{name}{operation}?"
        for name, operation in key_names_and_ops
    )
    comparison_word = " WHERE " if selectors else ""

    cmd = (
        f"UPDATE {table_name} " +
        "SET " +
        ",".join(all_fields) +
        comparison_word +
        selectors
    )

    def _update_table_fun(
        cursor: sqlite3.Cursor,
        pb_message: Message,
        attributes: Dict[str, Any],
        ops_values: List[Any],
    ):

        if pb_message is None:
            return

        pb_message_iter = (pb_message,) \
            if not isinstance(pb_message, Iterable) \
            else pb_message

        # this must not fail
        attribute_values_as_tuple: Tuple[Any, ...] = tuple(
            attributes[attribute_name]
            for attribute_name in attribute_names
        )

        values_to_insert_into_cmd = []
        for pb_entry in pb_message_iter:
            values_to_insert_into_cmd.append(
                (
                    *attribute_values_as_tuple,
                    *get_pb2_attributes_as_list(
                        pb_entry,
                        pb_descriptor,
                        fields_to_ignore=[],
                    ),
                    *ops_values,
                )
            )

        cursor.executemany(cmd, values_to_insert_into_cmd)

    return _update_table_fun


def get_update_even_data(
    update_event: UpdateEvent
) -> Tuple[str, Message]:
    """ Get the data of an update event

    Parameters
    ----------
    update_event : UpdateEvent
        event containing data update

    Returns
    -------
    name : str
        submessage variable name
    pb_msg : Message
        update event data
    """
    field_name = update_event.WhichOneof('event_data')
    sub_msg = getattr(
        update_event,
        field_name,
    )
    return field_name, sub_msg
