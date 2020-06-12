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

import logging
import time
from logging import Logger

import psycopg2
from psycopg2.extras import RealDictCursor


LOGGER: Logger = logging.getLogger(__name__)


CREATE_BLOCK_STMTS = """
CREATE TABLE IF NOT EXISTS blocks (
    block_num  bigint PRIMARY KEY,
    block_id   varchar
);
"""

CREATE_AUTH_STMTS = """
CREATE TABLE IF NOT EXISTS auth (
    public_key            varchar PRIMARY KEY,
    hashed_password       varchar,
    encrypted_private_key varchar
)
"""

CREATE_RECORD_STMTS = """
CREATE TABLE IF NOT EXISTS records (
    id               bigserial PRIMARY KEY,
    record_id        varchar,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_RECORD_LOCATION_STMTS = """
CREATE TABLE IF NOT EXISTS record_locations (
    id               bigserial PRIMARY KEY,
    record_id        varchar,
    latitude         bigint,
    longitude        bigint,
    timestamp        bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_RECORD_OWNER_STMTS = """
CREATE TABLE IF NOT EXISTS record_owners (
    id               bigserial PRIMARY KEY,
    record_id        varchar,
    agent_id         varchar,
    timestamp        bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_AGENT_STMTS = """
CREATE TABLE IF NOT EXISTS agents (
    id               bigserial PRIMARY KEY,
    public_key       varchar,
    name             varchar,
    timestamp        bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_TYPES_STMTS = """
DO $$ BEGIN
    CREATE TYPE results_permission_type AS ENUM('PRIVATE', 'VOTERS_ONLY', 'PUBLIC');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE voter_type AS ENUM('VOTER', 'ADMIN', 'SUPERADMIN');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE multiple_options_criteria_type AS ENUM('NONE', 'AT_LEAST', 'EQUAL_TO', 'AT_MOST', 'BETWEEN');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;
"""

CREATE_ELECTION_STMTS = """
CREATE TABLE IF NOT EXISTS elections (
    id                          bigserial PRIMARY KEY,
    election_id                 varchar,
    name                        varchar,
    description                 varchar,
    start_timestamp             bigint,
    end_timestamp               bigint,
    results_permission          results_permission_type,
    can_change_vote             boolean,
    can_show_realtime           boolean,
    admin_id                    varchar,
    status                      boolean,
    timestamp                   bigint,
    start_block_num             bigint,
    end_block_num               bigint
);
"""

CREATE_VOTING_OPTION_STMTS = """
CREATE TABLE IF NOT EXISTS voting_options (
    id               bigserial PRIMARY KEY,
    voting_option_id varchar,
    name             varchar,
    description      varchar,
    election_id      varchar,
    status           boolean,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_COUNT_VOTE_STMTS = """
CREATE TABLE IF NOT EXISTS count_votes (
    id               bigserial PRIMARY KEY,
    voting_option_id varchar,
    name             varchar,
    election_id      varchar,
    num_votes        smallint
);
"""

CREATE_VOTER_STMTS = """
CREATE TABLE IF NOT EXISTS voters (
    id               bigserial PRIMARY KEY,
    public_key       varchar,
    name             varchar,
    voter_id         varchar,
    type             voter_type,
    created_at       bigint,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_POLL_REGISTRATION_STMTS = """
CREATE TABLE IF NOT EXISTS poll_registrations (
    id               bigserial PRIMARY KEY,
    voter_id         varchar,
    name             varchar,
    election_id      varchar,
    status           boolean,
    start_block_num  bigint,
    end_block_num    bigint
);
"""

CREATE_VOTE_STMTS = """
CREATE TABLE IF NOT EXISTS votes (
    id               bigserial PRIMARY KEY,
    vote_id          varchar,
    timestamp        bigint,
    voter_id         varchar,
    election_id      varchar,
    voting_option_id         varchar,
    start_block_num  bigint,
    end_block_num    bigint
);
"""


class Database(object):
    """Simple object for managing a connection to a postgres database
    """
    def __init__(self, dsn):
        self._dsn = dsn
        self._conn = None

    def connect(self, retries=5, initial_delay=1, backoff=2):
        """Initializes a connection to the database

        Args:
            retries (int): Number of times to retry the connection
            initial_delay (int): Number of seconds wait between reconnects
            backoff (int): Multiplies the delay after each retry
        """
        LOGGER.info('Connecting to database')

        delay = initial_delay
        for attempt in range(retries):
            try:
                self._conn = psycopg2.connect(self._dsn)
                LOGGER.info('Successfully connected to database')
                return

            except psycopg2.OperationalError:
                LOGGER.debug(
                    'Connection failed.'
                    ' Retrying connection (%s retries remaining)',
                    retries - attempt)
                time.sleep(delay)
                delay *= backoff

        self._conn = psycopg2.connect(self._dsn)
        LOGGER.info('Successfully connected to database')

    def create_tables(self):
        """Creates the Simple Supply tables
        """
        with self._conn.cursor() as cursor:
            LOGGER.debug('Creating table: blocks')
            cursor.execute(CREATE_BLOCK_STMTS)

            LOGGER.debug('Creating table: auth')
            cursor.execute(CREATE_AUTH_STMTS)

            # LOGGER.debug('Creating table: records')
            # cursor.execute(CREATE_RECORD_STMTS)
            #
            # LOGGER.debug('Creating table: record_locations')
            # cursor.execute(CREATE_RECORD_LOCATION_STMTS)
            #
            # LOGGER.debug('Creating table: record_owners')
            # cursor.execute(CREATE_RECORD_OWNER_STMTS)
            #
            # LOGGER.debug('Creating table: agents')
            # cursor.execute(CREATE_AGENT_STMTS)

            LOGGER.debug('Creating types')
            cursor.execute(CREATE_TYPES_STMTS)

            LOGGER.debug('Creating table: elections')
            cursor.execute(CREATE_ELECTION_STMTS)

            LOGGER.debug('Creating table: voting_options')
            cursor.execute(CREATE_VOTING_OPTION_STMTS)

            LOGGER.debug('Creating table: voters')
            cursor.execute(CREATE_VOTER_STMTS)

            LOGGER.debug('Creating table: poll_registrations')
            cursor.execute(CREATE_POLL_REGISTRATION_STMTS)

            LOGGER.debug('Creating table: votes')
            cursor.execute(CREATE_VOTE_STMTS)

            LOGGER.debug('Creating table: count_votes')
            cursor.execute(CREATE_COUNT_VOTE_STMTS)

        self._conn.commit()

    def disconnect(self):
        """Closes the connection to the database
        """
        LOGGER.info('Disconnecting from database')
        if self._conn is not None:
            self._conn.close()

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def fetch_block(self, block_num):
        if block_num is None:
            return

        fetch = """
        SELECT block_num, block_id FROM blocks WHERE block_num = {}
        """.format(block_num)

        with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(fetch)
            block = cursor.fetchone()

        return block

    def drop_fork(self, block_num):
        """Deletes all resources from a particular block_num
        """
        delete_elections = """
               DELETE FROM elections WHERE start_block_num >= {}
               """.format(block_num)
        update_elections = """
               UPDATE elections SET end_block_num = null
               WHERE end_block_num >= {}
               """.format(block_num)

        delete_agents = """
        DELETE FROM agents WHERE start_block_num >= {}
        """.format(block_num)
        update_agents = """
        UPDATE agents SET end_block_num = null
        WHERE end_block_num >= {}
        """.format(block_num)

        delete_record_locations = """
        DELETE FROM record_owners WHERE record_id =
        (SELECT record_id FROM records WHERE start_block_num >= {})
        """.format(block_num)
        delete_record_owners = """
        DELETE FROM record_owners WHERE record_id =
        (SELECT record_id FROM records WHERE start_block_num >= {})
        """.format(block_num)
        delete_records = """
        DELETE FROM records WHERE start_block_num >= {}
        """.format(block_num)
        update_records = """
        UPDATE records SET end_block_num = null
        WHERE end_block_num >= {}
        """.format(block_num)

        delete_blocks = """
        DELETE FROM blocks WHERE block_num >= {}
        """.format(block_num)

        with self._conn.cursor() as cursor:
            cursor.execute(delete_elections)
            cursor.execute(update_elections)
            cursor.execute(delete_agents)
            cursor.execute(update_agents)
            cursor.execute(delete_record_locations)
            cursor.execute(delete_record_owners)
            cursor.execute(delete_records)
            cursor.execute(update_records)
            cursor.execute(delete_blocks)

    def fetch_last_known_blocks(self, count):
        """Fetches the specified number of most recent blocks
        """
        fetch = """
        SELECT block_num, block_id FROM blocks
        ORDER BY block_num DESC LIMIT {}
        """.format(count)

        with self._conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(fetch)
            blocks = cursor.fetchall()

        return blocks

    def insert_block(self, block_dict):
        insert = """
        INSERT INTO blocks (
        block_num,
        block_id)
        VALUES ('{}', '{}');
        """.format(
            block_dict['block_num'],
            block_dict['block_id'])

        with self._conn.cursor() as cursor:
            cursor.execute(insert)

    def insert_election(self, election_dict):
        update_election = """
           UPDATE elections SET end_block_num = {}
           WHERE end_block_num = {} AND election_id = '{}'
           """.format(
            election_dict['start_block_num'],
            election_dict['end_block_num'],
            election_dict['election_id'],)

        insert_election = """
           INSERT INTO elections (
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
           timestamp,
           start_block_num,
           end_block_num)
           VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');
           """.format(
            election_dict['election_id'],
            election_dict['name'],
            election_dict['description'],
            election_dict['start_timestamp'],
            election_dict['end_timestamp'],
            election_dict['results_permission'],
            election_dict['can_change_vote'],
            election_dict['can_show_realtime'],
            election_dict['admin_id'],
            election_dict['status'],
            election_dict['timestamp'],
            election_dict['start_block_num'],
            election_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_election)
            cursor.execute(insert_election)

    def insert_vote(self, vote_dict):
        update_vote = """
           UPDATE votes SET end_block_num = {}
           WHERE end_block_num = {} AND vote_id = '{}'
           """.format(
            vote_dict['start_block_num'],
            vote_dict['end_block_num'],
            vote_dict['vote_id'],)

        insert_vote = """
           INSERT INTO votes (
           vote_id,  
           timestamp,
           voter_id,
           election_id,
           voting_option_id,
           start_block_num,
           end_block_num)
           VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');
           """.format(
            vote_dict['vote_id'],
            vote_dict['timestamp'],
            vote_dict['voter_id'],
            vote_dict['election_id'],
            vote_dict['voting_option_id'],
            vote_dict['start_block_num'],
            vote_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_vote)
            cursor.execute(insert_vote)

    def insert_voting_option(self, voting_option_dict):
        update_voting_option = """
           UPDATE voting_options SET end_block_num = {}
           WHERE end_block_num = {} AND voting_option_id = '{}'
           """.format(
            voting_option_dict['start_block_num'],
            voting_option_dict['end_block_num'],
            voting_option_dict['voting_option_id'],)

        insert_voting_option = """
           INSERT INTO voting_options (
           voting_option_id, 
           name, 
           description, 
           election_id,
           status,
           start_block_num,
           end_block_num)
           VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');
           """.format(
            voting_option_dict['voting_option_id'],
            voting_option_dict['name'],
            voting_option_dict['description'],
            voting_option_dict['election_id'],
            voting_option_dict['status'],
            voting_option_dict['start_block_num'],
            voting_option_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_voting_option)
            cursor.execute(insert_voting_option)

    def insert_poll_registration(self, poll_registration_dict):
        update_poll_registration = """
           UPDATE poll_registrations SET end_block_num = {}
           WHERE end_block_num = {} AND voter_id = '{}'
           """.format(
            poll_registration_dict['start_block_num'],
            poll_registration_dict['end_block_num'],
            poll_registration_dict['voter_id'],)

        insert_poll_registration = """
           INSERT INTO poll_registrations (
           voter_id, 
           name, 
           election_id,
           status,
           start_block_num,
           end_block_num)
           VALUES ('{}', '{}', '{}', '{}',  '{}', '{}');
           """.format(
            poll_registration_dict['voter_id'],
            poll_registration_dict['name'],
            poll_registration_dict['election_id'],
            poll_registration_dict['status'],
            poll_registration_dict['start_block_num'],
            poll_registration_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_poll_registration)
            cursor.execute(insert_poll_registration)

    def insert_voter(self, voter_dict):
        update_voter = """
           UPDATE voters SET end_block_num = {}
           WHERE end_block_num = {} AND voter_id = '{}'
           """.format(
            voter_dict['start_block_num'],
            voter_dict['end_block_num'],
            voter_dict['voter_id'],)

        insert_voter = """
           INSERT INTO voters (
           voter_id,
           public_key, 
           name, 
           created_at,
           type,
           start_block_num,
           end_block_num)
           VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}');
           """.format(
            voter_dict['voter_id'],
            voter_dict['public_key'],
            voter_dict['name'],
            voter_dict['created_at'],
            voter_dict['type'],
            voter_dict['start_block_num'],
            voter_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_voter)
            cursor.execute(insert_voter)

    def insert_agent(self, agent_dict):
        update_agent = """
        UPDATE agents SET end_block_num = {}
        WHERE end_block_num = {} AND public_key = '{}'
        """.format(
            agent_dict['start_block_num'],
            agent_dict['end_block_num'],
            agent_dict['public_key'])

        insert_agent = """
        INSERT INTO agents (
        public_key,
        name,
        timestamp,
        start_block_num,
        end_block_num)
        VALUES ('{}', '{}', '{}', '{}', '{}');
        """.format(
            agent_dict['public_key'],
            agent_dict['name'],
            agent_dict['timestamp'],
            agent_dict['start_block_num'],
            agent_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_agent)
            cursor.execute(insert_agent)

    def insert_record(self, record_dict):
        update_record = """
        UPDATE records SET end_block_num = {}
        WHERE end_block_num = {} AND record_id = '{}'
        """.format(
            record_dict['start_block_num'],
            record_dict['end_block_num'],
            record_dict['record_id'])

        insert_record = """
        INSERT INTO records (
        record_id,
        start_block_num,
        end_block_num)
        VALUES ('{}', '{}', '{}');
        """.format(
            record_dict['record_id'],
            record_dict['start_block_num'],
            record_dict['end_block_num'])

        with self._conn.cursor() as cursor:
            cursor.execute(update_record)
            cursor.execute(insert_record)

        self._insert_record_locations(record_dict)
        self._insert_record_owners(record_dict)

    def _insert_record_locations(self, record_dict):
        update_record_locations = """
        UPDATE record_locations SET end_block_num = {}
        WHERE end_block_num = {} AND record_id = '{}'
        """.format(
            record_dict['start_block_num'],
            record_dict['end_block_num'],
            record_dict['record_id'])

        insert_record_locations = [
            """
            INSERT INTO record_locations (
            record_id,
            latitude,
            longitude,
            timestamp,
            start_block_num,
            end_block_num)
            VALUES ('{}', '{}', '{}', '{}', '{}', '{}');
            """.format(
                record_dict['record_id'],
                location['latitude'],
                location['longitude'],
                location['timestamp'],
                record_dict['start_block_num'],
                record_dict['end_block_num'])
            for location in record_dict['locations']
        ]
        with self._conn.cursor() as cursor:
            cursor.execute(update_record_locations)
            for insert in insert_record_locations:
                cursor.execute(insert)

    def _insert_record_owners(self, record_dict):
        update_record_owners = """
        UPDATE record_owners SET end_block_num = {}
        WHERE end_block_num = {} AND record_id = '{}'
        """.format(
            record_dict['start_block_num'],
            record_dict['end_block_num'],
            record_dict['record_id'])

        insert_record_owners = [
            """
            INSERT INTO record_owners (
            record_id,
            agent_id,
            timestamp,
            start_block_num,
            end_block_num)
            VALUES ('{}', '{}', '{}', '{}', '{}');
            """.format(
                record_dict['record_id'],
                owner['agent_id'],
                owner['timestamp'],
                record_dict['start_block_num'],
                record_dict['end_block_num'])
            for owner in record_dict['owners']
        ]
        with self._conn.cursor() as cursor:
            cursor.execute(update_record_owners)
            for insert in insert_record_owners:
                cursor.execute(insert)
