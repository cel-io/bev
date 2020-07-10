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

        if payload.action == payload_pb2.BevPayload.CREATE_ELECTION:
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
        elif payload.action == payload_pb2.BevPayload.UPDATE_VOTING_OPTION:
            _update_voting_option(
                state=state,
                public_key=header.signer_public_key,
                payload=payload)
        elif payload.action == payload_pb2.BevPayload.UPDATE_POLL_REGISTRATION:
            _update_poll_registration(
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
        election_id=payload.data.election_id,
        status=payload.data.status
    )


def _create_poll_registration(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Agent with the public key {} does '
                                 'not exist'.format(public_key))

    state.set_poll_registration(
        voter_id=payload.data.voter_id,
        name=payload.data.name,
        election_id=payload.data.election_id,
        status=payload.data.status
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
    state.update_voter(
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


def _update_voting_option(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Agent with the public key {} does '
                                 'not exist'.format(public_key))

    state.update_voting_option(
        voting_option_id=payload.data.voting_option_id,
        name=payload.data.name,
        description=payload.data.description,
        election_id=payload.data.election_id,
        status=payload.data.status
    )


def _update_poll_registration(state, public_key, payload):
    if state.get_voter(public_key) is None:
        raise InvalidTransaction('Agent with the public key {} does '
                                 'not exist'.format(public_key))

    state.update_poll_registration(
        voter_id=payload.data.voter_id,
        name=payload.data.name,
        election_id=payload.data.election_id,
        status=payload.data.status
    )


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
