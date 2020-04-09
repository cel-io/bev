
import enum
import hashlib


FAMILY_NAME = 'simple_supply'
FAMILY_VERSION = '0.1'
NAMESPACE = hashlib.sha512(FAMILY_NAME.encode('utf-8')).hexdigest()[:6]
AGENT_PREFIX = '00'
RECORD_PREFIX = '01'
ELECTION_PREFIX = '02'


@enum.unique
class AddressSpace(enum.IntEnum):
    AGENT = 0
    RECORD = 1
    ELECTION = 2

    OTHER_FAMILY = 100


def get_election_address(id):
    return NAMESPACE + ELECTION_PREFIX + hashlib.sha512(
        id.encode('utf-8')).hexdigest()[:62]


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

    return AddressSpace.OTHER_FAMILY
