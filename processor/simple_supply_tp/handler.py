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
# -----------------------------------------------------------------------------

import datetime
import time

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction

from simple_supply_addressing import addresser

from simple_supply_protobuf import payload_pb2

from simple_supply_tp.payload import BevPayload
from simple_supply_tp.state import SimpleSupplyState

SYNC_TOLERANCE = 60 * 5
MAX_LAT = 90 * 1e6
MIN_LAT = -90 * 1e6
MAX_LNG = 180 * 1e6
MIN_LNG = -180 * 1e6


class SimpleSupplyHandler(TransactionHandler):

    @property
    def family_name(self):
        return addresser.FAMILY_NAME

    @property
    def family_versions(self):
        return [addresser.FAMILY_VERSION]

    @property
    def namespaces(self):
        return [addresser.NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        payload = BevPayload(transaction.payload)
        state = SimpleSupplyState(context)

        _validate_timestamp(payload.timestamp)

        if payload.action == payload_pb2.BevPayload.CREATE_AGENT:
            _create_agent(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.CREATE_RECORD:
            _create_record(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.TRANSFER_RECORD:
            _transfer_record(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.UPDATE_RECORD:
            _update_record(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.CREATE_ELECTION:
            _create_election(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.CREATE_VOTING_OPTION:
            _create_voting_option(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.CREATE_POLL_REGISTRATION:
            _create_poll_registration(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.CREATE_VOTER:
            _create_voter(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.CREATE_VOTE:
            _create_vote(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.UPDATE_VOTE:
            _update_vote(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.UPDATE_ELECTION:
            _update_election(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.UPDATE_VOTER:
            _update_voter(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        else:
            raise InvalidTransaction('Unhandled action')


def _create_election(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Voter with the public key {} does '
                                 'not exist'.format(public_key))

    state.set_election(
        election_id=payload.data.election_id,
        name=payload.data.name,
        description=payload.data.description,
        start_timestamp=payload.data.start_timestamp,
        end_timestamp=payload.data.end_timestamp,
        results_permission=payload.data.results_permission,
        can_change_vote=payload.data.can_change_vote,
        can_show_realtime=payload.data.can_show_realtime,
        admin_id=payload.data.admin_id,
        status=payload.data.status,
        timestamp=payload.timestamp
    )


def _create_voting_option(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Agent with the public key {} does '
                                 'not exist'.format(public_key))

    state.set_voting_option(
        voting_option_id=payload.data.voting_option_id,
        name=payload.data.name,
        description=payload.data.description,
        election_id=payload.data.election_id
    )


def _create_poll_registration(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Agent with the public key {} does '
                                 'not exist'.format(public_key))

    state.set_poll_registration(
        voter_id=payload.data.voter_id,
        name=payload.data.name,
        election_id=payload.data.election_id
    )


def _create_voter(state, public_key, payload):
    if state.get_voter(public_key):
        raise InvalidTransaction('Voter with the public key {} already '
                                 'exists'.format(public_key))
    state.set_voter(
        voter_id=payload.data.voter_id,
        public_key=payload.data.public_key,
        name=payload.data.name,
        created_at=payload.data.created_at,
        type=payload.data.type)


def _update_voter(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Voter with the public key {} does '
                                 'not exists'.format(public_key))
    state.set_voter(
        voter_id=payload.data.voter_id,
        public_key=payload.data.public_key,
        name=payload.data.name,
        created_at=payload.data.created_at,
        type=payload.data.type)


def _create_vote(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Voter with the public key {} does '
                                 'not exist'.format(public_key))

    state.set_vote(
        vote_id=payload.data.vote_id,
        timestamp=payload.data.timestamp,
        voter_id=payload.data.voter_id,
        election_id=payload.data.election_id,
        voting_option_id=payload.data.voting_option_id
    )


def _update_vote(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Voter with the public key {} does '
                                 'not exist'.format(public_key))

    state.update_vote(
        vote_id=payload.data.vote_id,
        timestamp=payload.data.timestamp,
        voting_option_id=payload.data.voting_option_id
    )


def _update_election(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Voter with the public key {} does '
                                 'not exist'.format(public_key))

    state.update_election(
        election_id=payload.data.election_id,
        status=payload.data.status,
        timestamp=payload.timestamp
    )


def _create_agent(state, public_key, payload):
    if state.get_agent(public_key):
        raise InvalidTransaction('Agent with the public key {} already '
                                 'exists'.format(public_key))
    state.set_agent(
        public_key=public_key,
        name=payload.data.name,
        timestamp=payload.timestamp)


def _create_record(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Agent with the public key {} does '
                                 'not exist'.format(public_key))

    if payload.data.record_id == '':
        raise InvalidTransaction('No record ID provided')

    if state.get_record(payload.data.record_id):
        raise InvalidTransaction('Identifier {} belongs to an existing '
                                 'record'.format(payload.data.record_id))

    _validate_latlng(payload.data.latitude, payload.data.longitude)

    state.set_record(
        public_key=public_key,
        latitude=payload.data.latitude,
        longitude=payload.data.longitude,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)


def _transfer_record(state, public_key, payload):
    if state.get_voter(payload.data.receiving_agent) is None:
        raise InvalidTransaction(
            'Agent with the public key {} does '
            'not exist'.format(payload.data.receiving_agent))

    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not '
                                 'exist'.format(payload.data.record_id))

    if not _validate_record_owner(signer_public_key=public_key,
                                  record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record')

    state.transfer_record(
        receiving_agent=payload.data.receiving_agent,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)


def _update_record(state, public_key, payload):
    record = state.get_record(payload.data.record_id)
    if record is None:
        raise InvalidTransaction('Record with the record id {} does not '
                                 'exist'.format(payload.data.record_id))

    if not _validate_record_owner(signer_public_key=public_key,
                                  record=record):
        raise InvalidTransaction(
            'Transaction signer is not the owner of the record')

    _validate_latlng(payload.data.latitude, payload.data.longitude)

    state.update_record(
        latitude=payload.data.latitude,
        longitude=payload.data.longitude,
        record_id=payload.data.record_id,
        timestamp=payload.timestamp)


def _validate_record_owner(signer_public_key, record):
    """Validates that the public key of the signer is the latest (i.e.
    current) owner of the record
    """
    latest_owner = max(record.owners, key=lambda obj: obj.timestamp).agent_id
    return latest_owner == signer_public_key


def _validate_latlng(latitude, longitude):
    if not MIN_LAT <= latitude <= MAX_LAT:
        raise InvalidTransaction('Latitude must be between -90 and 90. '
                                 'Got {}'.format(latitude / 1e6))
    if not MIN_LNG <= longitude <= MAX_LNG:
        raise InvalidTransaction('Longitude must be between -180 and 180. '
                                 'Got {}'.format(longitude / 1e6))


def _validate_timestamp(timestamp):
    """Validates that the client submitted timestamp for a transaction is not
    greater than current time, within a tolerance defined by SYNC_TOLERANCE

    NOTE: Timestamp validation can be challenging since the machines that are
    submitting and validating transactions may have different system times
    """
    dts = datetime.datetime.utcnow()
    current_time = round(time.mktime(dts.timetuple()) + dts.microsecond / 1e6)
    if (timestamp - current_time) > SYNC_TOLERANCE:
        raise InvalidTransaction(
            'Timestamp must be less than local time.'
            ' Expected {0} in ({1}-{2}, {1}+{2})'.format(
                timestamp, current_time, SYNC_TOLERANCE))
