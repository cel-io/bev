# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

from sawtooth_sdk.processor.exceptions import InvalidTransaction

from simple_supply_protobuf import payload_pb2


class BevPayload(object):

    def __init__(self, payload):
        self._transaction = payload_pb2.BevPayload()
        self._transaction.ParseFromString(payload)

    @property
    def action(self):
        return self._transaction.action

    @property
    def data(self):
        if self._transaction.HasField('create_election') and \
            self._transaction.action == \
                payload_pb2.BevPayload.CREATE_ELECTION:
            return self._transaction.create_election

        if self._transaction.HasField('create_voting_option') and \
            self._transaction.action == \
                payload_pb2.BevPayload.CREATE_VOTING_OPTION:
            return self._transaction.create_voting_option

        if self._transaction.HasField('create_poll_registration') and \
            self._transaction.action == \
                payload_pb2.BevPayload.CREATE_POLL_REGISTRATION:
            return self._transaction.create_poll_registration

        if self._transaction.HasField('create_voter') and \
            self._transaction.action == \
                payload_pb2.BevPayload.CREATE_VOTER:
            return self._transaction.create_voter

        if self._transaction.HasField('create_vote') and \
            self._transaction.action == \
                payload_pb2.BevPayload.CREATE_VOTE:
            return self._transaction.create_vote

        if self._transaction.HasField('update_vote') and \
            self._transaction.action == \
                payload_pb2.BevPayload.UPDATE_VOTE:
            return self._transaction.update_vote

        if self._transaction.HasField('update_election') and \
            self._transaction.action == \
                payload_pb2.BevPayload.UPDATE_ELECTION:
            return self._transaction.update_election

        if self._transaction.HasField('update_voter') and \
            self._transaction.action == \
                payload_pb2.BevPayload.UPDATE_VOTER:
            return self._transaction.update_voter

        if self._transaction.HasField('create_agent') and \
            self._transaction.action == \
                payload_pb2.BevPayload.CREATE_AGENT:
            return self._transaction.create_agent

        if self._transaction.HasField('create_record') and \
            self._transaction.action == \
                payload_pb2.BevPayload.CREATE_RECORD:
            return self._transaction.create_record

        if self._transaction.HasField('transfer_record') and \
            self._transaction.action == \
                payload_pb2.BevPayload.TRANSFER_RECORD:
            return self._transaction.transfer_record

        if self._transaction.HasField('update_record') and \
            self._transaction.action == \
                payload_pb2.BevPayload.UPDATE_RECORD:
            return self._transaction.update_record

        raise InvalidTransaction('Action does not match payload data')

    @property
    def timestamp(self):
        return self._transaction.timestamp
