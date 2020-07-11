from sawtooth_rest_api.messaging import Connection
from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import validator_pb2
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context
from sawtooth_signing import secp256k1
from simple_supply_rest_api.errors import ApiBadRequest
from simple_supply_rest_api.errors import ApiInternalError

from simple_supply_rest_api.transaction_creation import \
    make_create_election_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_voting_option_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_poll_registration_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_voter_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_vote_transaction
from simple_supply_rest_api.transaction_creation import \
    make_update_vote_transaction
from simple_supply_rest_api.transaction_creation import \
    make_update_election_transaction
from simple_supply_rest_api.transaction_creation import \
    make_update_voter_transaction
from simple_supply_rest_api.transaction_creation import \
    make_update_voting_option_status_transaction
from simple_supply_rest_api.transaction_creation import \
    make_update_poll_book_status_transaction
import logging

LOGGER = logging.getLogger(__name__)
MAX_TRIES = 50

class Messenger(object):
    def __init__(self, validator_url, database):
        self._connection = Connection(validator_url)
        self._context = create_context('secp256k1')
        self._crypto_factory = CryptoFactory(self._context)
        self._batch_signer = self._crypto_factory.new_signer(
            self._context.new_random_private_key())
        self._database = database

    def open_validator_connection(self):
        self._connection.open()

    def close_validator_connection(self):
        self._connection.close()

    def get_new_key_pair(self):
        private_key = self._context.new_random_private_key()
        public_key = self._context.get_public_key(private_key)
        return public_key.as_hex(), private_key.as_hex()

    async def send_create_election_transaction(self,
                                               private_key,
                                               election_id,
                                               name,
                                               description,
                                               start_timestamp,
                                               end_timestamp,
                                               results_permission,
                                               can_change_vote,
                                               can_show_realtime,
                                               admin_id,
                                               status,
                                               timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_election_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            election_id=election_id,
            name=name,
            description=description,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            results_permission=results_permission,
            can_change_vote=can_change_vote,
            can_show_realtime=can_show_realtime,
            admin_id=admin_id,
            status=status,
            timestamp=timestamp)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            election = await self._database.fetch_election_resource(election_id=election_id)

            if election is not None:
                break

            LOGGER.info("Invalid transaction. Retrying...")
            count_tries = count_tries + 1

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_create_voting_option_transaction(self,
                                                    private_key,
                                                    voting_option_id,
                                                    name,
                                                    description,
                                                    election_id,
                                                    status,
                                                    timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_voting_option_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voting_option_id=voting_option_id,
            name=name,
            description=description,
            election_id=election_id,
            status=status,
            timestamp=timestamp
        )

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            voting_option = await self._database.fetch_voting_option_resource(voting_option_id=voting_option_id)

            if voting_option is not None:
                break

            LOGGER.info("Invalid transaction. Retrying...")
            count_tries = count_tries + 1

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_create_poll_registration_transaction(self,
                                                        private_key,
                                                        voter_id,
                                                        name,
                                                        election_id,
                                                        status,
                                                        timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_poll_registration_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voter_id=voter_id,
            name=name,
            election_id=election_id,
            status=status,
            timestamp=timestamp
        )

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            poll_book_registration = await self._database.fetch_poll_book_registration(election_id=election_id, voter_id=voter_id)

            if poll_book_registration is not None:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_create_voter_transaction(self,
                                            private_key,
                                            voter_id,
                                            public_key,
                                            name,
                                            created_at,
                                            type):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_voter_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voter_id=voter_id,
            public_key=public_key,
            name=name,
            created_at=created_at,
            type=type)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            voter = await self._database.fetch_voter_resource(voter_id=voter_id)
            if voter is not None:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_update_voter_transaction(self,
                                            private_key,
                                            voter_id,
                                            public_key,
                                            name,
                                            created_at,
                                            type):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_update_voter_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voter_id=voter_id,
            public_key=public_key,
            name=name,
            created_at=created_at,
            type=type)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            voter = await self._database.fetch_voter_resource(voter_id=voter_id)
            if voter is not None and voter.get("created_at") == created_at:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_create_vote_transaction(self,
                                           private_key,
                                           vote_id,
                                           timestamp,
                                           voter_id,
                                           election_id,
                                           voting_option_id):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_vote_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            vote_id=vote_id,
            timestamp=timestamp,
            voter_id=voter_id,
            election_id=election_id,
            voting_option_id=voting_option_id)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            vote = await self._database.fetch_vote_resource(vote_id=vote_id)
            if vote is not None:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_update_vote_transaction(self,
                                           private_key,
                                           vote_id,
                                           timestamp,
                                           voting_option_id):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_update_vote_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            vote_id=vote_id,
            timestamp=timestamp,
            voting_option_id=voting_option_id)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            vote = await self._database.fetch_vote_resource(vote_id=vote_id)
            if vote is not None and vote.get('timestamp') == timestamp:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_update_election_transaction(self,
                                               private_key,
                                               election_id,
                                               name,
                                               description,
                                               start_timestamp,
                                               end_timestamp,
                                               results_permission,
                                               can_change_vote,
                                               can_show_realtime,
                                               admin_id,
                                               status,
                                               timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_update_election_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            election_id=election_id,
            name=name,
            description=description,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            results_permission=results_permission,
            can_change_vote=can_change_vote,
            can_show_realtime=can_show_realtime,
            admin_id=admin_id,
            status=status,
            timestamp=timestamp)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            election = await self._database.fetch_election_resource(election_id=election_id)
            if election is not None and election.get('timestamp') == timestamp:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_update_voting_option_status_transaction(self,
                                                           private_key,
                                                           voting_option_id,
                                                           name,
                                                           description,
                                                           election_id,
                                                           status,
                                                           timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_update_voting_option_status_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voting_option_id=voting_option_id,
            name=name,
            description=description,
            election_id=election_id,
            status=status,
            timestamp=timestamp)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            voting_option = await self._database.fetch_voting_option_resource(voting_option_id=voting_option_id)
            if voting_option is not None and voting_option.get('timestamp') == timestamp:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def send_update_voter_poll_book_status_transaction(self,
                                                             private_key,
                                                             voter_id,
                                                             name,
                                                             election_id,
                                                             status,
                                                             timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_update_poll_book_status_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voter_id=voter_id,
            name=name,
            election_id=election_id,
            status=status,
            timestamp=timestamp)

        count_tries = 0

        while await self._send_and_wait_for_commit(batch) is False and count_tries < MAX_TRIES:
            poll_book_registration = await self._database.fetch_poll_book_registration(election_id=election_id,
                                                                                       voter_id=voter_id)

            if poll_book_registration is not None and poll_book_registration.get('timestamp') == timestamp:
                break

            LOGGER.debug("Invalid transaction. Retrying...")

        if count_tries == MAX_TRIES:
            raise ApiInternalError("Invalid transaction. MAX_TRIES limit reached.")

    async def _send_and_wait_for_commit(self, batch):
        # Send transaction to validator
        submit_request = client_batch_submit_pb2.ClientBatchSubmitRequest(
            batches=[batch])
        res = await self._connection.send(
            validator_pb2.Message.CLIENT_BATCH_SUBMIT_REQUEST,
            submit_request.SerializeToString(),
            500
        )

        submit_response = client_batch_submit_pb2.ClientBatchSubmitResponse()
        submit_response.ParseFromString(res.content)

        # Send status request to validator
        batch_id = batch.header_signature
        status_request = client_batch_submit_pb2.ClientBatchStatusRequest(
            batch_ids=[batch_id], wait=True, timeout=500)
        validator_response = await self._connection.send(
            validator_pb2.Message.CLIENT_BATCH_STATUS_REQUEST,
            status_request.SerializeToString(),
            500
        )

        # Parse response
        status_response = client_batch_submit_pb2.ClientBatchStatusResponse()
        status_response.ParseFromString(validator_response.content)
        status = status_response.batch_statuses[0].status
        if status == client_batch_submit_pb2.ClientBatchStatus.INVALID \
                or status == client_batch_submit_pb2.ClientBatchStatus.PENDING \
                or status == client_batch_submit_pb2.ClientBatchStatus.UNKNOWN:
            return False

        return True
