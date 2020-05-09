from sawtooth_rest_api.messaging import Connection
from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import validator_pb2
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context
from sawtooth_signing import secp256k1
from simple_supply_rest_api.errors import ApiBadRequest
from simple_supply_rest_api.errors import ApiInternalError
from simple_supply_rest_api.transaction_creation import \
    make_create_agent_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_election_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_voting_option_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_record_transaction
from simple_supply_rest_api.transaction_creation import \
    make_transfer_record_transaction
from simple_supply_rest_api.transaction_creation import \
    make_update_record_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_poll_registration_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_voter_transaction
from simple_supply_rest_api.transaction_creation import \
    make_create_vote_transaction
from simple_supply_rest_api.transaction_creation import \
    make_update_vote_transaction


class Messenger(object):
    def __init__(self, validator_url):
        self._connection = Connection(validator_url)
        self._context = create_context('secp256k1')
        self._crypto_factory = CryptoFactory(self._context)
        self._batch_signer = self._crypto_factory.new_signer(
            self._context.new_random_private_key())

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
            timestamp=timestamp)
        await self._send_and_wait_for_commit(batch)

    async def send_create_voting_option_transaction(self,
                                                    private_key,
                                                    voting_option_id,
                                                    name,
                                                    description,
                                                    election_id,
                                                    timestamp,
                                                    num_votes):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_voting_option_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voting_option_id=voting_option_id,
            name=name,
            description=description,
            election_id=election_id,
            timestamp=timestamp,
            num_votes=num_votes
        )

        await self._send_and_wait_for_commit(batch)

    async def send_create_poll_registration_transaction(self,
                                                        private_key,
                                                        voter_id,
                                                        name,
                                                        election_id,
                                                        timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_poll_registration_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            voter_id=voter_id,
            name=name,
            election_id=election_id,
            timestamp=timestamp
        )

        await self._send_and_wait_for_commit(batch)

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
        await self._send_and_wait_for_commit(batch)

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
        await self._send_and_wait_for_commit(batch)

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
        await self._send_and_wait_for_commit(batch)

    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # ------------------------------------------------------------

    async def send_create_agent_transaction(self,
                                            private_key,
                                            name,
                                            timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_agent_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            name=name,
            timestamp=timestamp)
        await self._send_and_wait_for_commit(batch)

    async def send_create_record_transaction(self,
                                             private_key,
                                             latitude,
                                             longitude,
                                             record_id,
                                             timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_create_record_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            latitude=latitude,
            longitude=longitude,
            record_id=record_id,
            timestamp=timestamp)
        await self._send_and_wait_for_commit(batch)

    async def send_transfer_record_transaction(self,
                                               private_key,
                                               receiving_agent,
                                               record_id,
                                               timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))

        batch = make_transfer_record_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            receiving_agent=receiving_agent,
            record_id=record_id,
            timestamp=timestamp)
        await self._send_and_wait_for_commit(batch)

    async def send_update_record_transaction(self,
                                             private_key,
                                             latitude,
                                             longitude,
                                             record_id,
                                             timestamp):
        transaction_signer = self._crypto_factory.new_signer(
            secp256k1.Secp256k1PrivateKey.from_hex(private_key))
        batch = make_update_record_transaction(
            transaction_signer=transaction_signer,
            batch_signer=self._batch_signer,
            latitude=latitude,
            longitude=longitude,
            record_id=record_id,
            timestamp=timestamp)
        await self._send_and_wait_for_commit(batch)

    async def _send_and_wait_for_commit(self, batch):
        # Send transaction to validator
        submit_request = client_batch_submit_pb2.ClientBatchSubmitRequest(
            batches=[batch])
        await self._connection.send(
            validator_pb2.Message.CLIENT_BATCH_SUBMIT_REQUEST,
            submit_request.SerializeToString())

        # Send status request to validator
        batch_id = batch.header_signature
        status_request = client_batch_submit_pb2.ClientBatchStatusRequest(
            batch_ids=[batch_id], wait=True)
        validator_response = await self._connection.send(
            validator_pb2.Message.CLIENT_BATCH_STATUS_REQUEST,
            status_request.SerializeToString())

        # Parse response
        status_response = client_batch_submit_pb2.ClientBatchStatusResponse()
        status_response.ParseFromString(validator_response.content)
        status = status_response.batch_statuses[0].status
        if status == client_batch_submit_pb2.ClientBatchStatus.INVALID:
            error = status_response.batch_statuses[0].invalid_transactions[0]
            raise ApiBadRequest(error.message)
        elif status == client_batch_submit_pb2.ClientBatchStatus.PENDING:
            raise ApiInternalError('Transaction submitted but timed out')
        elif status == client_batch_submit_pb2.ClientBatchStatus.UNKNOWN:
            raise ApiInternalError('Something went wrong. Try again later')
