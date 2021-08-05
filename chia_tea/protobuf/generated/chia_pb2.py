# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chia_tea/protobuf/generated/chia.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='chia_tea/protobuf/generated/chia.proto',
  package='chia_tea.protobuf.generated.chia_pb2',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n&chia_tea/protobuf/generated/chia.proto\x12$chia_tea.protobuf.generated.chia_pb2\"\xdc\x01\n\x0bProcessInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\nexecutable\x18\x02 \x01(\t\x12\x0f\n\x07\x63ommand\x18\x03 \x01(\t\x12\x13\n\x0b\x63reate_time\x18\x04 \x01(\x01\x12\n\n\x02id\x18\x05 \x01(\x03\x12\x11\n\tcpu_usage\x18\x06 \x01(\x02\x12\x19\n\x11used_physical_ram\x18\x07 \x01(\x02\x12\x18\n\x10used_virtual_ram\x18\x08 \x01(\x02\x12\x14\n\x0copened_files\x18\t \x01(\t\x12\x1b\n\x13network_connections\x18\n \x01(\t\"\xc4\x01\n\rHarvesterPlot\x12\n\n\x02id\x18\n \x01(\t\x12\x10\n\x08\x66ilename\x18\x03 \x01(\t\x12\x10\n\x08\x66ilesize\x18\x04 \x01(\x03\x12!\n\x19pool_contract_puzzle_hash\x18\x06 \x01(\t\x12\x17\n\x0fpool_public_key\x18\x07 \x01(\t\x12\x0c\n\x04size\x18\x08 \x01(\x03\x12\x15\n\rtime_modified\x18\t \x01(\x01\x12\x11\n\tplot_seed\x18\x01 \x01(\t\x12\x0f\n\x07\x64isk_id\x18\x02 \x01(\t\"5\n\rHarvesterInfo\x12\x12\n\nis_running\x18\x02 \x01(\x08\x12\x10\n\x08n_proofs\x18\x03 \x01(\x03\"\xaf\x01\n\x19HarvesterViewedFromFarmer\x12\n\n\x02id\x18\x01 \x01(\t\x12\x17\n\x0f\x63onnection_time\x18\x08 \x01(\x01\x12\x19\n\x11last_message_time\x18\t \x01(\x01\x12\x12\n\nip_address\x18\n \x01(\t\x12\x12\n\nn_timeouts\x18\x0b \x01(\x03\x12\x19\n\x11missed_challenges\x18\x06 \x01(\x03\x12\x0f\n\x07n_plots\x18\x02 \x01(\x03\":\n\nFarmerInfo\x12\x12\n\nis_running\x18\x01 \x01(\x08\x12\x18\n\x10total_challenges\x18\x02 \x01(\x03\"3\n\nWalletInfo\x12\x12\n\nis_running\x18\x01 \x01(\x08\x12\x11\n\tis_synced\x18\x02 \x01(\x08\"K\n\x0bPlottingJob\x12\x1b\n\x13n_plots_in_progress\x18\x01 \x01(\x03\x12\x1f\n\x17n_plots_completed_today\x18\x02 \x01(\x03\x62\x06proto3'
)




_PROCESSINFO = _descriptor.Descriptor(
  name='ProcessInfo',
  full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='executable', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.executable', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='command', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.command', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='create_time', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.create_time', index=3,
      number=4, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='id', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.id', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='cpu_usage', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.cpu_usage', index=5,
      number=6, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='used_physical_ram', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.used_physical_ram', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='used_virtual_ram', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.used_virtual_ram', index=7,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='opened_files', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.opened_files', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='network_connections', full_name='chia_tea.protobuf.generated.chia_pb2.ProcessInfo.network_connections', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=81,
  serialized_end=301,
)


_HARVESTERPLOT = _descriptor.Descriptor(
  name='HarvesterPlot',
  full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.id', index=0,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='filename', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.filename', index=1,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='filesize', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.filesize', index=2,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='pool_contract_puzzle_hash', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.pool_contract_puzzle_hash', index=3,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='pool_public_key', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.pool_public_key', index=4,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='size', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.size', index=5,
      number=8, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='time_modified', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.time_modified', index=6,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='plot_seed', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.plot_seed', index=7,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='disk_id', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterPlot.disk_id', index=8,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=304,
  serialized_end=500,
)


_HARVESTERINFO = _descriptor.Descriptor(
  name='HarvesterInfo',
  full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='is_running', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterInfo.is_running', index=0,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='n_proofs', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterInfo.n_proofs', index=1,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=502,
  serialized_end=555,
)


_HARVESTERVIEWEDFROMFARMER = _descriptor.Descriptor(
  name='HarvesterViewedFromFarmer',
  full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='connection_time', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer.connection_time', index=1,
      number=8, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='last_message_time', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer.last_message_time', index=2,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ip_address', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer.ip_address', index=3,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='n_timeouts', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer.n_timeouts', index=4,
      number=11, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='missed_challenges', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer.missed_challenges', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='n_plots', full_name='chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer.n_plots', index=6,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=558,
  serialized_end=733,
)


_FARMERINFO = _descriptor.Descriptor(
  name='FarmerInfo',
  full_name='chia_tea.protobuf.generated.chia_pb2.FarmerInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='is_running', full_name='chia_tea.protobuf.generated.chia_pb2.FarmerInfo.is_running', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='total_challenges', full_name='chia_tea.protobuf.generated.chia_pb2.FarmerInfo.total_challenges', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=735,
  serialized_end=793,
)


_WALLETINFO = _descriptor.Descriptor(
  name='WalletInfo',
  full_name='chia_tea.protobuf.generated.chia_pb2.WalletInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='is_running', full_name='chia_tea.protobuf.generated.chia_pb2.WalletInfo.is_running', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='is_synced', full_name='chia_tea.protobuf.generated.chia_pb2.WalletInfo.is_synced', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=795,
  serialized_end=846,
)


_PLOTTINGJOB = _descriptor.Descriptor(
  name='PlottingJob',
  full_name='chia_tea.protobuf.generated.chia_pb2.PlottingJob',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='n_plots_in_progress', full_name='chia_tea.protobuf.generated.chia_pb2.PlottingJob.n_plots_in_progress', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='n_plots_completed_today', full_name='chia_tea.protobuf.generated.chia_pb2.PlottingJob.n_plots_completed_today', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=848,
  serialized_end=923,
)

DESCRIPTOR.message_types_by_name['ProcessInfo'] = _PROCESSINFO
DESCRIPTOR.message_types_by_name['HarvesterPlot'] = _HARVESTERPLOT
DESCRIPTOR.message_types_by_name['HarvesterInfo'] = _HARVESTERINFO
DESCRIPTOR.message_types_by_name['HarvesterViewedFromFarmer'] = _HARVESTERVIEWEDFROMFARMER
DESCRIPTOR.message_types_by_name['FarmerInfo'] = _FARMERINFO
DESCRIPTOR.message_types_by_name['WalletInfo'] = _WALLETINFO
DESCRIPTOR.message_types_by_name['PlottingJob'] = _PLOTTINGJOB
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ProcessInfo = _reflection.GeneratedProtocolMessageType('ProcessInfo', (_message.Message,), {
  'DESCRIPTOR' : _PROCESSINFO,
  '__module__' : 'chia_tea.protobuf.generated.chia_pb2'
  # @@protoc_insertion_point(class_scope:chia_tea.protobuf.generated.chia_pb2.ProcessInfo)
  })
_sym_db.RegisterMessage(ProcessInfo)

HarvesterPlot = _reflection.GeneratedProtocolMessageType('HarvesterPlot', (_message.Message,), {
  'DESCRIPTOR' : _HARVESTERPLOT,
  '__module__' : 'chia_tea.protobuf.generated.chia_pb2'
  # @@protoc_insertion_point(class_scope:chia_tea.protobuf.generated.chia_pb2.HarvesterPlot)
  })
_sym_db.RegisterMessage(HarvesterPlot)

HarvesterInfo = _reflection.GeneratedProtocolMessageType('HarvesterInfo', (_message.Message,), {
  'DESCRIPTOR' : _HARVESTERINFO,
  '__module__' : 'chia_tea.protobuf.generated.chia_pb2'
  # @@protoc_insertion_point(class_scope:chia_tea.protobuf.generated.chia_pb2.HarvesterInfo)
  })
_sym_db.RegisterMessage(HarvesterInfo)

HarvesterViewedFromFarmer = _reflection.GeneratedProtocolMessageType('HarvesterViewedFromFarmer', (_message.Message,), {
  'DESCRIPTOR' : _HARVESTERVIEWEDFROMFARMER,
  '__module__' : 'chia_tea.protobuf.generated.chia_pb2'
  # @@protoc_insertion_point(class_scope:chia_tea.protobuf.generated.chia_pb2.HarvesterViewedFromFarmer)
  })
_sym_db.RegisterMessage(HarvesterViewedFromFarmer)

FarmerInfo = _reflection.GeneratedProtocolMessageType('FarmerInfo', (_message.Message,), {
  'DESCRIPTOR' : _FARMERINFO,
  '__module__' : 'chia_tea.protobuf.generated.chia_pb2'
  # @@protoc_insertion_point(class_scope:chia_tea.protobuf.generated.chia_pb2.FarmerInfo)
  })
_sym_db.RegisterMessage(FarmerInfo)

WalletInfo = _reflection.GeneratedProtocolMessageType('WalletInfo', (_message.Message,), {
  'DESCRIPTOR' : _WALLETINFO,
  '__module__' : 'chia_tea.protobuf.generated.chia_pb2'
  # @@protoc_insertion_point(class_scope:chia_tea.protobuf.generated.chia_pb2.WalletInfo)
  })
_sym_db.RegisterMessage(WalletInfo)

PlottingJob = _reflection.GeneratedProtocolMessageType('PlottingJob', (_message.Message,), {
  'DESCRIPTOR' : _PLOTTINGJOB,
  '__module__' : 'chia_tea.protobuf.generated.chia_pb2'
  # @@protoc_insertion_point(class_scope:chia_tea.protobuf.generated.chia_pb2.PlottingJob)
  })
_sym_db.RegisterMessage(PlottingJob)


# @@protoc_insertion_point(module_scope)
