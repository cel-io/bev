
import argparse
import asyncio
import logging
import sys
import datetime
import time
import os

import bcrypt
from Crypto.Cipher import AES

from zmq.asyncio import ZMQEventLoop

from sawtooth_sdk.processor.log import init_console_logging

from aiohttp import web

from simple_supply_rest_api.route_handler import RouteHandler
from simple_supply_rest_api.database import Database
from simple_supply_rest_api.messaging import Messenger

from os.path import join, dirname
from dotenv import load_dotenv

LOGGER = logging.getLogger(__name__)


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Starts the Simple Supply REST API')

    parser.add_argument(
        '-B', '--bind',
        help='identify host and port for api to run on',
        default='localhost:8000')
    parser.add_argument(
        '-C', '--connect',
        help='specify URL to connect to a running validator',
        default='tcp://localhost:4004')
    parser.add_argument(
        '-t', '--timeout',
        help='set time (in seconds) to wait for a validator response',
        default=500)
    parser.add_argument(
        '--db-name',
        help='The name of the database',
        default='bev')
    parser.add_argument(
        '--db-host',
        help='The host of the database',
        default='localhost')
    parser.add_argument(
        '--db-port',
        help='The port of the database',
        default='5432')
    parser.add_argument(
        '--db-user',
        help='The authorized user of the database',
        default='sawtooth')
    parser.add_argument(
        '--db-password',
        help="The authorized user's password for database access",
        default='sawtooth')
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        default=0,
        help='enable more verbose output to stderr')

    return parser.parse_args(args)


def start_rest_api(host, port, messenger, database):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(database.connect())

    app = web.Application(loop=loop)
    app['aes_key'] = os.environ.get("AES_KEY")
    app['secret_key'] = os.environ.get("SECRET_KEY")

    messenger.open_validator_connection()

    handler = RouteHandler(loop, messenger, database)

    app.router.add_post('/elections', handler.create_election)
    app.router.add_get('/elections/current', handler.list_elections_current) # CORRECT TO REST
    app.router.add_get('/elections/past', handler.list_elections_past) # CORRECT TO REST
    app.router.add_get('/elections/public', handler.list_public_elections)
    app.router.add_get('/elections/public/past', handler.list_public_past_elections)
    app.router.add_get('/elections/{electionId}', handler.get_election)
    app.router.add_get('/elections/{electionId}/number_of_votes', handler.get_election_votes)
    app.router.add_get('/elections/{electionId}/poll_book', handler.get_poll_registrations)
    app.router.add_get('/elections/{electionId}/poll_book/count', handler.count_poll_registrations)
    app.router.add_get('/elections/{electionId}/voting_options', handler.list_voting_options_election)
    app.router.add_post('/elections', handler.create_election)
    app.router.add_put('/elections/{electionId}', handler.update_election)

    app.router.add_get('/voting_options/{votingOptionId}', handler.get_voting_option)
    app.router.add_patch('/voting_options/{votingOptionId}/status', handler.update_voting_option_status)
    app.router.add_patch('/elections/{electionId}/poll_registration/{voterId}/status', handler.update_poll_book_status)
    app.router.add_get('/poll_book/{voterId}/{electionId}', handler.is_poll_book_registration)

    app.router.add_post('/voters', handler.create_voter)
    app.router.add_patch('/voters/{voterId}/type', handler.update_voter_type)
    app.router.add_get('/voters/admins', handler.list_admins)
    app.router.add_get('/voters/{voterId}', handler.get_voter)
    app.router.add_get('/voters/admins/{voterId}/elections', handler.list_admin_elections)

    app.router.add_get('/votes/{voteId}', handler.list_vote)
    app.router.add_get('/votes/{voterId}/election/{electionId}', handler.get_vote_election)
    app.router.add_post('/votes/{votingOptionId}', handler.create_vote)
    app.router.add_put('/votes/{voteId}', handler.update_vote)

    app.router.add_post('/authentication', handler.authenticate)
    app.router.add_post('/logout', handler.logout)

    # app.router.add_post('/agents', handler.create_agent)
    # app.router.add_get('/agents', handler.list_agents)
    # app.router.add_get('/agents/{agent_id}', handler.fetch_agent)
    #
    # app.router.add_post('/records', handler.create_record)
    # app.router.add_get('/records', handler.list_records)
    # app.router.add_get('/records/{record_id}', handler.fetch_record)
    # app.router.add_post(
    #     '/records/{record_id}/transfer', handler.transfer_record)
    # app.router.add_post('/records/{record_id}/update', handler.update_record)

    LOGGER.info('Starting BEV REST API on %s:%s', host, port)
    loop.run_until_complete(create_superadmins(messenger, database))
    web.run_app(
        app,
        host=host,
        port=port,
        access_log=LOGGER,
        access_log_format='%r: %s status, %b size, in %Tf s')


async def create_superadmins(messenger, database):
    if await database.is_superadmin_created() is not None:
        return

    superadmins = os.environ.get("SUPERADMINS").split()
    superadmins_passwords = os.environ.get("SUPERADMINS_PASSWORDS").split()

    superadmins_size = len(superadmins)
    i = 0

    if superadmins_size != len(superadmins_passwords):
        LOGGER.exception("Superadmin passwords must be the same number as superadmin IDs")
        sys.exit(1)

    while i < superadmins_size:
        public_key, private_key = messenger.get_new_key_pair()

        await messenger.send_create_voter_transaction(
            private_key=private_key,
            voter_id=superadmins[i],
            public_key=public_key,
            name=superadmins[i],
            created_at=get_time(),
            type='SUPERADMIN')

        encrypted_private_key = encrypt_private_key(os.environ.get("AES_KEY"), public_key, private_key)
        hashed_password = hash_password(superadmins_passwords[i])

        await database.create_auth_entry(public_key, encrypted_private_key, hashed_password)
        i += 1

    LOGGER.info('Created Super Admin accounts')


def encrypt_private_key(aes_key, public_key, private_key):
    init_vector = bytes.fromhex(public_key[:32])
    cipher = AES.new(bytes.fromhex(aes_key), AES.MODE_CBC, init_vector)
    return cipher.encrypt(private_key)


def hash_password(password):
    return bcrypt.hashpw(bytes(password, 'utf-8'), bcrypt.gensalt())


def get_time():
    dts = datetime.datetime.utcnow()
    return round(time.mktime(dts.timetuple()) + dts.microsecond / 1e6)


def main():
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)

    try:
        opts = parse_args(sys.argv[1:])

        init_console_logging(verbose_level=opts.verbose)

        validator_url = opts.connect
        if "tcp://" not in validator_url:
            validator_url = "tcp://" + validator_url

        database = Database(
            opts.db_host,
            opts.db_port,
            opts.db_name,
            opts.db_user,
            opts.db_password,
            loop)

        messenger = Messenger(validator_url, database)



        try:
            host, port = opts.bind.split(":")
            port = int(port)
        except ValueError:
            print("Unable to parse binding {}: Must be in the format"
                  " host:port".format(opts.bind))
            sys.exit(1)

        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)

        start_rest_api(host, port, messenger, database)
    except Exception as err:  # pylint: disable=broad-except
        LOGGER.exception(err)
        sys.exit(1)
    finally:
        database.disconnect()
        messenger.close_validator_connection()

