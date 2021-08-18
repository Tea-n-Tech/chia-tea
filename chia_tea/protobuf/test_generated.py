
import unittest

from chia_tea.protobuf.to_sqlite.generic import (ProtoType,
                                                 field_descriptor_is_list)

from .generated.computer_info_pb2 import _COMPUTERINFO, _UPDATEEVENT
from .generated.config_pb2 import \
    _MONITORINGCONFIG_CLIENTCONFIG_SENDUPDATEEVERY


class TestGenerated(unittest.TestCase):

    def test_send_update_every_matches_update_event_names(self):

        update_event_fields = set(
            field.name
            for field in _UPDATEEVENT.fields
            if field.type == ProtoType.MESSAGE.value
        )

        send_update_every_fields = set(
            field.name
            for field in _MONITORINGCONFIG_CLIENTCONFIG_SENDUPDATEEVERY.fields
        )

        missing_fields = update_event_fields - send_update_every_fields
        self.assertSetEqual(missing_fields, set())

        invalid_fields = send_update_every_fields - update_event_fields
        self.assertSetEqual(invalid_fields, set())

    def test_that_update_event_and_computer_info_have_same_field_types(self):

        update_event_message_types = set(
            field.message_type
            for field in _COMPUTERINFO.fields
            if field.message_type == ProtoType.MESSAGE.value
        )

        computer_info_message_types = set(
            field.message_type
            for field in _COMPUTERINFO.fields
            if field.message_type == ProtoType.MESSAGE.value
        )

        self.assertSetEqual(update_event_message_types,
                            computer_info_message_types)

    def test_that_every_array_message_in_computer_info_has_an_id_entry(self):

        for field in _COMPUTERINFO.fields:

            if field.message_type != ProtoType.MESSAGE.value:
                continue

            submessage_type = field.message_type

            if field_descriptor_is_list(submessage_type):
                msg_field_names = list(submessage_type.fields_by_name)
                self.assertTrue(
                    "id" in msg_field_names,
                    "Message type '{0}' is a repeated field and must contain an entry 'id'.".format(
                        submessage_type.name
                    )
                )
