
import argparse
import asyncio
import logging
import sys

from zmq.asyncio import ZMQEventLoop

from sawtooth_sdk.processor.log import init_console_logging

from aiohttp import web

from simple_supply_rest_api.route_handler import RouteHandler
from simple_supply_rest_api.database import Database
from simple_supply_rest_api.messaging import Messenger

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
    asyncio.ensure_future(database.connect())

    app = web.Application(loop=loop)
    # WARNING: UNSAFE KEY STORAGE
    # In a production application these keys should be passed in more securely
    app['aes_key'] = 'ffffffffffffffffffffffffffffffff'
    app['secret_key'] = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

    messenger.open_validator_connection()

    handler = RouteHandler(loop, messenger, database)

    app.router.add_post('/elections', handler.create_election)
    app.router.add_get('/elections/current', handler.list_elections_current)
    app.router.add_get('/elections/past', handler.list_elections_past)
    app.router.add_get('/elections/{electionId}', handler.get_election)
    app.router.add_get('/elections/{electionId}/number_of_votes', handler.get_election_votes)
    app.router.add_get('/elections/{electionId}/poll_book', handler.get_poll_registrations)
    app.router.add_get('/elections/{electionId}/voting_options', handler.list_voting_options_election)
    app.router.add_post('/elections', handler.create_election)
    app.router.add_put('/elections/{electionId}/change_status', handler.update_election)

    app.router.add_post('/voters', handler.create_voter)

    app.router.add_get('/votes/{voteId}', handler.list_vote)
    app.router.add_get('/votes/{voterId}/voter', handler.get_vote_voter_id)
    app.router.add_post('/votes/{votingOptionId}', handler.create_vote)
    app.router.add_put('/votes/{voteId}/update', handler.update_vote)

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

    LOGGER.info('Starting Simple Supply REST API on %s:%s', host, port)
    web.run_app(
        app,
        host=host,
        port=port,
        access_log=LOGGER,
        access_log_format='%r: %s status, %b size, in %Tf s')


def main():
    loop = ZMQEventLoop()
    asyncio.set_event_loop(loop)

    try:
        opts = parse_args(sys.argv[1:])

        init_console_logging(verbose_level=opts.verbose)

        validator_url = opts.connect
        if "tcp://" not in validator_url:
            validator_url = "tcp://" + validator_url
        messenger = Messenger(validator_url)

        database = Database(
            opts.db_host,
            opts.db_port,
            opts.db_name,
            opts.db_user,
            opts.db_password,
            loop)

        try:
            host, port = opts.bind.split(":")
            port = int(port)
        except ValueError:
            print("Unable to parse binding {}: Must be in the format"
                  " host:port".format(opts.bind))
            sys.exit(1)

        start_rest_api(host, port, messenger, database)
    except Exception as err:  # pylint: disable=broad-except
        LOGGER.exception(err)
        sys.exit(1)
    finally:
        database.disconnect()
        messenger.close_validator_connection()

