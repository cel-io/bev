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

        if self._transaction.HasField('update_voting_option') and \
            self._transaction.action == \
                payload_pb2.BevPayload.UPDATE_VOTING_OPTION:
            return self._transaction.update_voting_option

        if self._transaction.HasField('update_poll_registration') and \
            self._transaction.action == \
                payload_pb2.BevPayload.UPDATE_POLL_REGISTRATION:
            return self._transaction.update_poll_registration

        raise InvalidTransaction('Action does not match payload data')

    @property
    def timestamp(self):
        return self._transaction.timestamp
