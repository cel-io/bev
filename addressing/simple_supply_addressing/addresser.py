
import enum
import hashlib


FAMILY_NAME = 'bev'
FAMILY_VERSION = '0.1'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[:6]
AGENT_PREFIX = '00'
RECORD_PREFIX = '01'
ELECTION_PREFIX = '02'
VOTING_OPTION_PREFIX = '03'
POLL_REGISTRATION_PREFIX = '04'
VOTER_PREFIX = '05'




@enum.unique
class AddressSpace(enum.IntEnum):
    AGENT = 0
    RECORD = 1
    ELECTION = 2
    VOTING_OPTION = 3
    POLL_REGISTRATION = 4
    VOTER = 5

    OTHER_FAMILY = 100


def get_election_address(election_id):
    return NAMESPACE + ELECTION_PREFIX + hashlib.sha512(
        election_id.encode('utf-8')).hexdigest()[:62]


def get_voting_option_address(voting_option_id):
    return NAMESPACE + VOTING_OPTION_PREFIX + hashlib.sha512(
        voting_option_id.encode('utf-8')).hexdigest()[:62]


def get_poll_registration_address(voter_id):
    return NAMESPACE + POLL_REGISTRATION_PREFIX + hashlib.sha512(
        voter_id.encode('utf-8')).hexdigest()[:62]


def get_voter_address(public_key):
    return NAMESPACE + VOTER_PREFIX + hashlib.sha512(
        public_key.encode('utf-8')).hexdigest()[:62]


def get_agent_address(public_key):
    return NAMESPACE + AGENT_PREFIX + hashlib.sha512(
        public_key.encode('utf-8')).hexdigest()[:62]


def get_record_address(record_id):
    return NAMESPACE + RECORD_PREFIX + hashlib.sha512(
        record_id.encode('utf-8')).hexdigest()[:62]


def get_address_type(address):
    if address[:len(NAMESPACE)] != NAMESPACE:
        return AddressSpace.OTHER_FAMILY

    infix = address[6:8]

    if infix == '00':
        return AddressSpace.AGENT
    if infix == '01':
        return AddressSpace.RECORD
    if infix == '02':
        return AddressSpace.ELECTION
    if infix == '03':
        return AddressSpace.VOTING_OPTION
    if infix == '04':
        return AddressSpace.POLL_REGISTRATION
    if infix == '05':
        return AddressSpace.VOTER

    return AddressSpace.OTHER_FAMILY
