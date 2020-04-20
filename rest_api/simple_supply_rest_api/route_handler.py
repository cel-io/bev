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

import uuid

LOGGER = logging.getLogger(__name__)


class RouteHandler(object):
    def __init__(self, loop, messenger, database):
        self._loop = loop
        self._messenger = messenger
        self._database = database

    async def create_election(self, request):
        body = await decode_request(request)
        required_fields = ['name', 'description', 'start_timestamp', 'end_timestamp',
                           'results_permission', 'can_change_vote', 'can_show_realtime',
                           'voting_options', 'poll_book']
        validate_fields(required_fields, body)

        private_key = await self._authorize(request)
        election_id = uuid.uuid1().hex

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
            admin_id="1",
            timestamp=get_time()
        )

        for voting_option in body.get('voting_options'):
            await self._messenger.send_create_voting_option_transaction(
                private_key=private_key,
                voting_option_id=uuid.uuid1().hex,
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

    async def list_elections(self, _request):
        election_list = await self._database.fetch_all_election_resources()
        return json_response(election_list)

    # ------------------------------------------------------------
    # ------------------------------------------------------------
    # ------------------------------------------------------------

    async def authenticate(self, request):
        body = await decode_request(request)
        required_fields = ['public_key', 'password']
        validate_fields(required_fields, body)

        password = bytes(body.get('password'), 'utf-8')

        auth_info = await self._database.fetch_auth_resource(
            body.get('public_key'))
        if auth_info is None:
            raise ApiUnauthorized('No agent with that public key exists')

        hashed_password = auth_info.get('hashed_password')
        if not bcrypt.checkpw(password, bytes.fromhex(hashed_password)):
            raise ApiUnauthorized('Incorrect public key or password')

        token = generate_auth_token(
            request.app['secret_key'], body.get('public_key'))

        return json_response({'authorization': token})

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
        private_key = await self._authorize(request)

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
        private_key = await self._authorize(request)

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
        private_key = await self._authorize(request)

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

        auth_resource = await self._database.fetch_auth_resource(public_key)
        if auth_resource is None:
            raise ApiUnauthorized('Token is not associated with an agent')
        return decrypt_private_key(request.app['aes_key'],
                                   public_key,
                                   auth_resource['encrypted_private_key'])


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
    serializer = Serializer(secret_key)
    token = serializer.dumps({'public_key': public_key})
    return token.decode('ascii')


def deserialize_auth_token(secret_key, token):
    serializer = Serializer(secret_key)
    return serializer.loads(token)
