import datetime
from json.decoder import JSONDecodeError
import logging
import time

from aiohttp.web import json_response
import bcrypt
from Crypto.Cipher import AES
from itsdangerous import BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from simple_supply_rest_api.errors import ApiForbidden
from simple_supply_rest_api.errors import ApiConflict
from simple_supply_rest_api.errors import ApiBadRequest
from simple_supply_rest_api.errors import ApiNotFound
from simple_supply_rest_api.errors import ApiUnauthorized
from simple_supply_rest_api.errors import ApiInternalError

import uuid

from diskcache import Cache

LOGGER = logging.getLogger(__name__)


class RouteHandler(object):
    def __init__(self, loop, messenger, database):
        self._loop = loop
        self._messenger = messenger
        self._database = database
        self.cache = Cache()

    async def create_election(self, request):
        private_key, public_key, user = await self._authorize(request)
        body = await decode_request(request)
        required_fields = ['name', 'description', 'start_timestamp', 'end_timestamp',
                           'results_permission', 'can_change_vote', 'can_show_realtime',
                           'voting_options', 'poll_book']
        validate_fields(required_fields, body)

        if user.get('type') != 'ADMIN' and user.get('type') != 'SUPERADMIN':
            raise ApiForbidden('Voter must be an admin or superadmin')

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

            await self._messenger.send_create_voting_option_transaction(
                private_key=private_key,
                voting_option_id=voting_option_id,
                name=voting_option.get('name'),
                description=voting_option.get('description'),
                election_id=election_id,
                status=1,
                timestamp=get_time()
            )

            await self._database.insert_voting_option_num_vote_resource(voting_option_id=voting_option_id,
                                                                        name=voting_option.get('name'),
                                                                        election_id=election_id)

        for poll_book in body.get('poll_book'):
            await self._messenger.send_create_poll_registration_transaction(
                private_key=private_key,
                voter_id=poll_book.get('id'),
                name=poll_book.get('name'),
                election_id=election_id,
                status=1,
                timestamp=get_time()
            )

        return json_response({'data': 'Create election transaction submitted'})

    async def create_voter(self, request):
        body = await decode_request(request)
        required_fields = ['voter_id', 'name', 'password']
        validate_fields(required_fields, body)

        if await self._database.is_voter_created(body.get("voter_id")) is not None:
            raise ApiConflict("Voter ID must be unique")

        public_key, private_key = self._messenger.get_new_key_pair()

        await self._messenger.send_create_voter_transaction(
            private_key=private_key,
            voter_id=body.get('voter_id'),
            public_key=public_key,
            name=body.get('name'),
            created_at=get_time(),
            type='VOTER')

        encrypted_private_key = encrypt_private_key(request.app['aes_key'], public_key, private_key)
        hashed_password = hash_password(body.get('password'))

        await self._database.create_auth_entry(public_key, encrypted_private_key, hashed_password)

        user = {'name': body.get('name'), 'voter_id': body.get('voter_id'), 'type': 'VOTER'}

        token = self.generate_auth_token(request.app['secret_key'], public_key, user)

        return json_response(
            {'accessToken': token, 'user': user})

    async def update_voter_type(self, request):
        private_key, public_key, user = await self._authorize(request)
        body = await decode_request(request)
        required_fields = ['type']
        validate_fields(required_fields, body)

        voter_id = request.match_info.get('voterId', '')
        if voter_id == '':
            raise ApiBadRequest(
                'The voter ID is a required query string parameter'
            )

        if user.get('type') != 'SUPERADMIN':
            raise ApiForbidden(
                'Forbidden'
            )

        voter = await self._database.fetch_voter_resource(voter_id=voter_id)

        if voter is None:
            raise ApiNotFound(
                'No voter found'
            )

        if voter.get('type') == 'ADMIN' or voter.get('type') == 'SUPERADMIN':
            raise ApiConflict(
                'Voter {} is already an admin or superadmin'.format(voter_id)
            )

        auth_info = await self._database.fetch_auth_resource(public_key=voter.get('public_key'))
        voter_private_key = decrypt_private_key(request.app['aes_key'], voter.get('public_key'),
                                                auth_info.get('encrypted_private_key'))

        await self._messenger.send_update_voter_transaction(
            private_key=voter_private_key,
            voter_id=voter_id,
            public_key=voter.get('public_key'),
            name=voter.get('name'),
            created_at=get_time(),
            type=body.get('type'))

        return json_response({'voter': {'voter_id': voter_id, 'name': voter.get('name'), 'type': 'ADMIN'}})

    async def create_vote(self, request):
        body = await decode_request(request)
        required_fields = []
        validate_fields(required_fields, body)

        private_key, public_key, user = await self._authorize(request)
        voting_option_id = request.match_info.get('votingOptionId', '')

        if voting_option_id == '':
            raise ApiBadRequest(
                'The voting option ID is a required query string parameter'
            )

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

        election_id = voting_option.get('election_id')
        election = await self._database.fetch_election_resource(election_id=election_id)

        if election.get('status') == 0:
            raise ApiBadRequest(
                'Election with the election id '
                '{} is cancelled'.format(election_id))

        current_time = get_time()

        if election.get('end_timestamp') < current_time or election.get('start_timestamp') > current_time:
            raise ApiBadRequest(
                'Not in election time.'.format())

        poll_registration = await self._database.fetch_poll_book_registration(voter_id=user.get('voter_id'),
                                                                              election_id=election_id)

        if poll_registration is None:
            raise ApiBadRequest(
                'Voter is not registered in the poll book of the election with the id '
                '{} .'.format(election_id))

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
        private_key, public_key, user = await self._authorize(request)
        body = await decode_request(request)
        required_fields = ['voting_option_id']
        validate_fields(required_fields, body)

        vote_id = request.match_info.get('voteId', '')

        if vote_id == '':
            raise ApiBadRequest(
                'The vote ID is a required query string parameter'
            )

        vote = await self._database.fetch_vote_resource(vote_id=vote_id)
        election_id = vote.get('election_id')

        if vote is None:
            raise ApiNotFound(
                'Vote with the vote id '
                '{} was not found'.format(vote_id))

        if vote.get('voting_option_id') == body.get('voting_option_id'):
            raise ApiBadRequest(
                'Vote must be different.'
            )

        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        if election.get('can_change_vote') == 0:
            raise ApiInternalError(
                'Election with the election id '
                '{} was not found don\'t permit to change vote'.format(election_id))

        if election.get('can_change_vote') == 0:
            raise ApiInternalError(
                'Election with the election id '
                '{} was not found don\'t permit to change vote'.format(election_id))

        current_time = get_time()

        if election.get('end_timestamp') < current_time or election.get('start_timestamp') > current_time:
            raise ApiBadRequest(
                'Not in election time.'.format())

        if election.get('admin_id') == user.get('voter_id'):
            raise ApiBadRequest(
                'User is not the owner of the election with the id '
                '{} .'.format(election_id))

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
        private_key, public_key, user = await self._authorize(request)
        body = await decode_request(request)
        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        current_time = get_time()

        if election.get('start_timestamp') < current_time:
            raise ApiBadRequest(
                'Election with the election id '
                '{} already start.'.format(election_id))

        if election.get('admin_id') != user.get('voter_id'):
            raise ApiBadRequest(
                'User is not the owner of the election with the id '
                '{} .'.format(election_id))

        await self._messenger.send_update_election_transaction(
            private_key=private_key,
            election_id=election_id,
            name=body.get('name') if body.get('name') is not None else election.get('name'),
            description=body.get('description') if body.get('description') is not None else election.get('description'),
            start_timestamp=body.get('start_timestamp') if body.get('start_timestamp') is not None else election.get(
                'start_timestamp'),
            end_timestamp=body.get('end_timestamp') if body.get('end_timestamp') is not None else election.get(
                'end_timestamp'),
            results_permission=body.get('results_permission') if body.get(
                'results_permission') is not None else election.get('results_permission'),
            can_change_vote=body.get('can_change_vote') if body.get('can_change_vote') is not None else election.get(
                'can_change_vote'),
            can_show_realtime=body.get('can_show_realtime') if body.get(
                'can_show_realtime') is not None else election.get('can_show_realtime'),
            admin_id=user.get('voter_id'),
            status=body.get('status') if body.get('status') is not None else election.get('status'),
            timestamp=get_time())

        if body.get('voting_options') is not None:
            for voting_option in body.get('voting_options'):
                voting_option_id = uuid.uuid1().hex

                await self._messenger.send_create_voting_option_transaction(
                    private_key=private_key,
                    voting_option_id=voting_option_id,
                    name=voting_option.get('name'),
                    description=voting_option.get('description'),
                    election_id=election_id,
                    status=1,
                    timestamp=get_time()
                )

                await self._database.insert_voting_option_num_vote_resource(voting_option_id=voting_option_id,
                                                                            name=voting_option.get('name'),
                                                                            election_id=election_id)
        if body.get('poll_book') is not None:
            for poll_book in body.get('poll_book'):
                await self._messenger.send_create_poll_registration_transaction(
                    private_key=private_key,
                    voter_id=poll_book.get('id'),
                    name=poll_book.get('name'),
                    election_id=election_id,
                    status=1,
                    timestamp=get_time()
                )

        return json_response(
            {'data': 'Update Election transaction submitted'})

    async def get_election(self, request):
        private_key, public_key, user = await self._authorize(request)

        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        election = await self._database.fetch_election_with_can_vote_resource(voter_id=user.get('voter_id'),
                                                                              election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        if election.get('results_permission') != 'PUBLIC':
            if election.get('can_vote') is False and election.get('admin_id') != user.get('voter_id'):
                raise ApiForbidden(
                    'Voter is not registered in the poll book of the election with the id '
                    '{}.'.format(election_id))

        return json_response(election)

    async def get_election_votes(self, request):
        private_key, public_key, user = await self._authorize(request)
        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        number_of_votes = await self._database.fetch_number_of_votes(election_id=election_id)

        if number_of_votes is None:
            raise ApiNotFound(
                'No voting options with the election id '
                '{} was not found'.format(election_id))

        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        if election.get('results_permission') != 'PUBLIC':

            poll_registration = await self._database.fetch_poll_book_registration(voter_id=user.get('voter_id'),
                                                                                  election_id=election_id)

            if poll_registration is None and election.get('admin_id') != user.get('voter_id'):
                raise ApiBadRequest(
                    'Voter is not registered in the poll book of the election with the id '
                    '{} .'.format(election_id))

        return json_response(number_of_votes)

    async def get_poll_registrations(self, request):
        private_key, public_key, user = await self._authorize(request)
        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        poll_book = await self._database.fetch_poll_book(election_id=election_id)

        if poll_book is None:
            raise ApiNotFound(
                'No voters with the election id '
                '{} was not found'.format(election_id))

        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        if election.get('admin_id') != user.get('voter_id'):
            raise ApiBadRequest(
                'User is not the owner of the election with the id '
                '{} .'.format(election_id))

        return json_response(poll_book)

    async def count_poll_registrations(self, request):
        private_key, public_key, user = await self._authorize(request)
        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        count_poll_book = await self._database.count_poll_book(election_id=election_id)

        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        if election.get('results_permission') != 'PUBLIC':

            poll_registration = await self._database.fetch_poll_book_registration(voter_id=user.get('voter_id'),
                                                                                  election_id=election_id)

            if poll_registration is None and election.get('admin_id') != user.get('voter_id'):
                raise ApiBadRequest(
                    'Voter is not registered in the poll book of the election with the id '
                    '{} .'.format(election_id))

        return json_response(count_poll_book)

    async def list_voting_options_election(self, request):
        private_key, public_key, user = await self._authorize(request)
        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        voting_options = await self._database.fetch_election_voting_options_resource(election_id=election_id)

        if voting_options is None:
            raise ApiNotFound(
                'Voting Options in the election id '
                '{} was not found'.format(election_id))

        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        if election.get('results_permission') != 'PUBLIC':

            poll_registration = await self._database.fetch_poll_book_registration(voter_id=user.get('voter_id'),
                                                                                  election_id=election_id)

            if poll_registration is None and election.get('admin_id') != user.get('voter_id'):
                raise ApiForbidden(
                    'Voter is not registered in the poll book of the election with the id '
                    '{} .'.format(election_id))

        return json_response(voting_options)

    async def get_voting_option(self, request):
        private_key, public_key, user = await self._authorize(request)
        voting_option_id = request.match_info.get('votingOptionId', '')

        if voting_option_id == '':
            raise ApiBadRequest(
                'The voting option ID is a required query string parameter'
            )

        voting_option = await self._database.fetch_voting_option_resource(voting_option_id=voting_option_id)

        if voting_option is None:
            raise ApiNotFound(
                'No voting options with the id '
                '{} was not found'.format(voting_option_id))

        return json_response(voting_option)

    async def update_voting_option_status(self, request):
        private_key, public_key, user = await self._authorize(request)
        voting_option_id = request.match_info.get('votingOptionId', '')

        if voting_option_id == '':
            raise ApiBadRequest(
                'The voting option ID is a required query string parameter'
            )

        voting_option = await self._database.fetch_voting_option_resource(voting_option_id=voting_option_id)

        if voting_option is None:
            raise ApiNotFound(
                'Voting Option with the voting option id '
                '{} was not found'.format(voting_option_id))

        election_id = voting_option.get('election_id')
        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        current_time = get_time()

        if election.get('start_timestamp') < current_time:
            raise ApiBadRequest(
                'Election with the election id '
                '{} already start.'.format(election_id))

        if election.get('admin_id') != user.get('voter_id'):
            raise ApiBadRequest(
                'User is not the owner of the election with the id '
                '{} .'.format(election_id))

        if voting_option.get('status') is True:
            status = 0
        else:
            status = 1

        await self._messenger.send_update_voting_option_status_transaction(
            private_key=private_key,
            voting_option_id=voting_option_id,
            name=voting_option.get('name'),
            description=voting_option.get('description'),
            election_id=voting_option.get('election_id'),
            status=status,
            timestamp=get_time())

        return json_response(
            {'data': 'Update Voting Option Status transaction submitted'})

    async def update_poll_book_status(self, request):
        private_key, public_key, user = await self._authorize(request)
        voter_id = request.match_info.get('voterId', '')

        if voter_id == '':
            raise ApiBadRequest(
                'The voter ID is a required query string parameter'
            )

        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        voter_poll_book = await self._database.fetch_poll_book_registration(election_id=election_id,
                                                                            voter_id=voter_id)

        if voter_poll_book is None:
            raise ApiNotFound(
                'Voter with the voter id '
                '{} was not found'.format(voter_id))

        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        current_time = get_time()

        if election.get('start_timestamp') < current_time:
            raise ApiBadRequest(
                'Election with the election id '
                '{} already start.'.format(election_id))

        if election.get('admin_id') != user.get('voter_id'):
            raise ApiBadRequest(
                'User is not the owner of the election with the id '
                '{} .'.format(election_id))

        if voter_poll_book.get('status') is True:
            status = 0
        else:
            status = 1

        await self._messenger.send_update_voter_poll_book_status_transaction(
            private_key=private_key,
            voter_id=voter_id,
            name=voter_poll_book.get('name'),
            election_id=election_id,
            status=status,
            timestamp=get_time())

        return json_response(
            {'data': 'Update Poll Registration Status transaction submitted'})

    async def list_elections_current(self, request):
        private_key, public_key, user = await self._authorize(request)
        voterId = request.match_info.get('voterId', '')

        if voterId == '':
            raise ApiBadRequest(
                'The voter ID is a required query string parameter'
            )

        if user.get('voter_id') != voterId:
            raise ApiForbidden('Admin must be the authenticated one')

        current_elections_list = await self._database.fetch_current_elections_resources(voterId,
                                                                                        get_time())
        return json_response(current_elections_list)

    async def list_elections_past(self, request):
        private_key, public_key, user = await self._authorize(request)
        voterId = request.match_info.get('voterId', '')

        if voterId == '':
            raise ApiBadRequest(
                'The voter ID is a required query string parameter'
            )

        if user.get('voter_id') != voterId:
            raise ApiForbidden('Admin must be the authenticated one')

        past_elections_list = await self._database.fetch_past_elections_resources(voterId, get_time())

        return json_response(past_elections_list)

    async def list_admin_elections(self, request):
        private_key, public_key, user = await self._authorize(request)

        voter_id = request.match_info.get('voterId', '')

        if voter_id == '':
            raise ApiBadRequest(
                'The voter ID is a required query string parameter'
            )

        if user.get('voter_id') != voter_id:
            raise ApiForbidden('Admin must be the authenticated one')

        if user.get('type') != 'ADMIN' and user.get('type') != 'SUPERADMIN':
            raise ApiForbidden('Voter must be an admin or superadmin')

        admin_elections_list = await self._database.fetch_admin_elections_resources(user.get('voter_id'))
        return json_response(admin_elections_list)

    async def list_public_elections(self, request):
        private_key, public_key, user = await self._authorize(request)

        public_elections_list = await self._database.fetch_public_elections_resources(get_time())
        return json_response(public_elections_list)

    async def list_public_past_elections(self, request):
        private_key, public_key, user = await self._authorize(request)

        past_elections_list = await self._database.fetch_public_past_elections_resources(user.get('voter_id'),
                                                                                         get_time())

        return json_response(past_elections_list)

    async def list_admins(self, request):
        private_key, public_key, user = await self._authorize(request)

        if user.get('type') != 'SUPERADMIN':
            raise ApiForbidden(
                'Forbidden'
            )

        admin_list = await self._database.fetch_admins_resources()

        return json_response(admin_list)

    async def get_voters(self, request):
        private_key, public_key, user = await self._authorize(request)

        if user.get('type') != 'SUPERADMIN':
            raise ApiForbidden(
                'Forbidden'
            )

        voter_id = request.match_info.get('voterId', '')
        voters_list = await self._database.fetch_voters_resources(voter_id=voter_id)

        return json_response(voters_list)

    async def get_vote(self, request):
        private_key, public_key, user = await self._authorize(request)
        vote_id = request.match_info.get('voteId', '')

        if vote_id == '':
            raise ApiBadRequest(
                'The vote ID is a required query string parameter'
            )

        vote = await self._database.fetch_vote_resource(vote_id=vote_id)

        if vote is None:
            raise ApiNotFound(
                'Vote with the vote id '
                '{} was not found'.format(vote_id))

        election_id = vote.get('election_id')
        election = await self._database.fetch_election_resource(election_id=election_id)

        if election is None:
            raise ApiNotFound(
                'Election with the election id '
                '{} was not found'.format(election_id))

        return json_response(vote)

    async def get_vote_election(self, request):
        private_key, public_key, user = await self._authorize(request)
        voter_id = request.match_info.get('voterId', '')

        if voter_id == '':
            raise ApiBadRequest(
                'The voter ID is a required query string parameter'
            )

        election_id = request.match_info.get('electionId', '')

        if election_id == '':
            raise ApiBadRequest(
                'The election ID is a required query string parameter'
            )

        if user.get('voter_id') != voter_id:
            raise ApiForbidden('Admin must be the authenticated one')

        vote = await self._database.fetch_my_vote__election_resource(voter_id=voter_id,
                                                                     election_id=election_id)

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

        user = {'name': voter.get('name'), 'voter_id': body.get('voter_id'), 'type': voter.get('type')}

        token = self.generate_auth_token(
            request.app['secret_key'], voter.get('public_key'), user)

        return json_response(
            {'accessToken': token, 'user': user})

    async def _authorize(self, request):
        token = request.headers.get('AUTHORIZATION')
        if token is None:
            raise ApiUnauthorized('No auth token provided')
        token_prefixes = ('Bearer', 'Token')
        for prefix in token_prefixes:
            if prefix in token:
                token = token.partition(prefix)[2].strip()
        try:
            token_dict = self.deserialize_auth_token(request.app['secret_key'], token)
        except BadSignature:
            raise ApiUnauthorized('Invalid auth token')
        public_key = token_dict.get('public_key')

        auth_resource = await self._database.fetch_auth_resource(public_key=public_key)
        if auth_resource is None:
            raise ApiUnauthorized('Token is not associated with an agent')

        user = self.cache.get(token)
        return decrypt_private_key(request.app['aes_key'],
                                   public_key,
                                   auth_resource['encrypted_private_key']), public_key, user

    async def logout(self, request):
        await self._authorize(request)
        token = request.headers.get('AUTHORIZATION')
        token_prefixes = ('Bearer', 'Token')
        for prefix in token_prefixes:
            if prefix in token:
                token = token.partition(prefix)[2].strip()

        self.cache.delete(token)
        return json_response("Successful logout")

    def generate_auth_token(self, secret_key, public_key, user):
        serializer = Serializer(secret_key, expires_in=3600)
        token = serializer.dumps({'public_key': public_key})
        decoded_token = token.decode('ascii')
        self.cache.set(decoded_token, user, expire=3600)
        self.cache.close()
        return decoded_token

    def deserialize_auth_token(self, secret_key, token):
        token_status = self.cache.get(token)
        if token_status is None:
            raise BadSignature("")

        serializer = Serializer(secret_key)
        return serializer.loads(token)


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
