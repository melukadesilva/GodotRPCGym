# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: observation_action.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x18observation_action.proto\x12\x03rlc\"\x07\n\x05\x45mpty\"H\n\x0fObservationData\x12\x14\n\x0cobservations\x18\x01 \x03(\x02\x12\x0e\n\x06reward\x18\x02 \x01(\x02\x12\x0f\n\x07is_done\x18\x03 \x01(\x03\"6\n\nActionData\x12\x14\n\x0c\x61\x63tion_index\x18\x01 \x03(\x02\x12\x12\n\nenv_action\x18\x02 \x01(\x03\x32\x8a\x01\n\x03RLC\x12/\n\x04Step\x12\x0f.rlc.ActionData\x1a\x14.rlc.ObservationData\"\x00\x12+\n\x05Reset\x12\n.rlc.Empty\x1a\x14.rlc.ObservationData\"\x00\x12%\n\tTerminate\x12\n.rlc.Empty\x1a\n.rlc.Empty\"\x00\x62\x06proto3')



_EMPTY = DESCRIPTOR.message_types_by_name['Empty']
_OBSERVATIONDATA = DESCRIPTOR.message_types_by_name['ObservationData']
_ACTIONDATA = DESCRIPTOR.message_types_by_name['ActionData']
Empty = _reflection.GeneratedProtocolMessageType('Empty', (_message.Message,), {
  'DESCRIPTOR' : _EMPTY,
  '__module__' : 'observation_action_pb2'
  # @@protoc_insertion_point(class_scope:rlc.Empty)
  })
_sym_db.RegisterMessage(Empty)

ObservationData = _reflection.GeneratedProtocolMessageType('ObservationData', (_message.Message,), {
  'DESCRIPTOR' : _OBSERVATIONDATA,
  '__module__' : 'observation_action_pb2'
  # @@protoc_insertion_point(class_scope:rlc.ObservationData)
  })
_sym_db.RegisterMessage(ObservationData)

ActionData = _reflection.GeneratedProtocolMessageType('ActionData', (_message.Message,), {
  'DESCRIPTOR' : _ACTIONDATA,
  '__module__' : 'observation_action_pb2'
  # @@protoc_insertion_point(class_scope:rlc.ActionData)
  })
_sym_db.RegisterMessage(ActionData)

_RLC = DESCRIPTOR.services_by_name['RLC']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EMPTY._serialized_start=33
  _EMPTY._serialized_end=40
  _OBSERVATIONDATA._serialized_start=42
  _OBSERVATIONDATA._serialized_end=114
  _ACTIONDATA._serialized_start=116
  _ACTIONDATA._serialized_end=170
  _RLC._serialized_start=173
  _RLC._serialized_end=311
# @@protoc_insertion_point(module_scope)
