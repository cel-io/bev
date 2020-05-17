import datetime
from json.decoder import JSONDecodeError
import logging
import time

from aiohttp.web import json_response
import bcrypt
from Crypto.Cipher import AES
from itsdangerous import BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from simple_supply_rest_api.errors import ApiBadRequest
from simple_supply_rest_api.errors import ApiNotFound
from simple_supply_rest_api.errors import ApiUnauthorized
from simple_supply_rest_api.errors import ApiInternalError

import uuid

LOGGER = logging.getLogger(__name__)


class RouteHandler(object):
    def __init__(self, loop, messenger, database):
        self._loop = loop
        self._messenger = messenger
        self._database = database

    async def create_election(self, request):
        private_key, public_key = await self._authorize(request)
        body = await decode_request(request)
        required_fields = ['name', 'description', 'start_timestamp', 'end_timestamp',
                           'results_permission', 'can_change_vote', 'can_show_realtime',
                           'voting_options', 'poll_book']
        validate_fields(required_fields, body)

        election_id = uuid.uuid1().hex
        voting_options = body.get('voting_options')
        admin = await self._database.fetch_voter_resource(public_key=public_key)

        for voting_option in voting_options:
            if voting_option.get('name').upper() == "NULL" or voting_option.get('name').upper() == "BLANK":
                raise ApiInternalError('NULL and BLANK are default options')

        voting_options.append({"name": "NULL", "description": "VOTE NULL"})
        voting_options.append({"name": "BLANK", "description": "VOTE BLANK"})

        await self._messenger.send_create_election_transaction(
            private_key=private_key,
            election_id=election_id,
            name=body.get('name'),
            description=body.get('description'),
            start_timestamp=body.get('start_timestamp'),
            end_timestamp=body.get('end_timestamp'),
            results_permission=body.get('results_permission'),
            can_change_vote=body.get('can_change_vote'),
            can_show_realtime=body.get('can_show_realtime'),
            admin_id=admin.get('voter_id'),
            status=1,
            timestamp=get_time()
        )

        for voting_option in voting_options:
            voting_option_id = uuid.uuid1().hex

            await self._database.insert_voting_option_num_vote_resource(voting_option_id=voting_option_id,
                                                                        name=voting_option.get('name'))

            await self._messenger.send_create_voting_option_transaction(
                private_key=private_key,
                voting_option_id=voting_option_id,
                name=voting_option.get('name'),
                description=voting_option.get('description'),
                election_id=election_id,
                timestamp=get_time()
            )

        for poll_book in body.get('poll_book'):
            await self._messenger.send_create_poll_registration_transaction(
                private_key=private_key,
                voter_id=poll_book.get('id'),
                name=poll_book.get('name'),
                election_id=election_id,
                timestamp=get_time()
            )

        return json_response({'data': 'Create election transaction submitted'})

    async def create_voter(self, request):
        body = await decode_request(request)
        required_fields = ['voter_id', 'name', 'type', 'password']
        validate_fields(required_fields, body)

        public_key, private_key = self._messenger.get_new_key_pair()

        await self._messenger.send_create_voter_transaction(
            private_key=private_key,
            voter_id=body.get('voter_id'),
            public_key=public_key,
            name=body.get('name'),
            created_at=get_time(),
            type=body.get('type'))

        encrypted_private_key = encrypt_private_key(request.app['aes_key'], public_key, private_key)
        hashed_password = hash_password(body.get('password'))

        await self._database.create_auth_entry(public_key, encrypted_private_key, hashed_password)

        token = generate_auth_token(request.app['secret_key'], public_key)

        return json_response(
            {'accessToken': token, 'user': {'name': body.get('name'), 'voter_id': body.get('voter_id'),
                                            'type': body.get('type')}})

    async def create_vote(self, request):
        body = await decode_request(request)
        required_fields = []
        validate_fields(required_fields, body)

        private_key, public_key = await self._authorize(request)
        voting_option_id = request.match_info.get('votingOptionId', '')

        voter = await self._database.fetch_voter_resource(public_key=public_key)

        if voter is None:
            raise ApiNotFound(
                'Voter with the public_key '
                '{} was not found'.format(public_key))

        voting_option = await self._database.fetch_voting_option_resource(
            voting_option_id=voting_option_id)
        vo_count_vote = await self._database.fetch_voting_option_num_vote_resource(
            voting_option_id=voting_option_id)

        if voting_option is None:
            raise ApiNotFound(
                'Voting Option with the voting option id '
                '{} was not found'.format(voting_option_id))

        election = await self._database.fetch_election_resource(election_id=voting_option.get('election_id'))

        if election.get('status') == 0:
            raise ApiInternalError(
                'Election with the election id '
                '{} is cancelled'.format(election.get('election_id')))

        num_votes_update = vo_count_vote.get('num_votes') + 1

        await self._messenger.send_create_vote_transaction(
            private_key=private_key,
            vote_id=uuid.uuid1().hex,
            timestamp=get_time(),
            voter_id=voter.get('voter_id'),
            election_id=voting_option.get('election_id'),
            voting_option_id=voting_option_id)

        await self._database.update_voting_option_num_vote_resource(voting_option_id=voting_option_id,
                                                                    num_votes=num_votes_update)

        return json_response({'data': 'Create vote transaction submitted'})

    async def update_vote(self, request):
        private_key, public_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['voting_option_id']
        validate_fields(required_fields, body)

        vote_id = request.match_info.get('voteId', '')
        vote = await self._database.fetch_vote_resource(vote_id=vote_id)

        if vote is None:
            raise ApiNotFound(
                'Vote with the vote id '
                '{} was not found'.format(vote_id))

        election = await self._database.fetch_election_resource(election_id=vote.get('election_id'))

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(vote.get('election_id')))

        if election.get('can_change_vote') == 0:
            raise ApiInternalError(
                'Election with the election id '
                '{} was not found don\'t permit to change vote'.format(vote.get('election_id')))

        if election.get('can_change_vote') == 0:
            raise ApiInternalError(
                'Election with the election id '
                '{} was not found don\'t permit to change vote'.format(vote.get('election_id')))

        new_voting_option_id = body.get('voting_option_id')
        old_voting_option_id = vote.get('voting_option_id')

        old_num_vote = await self._database.fetch_voting_option_num_vote_resource(
            voting_option_id=old_voting_option_id)
        new_num_vote = await self._database.fetch_voting_option_num_vote_resource(
            voting_option_id=new_voting_option_id)
        num_votes_remove = old_num_vote.get('num_votes') - 1
        num_votes_update = new_num_vote.get('num_votes') + 1

        await self._messenger.send_update_vote_transaction(
            private_key=private_key,
            vote_id=vote_id,
            timestamp=get_time(),
            voting_option_id=new_voting_option_id)

        # remove -1 to old voting option
        await self._database.update_voting_option_num_vote_resource(voting_option_id=old_voting_option_id,
                                                                    num_votes=num_votes_remove)

        # add +1 to new voting option
        await self._database.update_voting_option_num_vote_resource(voting_option_id=new_voting_option_id,
                                                                    num_votes=num_votes_update)

        return json_response(
            {'data': 'Update Vote transaction submitted'})

    async def update_election(self, request):
        private_key, public_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['voting_option_id']
        validate_fields(required_fields, body)

        electionId = request.match_info.get('electionId', '')

        election = await self._database.fetch_election_resource(election_id=electionId)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(electionId))

        current_time = get_time()

        if election.get(start_timestamp) > current_time:
            raise ApiInternalError(
                'Election with the election id '
                '{} already start.'.format(electionId))

        admin = await self._database.fetch_voter_resource(public_key=public_key)

        if election.get('status') == 1:
            status = 0
        else:
            status = 1

        await self._messenger.send_update_election_transaction(
            private_key=private_key,
            election_id=electionId,
            name=election.get('name'),
            description=election.get('description'),
            start_timestamp=election.get('start_timestamp'),
            end_timestamp=election.get('end_timestamp'),
            results_permission=election.get('results_permission'),
            can_change_vote=election.get('can_change_vote'),
            can_show_realtime=election.get('can_show_realtime'),
            admin_id=admin.get('voter_id'),
            status=status,
            timestamp=get_time())

        return json_response(
            {'data': 'Update Election transaction submitted'})

    async def get_election(self, request):
        private_key, public_key = await self._authorize(request)
        election_id = request.match_info.get('electionId', '')
        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the A election id '
                '{} was not found'.format(election_id))

        return json_response(election)

    async def list_voting_options_election(self, request):
        private_key, public_key = await self._authorize(request)

        election_id = request.match_info.get('electionId', '')
        voting_options = await self._database.fetch_election_voting_options_resource(election_id=election_id)

        if voting_options is None:
            raise ApiNotFound(
                'Voting Options in the election id '
                '{} was not found'.format(election_id))

        return json_response(voting_options)

    async def list_elections_current(self, request):
        private_key, public_key = await self._authorize(request)

        voter = await self._database.fetch_voter_resource(public_key=public_key)

        current_elections_list = await self._database.fetch_current_elections_resources(voter.get('voter_id'),
                                                                                        get_time())
        return json_response(current_elections_list)

    async def list_elections_past(self, request):
        private_key, public_key = await self._authorize(request)

        voter = await self._database.fetch_voter_resource(public_key=public_key)

        past_elections_list = await self._database.fetch_past_elections_resources(voter.get('voter_id'), get_time())

        return json_response(past_elections_list)

    async def list_vote(self, request):
        private_key, public_key = await self._authorize(request)
        vote_id = request.match_info.get('voteId', '')
        vote = await self._database.fetch_vote_resource(vote_id=vote_id)

        if vote is None:
            raise ApiNotFound(
                'Vote with the vote id BLEUUU'
                '{} was not found'.format(vote_id))

        return json_response(vote)

    async def authenticate(self, request):
        body = await decode_request(request)
        required_fields = ['voter_id', 'password']
        validate_fields(required_fields, body)

        password = bytes(body.get('password'), 'utf-8')

        voter = await self._database.fetch_voter_resource(voter_id=body.get('voter_id'))
        if voter is None:
            raise ApiUnauthorized('Incorrect voter_id or password')

        auth_info = await self._database.fetch_auth_resource(
            public_key=voter.get('public_key'))
        if auth_info is None:
            raise ApiUnauthorized('No voter with that public key exists')

        hashed_password = auth_info.get('hashed_password')
        if not bcrypt.checkpw(password, bytes.fromhex(hashed_password)):
            raise ApiUnauthorized('Incorrect public key or password')

        token = generate_auth_token(
            request.app['secret_key'], voter.get('public_key'))

        return json_response(
            {'accessToken': token, 'user': {'name': voter.get('name'), 'voter_id': voter.get('voter_id'),
                                            'type': voter.get('type')}})

    async def _authorize(self, request):
        token = request.headers.get('AUTHORIZATION')
        if token is None:
            raise ApiUnauthorized('No auth token provided')
        token_prefixes = ('Bearer', 'Token')
        for prefix in token_prefixes:
            if prefix in token:
                token = token.partition(prefix)[2].strip()
        try:
            token_dict = deserialize_auth_token(request.app['secret_key'],
                                                token)
        except BadSignature:
            raise ApiUnauthorized('Invalid auth token')
        public_key = token_dict.get('public_key')

        auth_resource = await self._database.fetch_auth_resource(public_key=public_key)
        if auth_resource is None:
            raise ApiUnauthorized('Token is not associated with an agent')
        return decrypt_private_key(request.app['aes_key'],
                                   public_key,
                                   auth_resource['encrypted_private_key']), public_key

    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # ------------------------------------------------------------

    async def create_agent(self, request):
        body = await decode_request(request)
        required_fields = ['name', 'password']
        validate_fields(required_fields, body)

        public_key, private_key = self._messenger.get_new_key_pair()

        await self._messenger.send_create_agent_transaction(
            private_key=private_key,
            name=body.get('name'),
            timestamp=get_time())

        encrypted_private_key = encrypt_private_key(
            request.app['aes_key'], public_key, private_key)
        hashed_password = hash_password(body.get('password'))

        await self._database.create_auth_entry(
            public_key, encrypted_private_key, hashed_password)

        token = generate_auth_token(
            request.app['secret_key'], public_key)

        return json_response({'authorization': token})

    async def list_agents(self, _request):
        agent_list = await self._database.fetch_all_agent_resources()
        return json_response(agent_list)

    async def fetch_agent(self, request):
        public_key = request.match_info.get('agent_id', '')
        agent = await self._database.fetch_agent_resource(public_key)
        if agent is None:
            raise ApiNotFound(
                'Agent with public key {} was not found'.format(public_key))
        return json_response(agent)

    async def create_record(self, request):
        private_key, public_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['latitude', 'longitude', 'record_id']
        validate_fields(required_fields, body)

        await self._messenger.send_create_record_transaction(
            private_key=private_key,
            latitude=body.get('latitude'),
            longitude=body.get('longitude'),
            record_id=body.get('record_id'),
            timestamp=get_time())

        return json_response(
            {'data': 'Create record transaction submitted'})

    async def list_records(self, _request):
        record_list = await self._database.fetch_all_record_resources()
        return json_response(record_list)

    async def fetch_record(self, request):
        record_id = request.match_info.get('record_id', '')
        record = await self._database.fetch_record_resource(record_id)
        if record is None:
            raise ApiNotFound(
                'Record with the record id '
                '{} was not found'.format(record_id))
        return json_response(record)

    async def transfer_record(self, request):
        private_key, public_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['receiving_agent']
        validate_fields(required_fields, body)

        record_id = request.match_info.get('record_id', '')

        await self._messenger.send_transfer_record_transaction(
            private_key=private_key,
            receiving_agent=body['receiving_agent'],
            record_id=record_id,
            timestamp=get_time())

        return json_response(
            {'data': 'Transfer record transaction submitted'})

    async def update_record(self, request):
        private_key, public_key = await self._authorize(request)

        body = await decode_request(request)
        required_fields = ['latitude', 'longitude']
        validate_fields(required_fields, body)

        record_id = request.match_info.get('record_id', '')

        await self._messenger.send_update_record_transaction(
            private_key=private_key,
            latitude=body['latitude'],
            longitude=body['longitude'],
            record_id=record_id,
            timestamp=get_time())

        return json_response(
            {'data': 'Update record transaction submitted'})

    async def _authorize(self, request):
        token = request.headers.get('AUTHORIZATION')
        if token is None:
            raise ApiUnauthorized('No auth token provided')
        token_prefixes = ('Bearer', 'Token')
        for prefix in token_prefixes:
            if prefix in token:
                token = token.partition(prefix)[2].strip()
        try:
            token_dict = deserialize_auth_token(request.app['secret_key'],
                                                token)
        except BadSignature:
            raise ApiUnauthorized('Invalid auth token')
        public_key = token_dict.get('public_key')

        LOGGER.info(public_key)

        auth_resource = await self._database.fetch_auth_resource(public_key=public_key)
        if auth_resource is None:
            raise ApiUnauthorized('Token is not associated with an agent')
        return decrypt_private_key(request.app['aes_key'],
                                   public_key,
                                   auth_resource['encrypted_private_key']), public_key


async def decode_request(request):
    try:
        return await request.json()
    except JSONDecodeError:
        raise ApiBadRequest('Improper JSON format')


def validate_fields(required_fields, body):
    for field in required_fields:
        if body.get(field) is None:
            raise ApiBadRequest(
                "'{}' parameter is required".format(field))


def encrypt_private_key(aes_key, public_key, private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    return cipher.encrypt(private_key)


def decrypt_private_key(aes_key, public_key, encrypted_private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    private_key = cipher.decrypt(bytes.fromhex(encrypted_private_key))
    return private_key


def hash_password(password):
    return bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())


def get_time():
    dts = datetime.datetime.utcnow()
    return round(time.mktime(dts.timetuple()) + dts.microsecond / 1e6)


def generate_auth_token(secret_key, public_key):
    serializer = Serializer(secret_key, expires_in=3600)
    token = serializer.dumps({'public_key': public_key})
    return token.decode('ascii')


def deserialize_auth_token(secret_key, token):
    serializer = Serializer(secret_key)
    return serializer.loads(token)
