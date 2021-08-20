
import enum
import traceback
from typing import List, Tuple

from google.protobuf.descriptor import Descriptor, FieldDescriptor


class ProtoType(enum.Enum):
    """ Protobuf enum types

    Notes
    -----
        For protobuf type enums see:
        https://developers.google.com/protocol-buffers/docs/reference/cpp/google.protobuf.descriptor.pb
    """
    DOUBLE = 1
    FLOAT = 2
    INT64 = 3
    UINT64 = 4
    INT32 = 5
    FIXED64 = 6
    FIXED32 = 7
    BOOL = 8
    STRING = 9
    GROUP = 10
    MESSAGE = 11
    BYTES = 12
    UINT32 = 13
    ENUM = 14
    SFIXED32 = 15
    SFIXED64 = 16
    SINT32 = 17
    SINT64 = 18


class SqliteType(enum.Enum):
    """ Enum for sqlite3 datatypes """
    REAL = "READ"
    INTEGER = "INTEGER"
    STRING = "STRING"
    BLOB = "BLOB"


def field_descriptor_is_list(
    field_descriptor: FieldDescriptor
) -> bool:
    """ Checks if a proto field is a list or not

    Parameters
    ----------
    field_descriptor : FieldDescriptor
        descriptor of a field within a proto msg

    Returns
    -------
    is_list : bool
    """
    return isinstance(field_descriptor.default_value, list)


def sql_type_from_proto_type(
    proto_type: int,
    message_name: str,
    field_name: str,
) -> SqliteType:
    """ Translate protobuf types into sqlite types

    Parameters
    ----------
    proto_type : int
        protobuf type enum
    message_name : str
        message name for better error messages
    field_name : str
        field name for better error messages

    Returns
    -------
    sqlite_type : SqliteType
        enum type of sqlite type

    Notes
    -----
        For protobuf type enums see:
        https://developers.google.com/protocol-buffers/docs/reference/cpp/google.protobuf.descriptor.pb
    """
    if proto_type in (
            ProtoType.DOUBLE.value,
            ProtoType.FLOAT.value):
        return SqliteType.REAL

    if proto_type in (
            ProtoType.INT64.value,
            ProtoType.UINT64.value,
            ProtoType.INT32.value,
            ProtoType.FIXED64.value,
            ProtoType.FIXED32.value,
            ProtoType.BOOL.value,
            ProtoType.UINT32.value,
            ProtoType.SFIXED32.value,
            ProtoType.SFIXED64.value,
            ProtoType.SINT32.value,
            ProtoType.SINT64.value,
    ):
        return SqliteType.INTEGER

    if proto_type == ProtoType.STRING.value:
        return SqliteType.STRING

    if proto_type == ProtoType.BYTES.value:
        return SqliteType.BLOB

    err_msg = (f"{message_name}.{field_name} " +
               f"has an unknown protobuf type enum: {proto_type}")
    raise RuntimeError(err_msg)


def get_proto_fields_with_types(
        pb_descriptor: Descriptor
) -> List[Tuple[str, SqliteType]]:
    """ Get the proto field names of a descriptor with types

    Parameters
    ----------
    pb_descriptor: descriptor.Descriptor
        descriptor from protobuf basically describing a message

    Returns
    -------
    fields : List[Tuple[str, SqliteType]]
        fields with (name, type) tuple
    """
    try:
        return [
            (
                field.name,
                sql_type_from_proto_type(
                    field.type,
                    pb_descriptor.full_name,
                    field.name)
            )
            for field in pb_descriptor.fields
        ]
    except RuntimeError:
        err_msg = traceback.format_exc(
        ) + f"\nError in {pb_descriptor.full_name}"
        raise RuntimeError(err_msg) from None


def get_sqlite_fields_for_insertion_from_pb2(
    pb_descriptor: Descriptor
) -> str:
    """ Converts proto fields from a proto descriptor into sqlite fields
    for table insertion

    Parameters
    ----------
    pb_descriptor: descriptor.Descriptor
        descriptor from protobuf basically describing a message

    Returns
    -------
    fields : str
        string usable for table insertion
    """
    field_name_and_type = get_proto_fields_with_types(pb_descriptor)
    field_names_prepped = (
        f"'{name}'" for (name, _) in field_name_and_type
    )
    return ",".join(field_names_prepped)


def get_create_table_cmd(
    table_name: str,
    attributes: List[Tuple[str, SqliteType]],
    primary_key_attribute_names: List[str],
) -> str:
    """ Get the command to create a sqlite table from the
    definition of the attributes

    Parameters
    ----------
    table_name : str
        name of the table
    attributes : Dict[str, SqliteType]
        attributes to store in the sqlite table
    key_attribute_names : List[str]
        names of the attributes used as keys

    Returns
    -------
    create_tbl_cmd : str
        command for sqlite to create a table
    """

    format_str = "{0} {1}"
    name_and_type_as_str = (
        format_str.format(attribute_name, attribute_type.value)
        for attribute_name, attribute_type in attributes
    )
    attribute_string = ", ".join(name_and_type_as_str)

    return (
        f"CREATE TABLE IF NOT EXISTS {table_name}("
        + attribute_string
        + ",PRIMARY KEY("
        + ",".join(primary_key_attribute_names)
        + ")"
        + ")"
    )


def sqlite_create_tbl_cmd_from_pb2(
    table_name: str,
    meta_attributes: List[Tuple[str, SqliteType]],
    primary_key_attribute_names: List[str],
    pb_descriptor: Descriptor,
) -> str:
    """ Get the table creation command from a proto msg

    Parameters
    ----------
    table_name : str
        name of the table
    meta_attributes : List[Tuple[str, SqliteType]]
        additional attributes to store in the sqlite table
    pb_descriptor : descriptor.Descriptor
        proto message to be stored

    Returns
    -------
    create_tbl_cmd : str
        command for sqlite to create a table
    """

    pb2_attributes = get_proto_fields_with_types(pb_descriptor)

    # enforce unique naming to be safe
    set_meta_names = set(name for name, _ in meta_attributes)
    set_pb2_names = set(name for name, _ in pb2_attributes)
    duplicate_names = set_meta_names.intersection(set_pb2_names)
    if duplicate_names:
        err_msg = ("The following meta names intersect " +
                   "with protobuf message names: {0}")
        raise ValueError(err_msg.format(
            ", ".join(duplicate_names)
        ))

    set_primary_names = set(primary_key_attribute_names)
    set_all_attribute_names = set_meta_names.union(set_pb2_names)
    missing_attributes = set_primary_names - set_all_attribute_names
    if missing_attributes:
        err_msg = (
            "The following primary key attribute names do" +
            " neither exist in the proto file nor the additionally" +
            " specified attributes: " +
            ", ".join(missing_attributes)
        )

    return get_create_table_cmd(
        table_name=table_name,
        attributes=meta_attributes+pb2_attributes,
        primary_key_attribute_names=primary_key_attribute_names
    )
