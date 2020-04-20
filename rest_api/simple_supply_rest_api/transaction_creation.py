import hashlib

from sawtooth_rest_api.protobuf import batch_pb2
from sawtooth_rest_api.protobuf import transaction_pb2

from simple_supply_addressing import addresser

from simple_supply_protobuf import payload_pb2

import time


def make_create_election_transaction(transaction_signer,
                                     batch_signer,
                                     election_id,
                                     name,
                                     description,
                                     start_timestamp,
                                     end_timestamp,
                                     results_permission,
                                     can_show_realtime,
                                     can_change_vote,
                                     admin_id,
                                     timestamp):
    """Make a CreateElectionAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        election_id (str): Unique ID of the election
        name (str): Name of the election
        description (str): Description of the election
        start_timestamp (int): Unix UTC timestamp of when the election start
        end_timestamp (int): Unix UTC timestamp of when the election end
        results_permission (int): Defines if its possible to change the voting option of the election
        can_show_realtime (bool): Defines if the results of the election will be show realtime
        can_change_vote  (bool): Defines if the results of the election will be presented
        admin_id (str):  Unique ID of the administrator
        timestamp (int): Unix UTC timestamp of when the election is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """

    inputs = [
        addresser.get_agent_address(
            transaction_signer.get_public_key().as_hex()),
        addresser.get_election_address(election_id)
    ]

    outputs = [addresser.get_election_address(election_id)]

    action = payload_pb2.CreateElectionAction(
        election_id=election_id,
        name=name,
        description=description,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        results_permission=results_permission,
        can_change_vote=can_change_vote,
        can_show_realtime=can_show_realtime,
        admin_id=admin_id)

    payload = payload_pb2.BevPayload(
        action=payload_pb2.BevPayload.CREATE_ELECTION,
        create_election=action,
        timestamp=timestamp
    )
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_voting_option_transaction(transaction_signer,
                                          batch_signer,
                                          voting_option_id,
                                          name,
                                          description,
                                          election_id,
                                          timestamp):
    """Make a CreateVotingOptionAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        voting_option_id (str): Unique ID of the voting option
        name (str): Name of the voting option
        description (str): Description of the voting option
        election_id (str):  Unique ID of the election
        timestamp (int): Unix UTC timestamp of when the election is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """

    inputs = [
        addresser.get_agent_address(
            transaction_signer.get_public_key().as_hex()),
        addresser.get_voting_option_address(voting_option_id)
    ]

    outputs = [addresser.get_voting_option_address(voting_option_id)]

    action = payload_pb2.CreateVotingOptionAction(
        voting_option_id=voting_option_id,
        name=name,
        description=description,
        election_id=election_id)

    payload = payload_pb2.BevPayload(
        action=payload_pb2.BevPayload.CREATE_VOTING_OPTION,
        create_voting_option=action,
        timestamp=timestamp
    )
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_poll_registration_transaction(transaction_signer,
                                              batch_signer,
                                              voter_id,
                                              name,
                                              election_id,
                                              timestamp):
    """Make a CreatePollRegistrationAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        voter_id (str): Unique ID of the voter
        name (str): Name of the voter
        election_id (str):  Unique ID of the election
        timestamp (int): Unix UTC timestamp of when the election is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """

    inputs = [
        addresser.get_agent_address(
            transaction_signer.get_public_key().as_hex()),
        addresser.get_poll_registration_address(voter_id)
    ]

    outputs = [addresser.get_poll_registration_address(voter_id)]

    action = payload_pb2.CreatePollRegistrationAction(
        voter_id=voter_id,
        name=name,
        election_id=election_id)

    payload = payload_pb2.BevPayload(
        action=payload_pb2.BevPayload.CREATE_POLL_REGISTRATION,
        create_poll_registration=action,
        timestamp=timestamp
    )
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_agent_transaction(transaction_signer,
                                  batch_signer,
                                  name,
                                  timestamp):
    """Make a CreateAgentAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        name (str): The agent's name
        timestamp (int): Unix UTC timestamp of when the agent is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch

    """

    agent_address = addresser.get_agent_address(
        transaction_signer.get_public_key().as_hex())

    inputs = [agent_address]

    outputs = [agent_address]

    action = payload_pb2.CreateAgentAction(name=name)

    payload = payload_pb2.BevPayload(
        action=payload_pb2.BevPayload.CREATE_AGENT,
        create_agent=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_create_record_transaction(transaction_signer,
                                   batch_signer,
                                   latitude,
                                   longitude,
                                   record_id,
                                   timestamp):
    """Make a CreateRecordAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        latitude (int): Initial latitude of the record
        longitude (int): Initial latitude of the record
        record_id (str): Unique ID of the record
        timestamp (int): Unix UTC timestamp of when the agent is created

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """

    inputs = [
        addresser.get_agent_address(
            transaction_signer.get_public_key().as_hex()),
        addresser.get_record_address(record_id)
    ]

    outputs = [addresser.get_record_address(record_id)]

    action = payload_pb2.CreateRecordAction(
        record_id=record_id,
        latitude=latitude,
        longitude=longitude)

    payload = payload_pb2.BevPayload(
        action=payload_pb2.BevPayload.CREATE_RECORD,
        create_record=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_transfer_record_transaction(transaction_signer,
                                     batch_signer,
                                     receiving_agent,
                                     record_id,
                                     timestamp):
    """Make a CreateRecordAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        receiving_agent (str): Public key of the agent receiving the record
        record_id (str): Unique ID of the record
        timestamp (int): Unix UTC timestamp of when the record is transferred

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """
    sending_agent_address = addresser.get_agent_address(
        transaction_signer.get_public_key().as_hex())
    receiving_agent_address = addresser.get_agent_address(receiving_agent)
    record_address = addresser.get_record_address(record_id)

    inputs = [sending_agent_address, receiving_agent_address, record_address]

    outputs = [record_address]

    action = payload_pb2.TransferRecordAction(
        record_id=record_id,
        receiving_agent=receiving_agent)

    payload = payload_pb2.BevPayload(
        action=payload_pb2.BevPayload.TRANSFER_RECORD,
        transfer_record=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def make_update_record_transaction(transaction_signer,
                                   batch_signer,
                                   latitude,
                                   longitude,
                                   record_id,
                                   timestamp):
    """Make a CreateRecordAction transaction and wrap it in a batch

    Args:
        transaction_signer (sawtooth_signing.Signer): The transaction key pair
        batch_signer (sawtooth_signing.Signer): The batch key pair
        latitude (int): Updated latitude of the location
        longitude (int): Updated longitude of the location
        record_id (str): Unique ID of the record
        timestamp (int): Unix UTC timestamp of when the record is updated

    Returns:
        batch_pb2.Batch: The transaction wrapped in a batch
    """
    agent_address = addresser.get_agent_address(
        transaction_signer.get_public_key().as_hex())
    record_address = addresser.get_record_address(record_id)

    inputs = [agent_address, record_address]

    outputs = [record_address]

    action = payload_pb2.UpdateRecordAction(
        record_id=record_id,
        latitude=latitude,
        longitude=longitude)

    payload = payload_pb2.BevPayload(
        action=payload_pb2.BevPayload.UPDATE_RECORD,
        update_record=action,
        timestamp=timestamp)
    payload_bytes = payload.SerializeToString()

    return _make_batch(
        payload_bytes=payload_bytes,
        inputs=inputs,
        outputs=outputs,
        transaction_signer=transaction_signer,
        batch_signer=batch_signer)


def _make_batch(payload_bytes,
                inputs,
                outputs,
                transaction_signer,
                batch_signer):
    transaction_header = transaction_pb2.TransactionHeader(
        family_name=addresser.FAMILY_NAME,
        family_version=addresser.FAMILY_VERSION,
        inputs=inputs,
        outputs=outputs,
        signer_public_key=transaction_signer.get_public_key().as_hex(),
        batcher_public_key=batch_signer.get_public_key().as_hex(),
        dependencies=[],
        payload_sha512=hashlib.sha512(payload_bytes).hexdigest())
    transaction_header_bytes = transaction_header.SerializeToString()

    transaction = transaction_pb2.Transaction(
        header=transaction_header_bytes,
        header_signature=transaction_signer.sign(transaction_header_bytes),
        payload=payload_bytes)

    batch_header = batch_pb2.BatchHeader(
        signer_public_key=batch_signer.get_public_key().as_hex(),
        transaction_ids=[transaction.header_signature])
    batch_header_bytes = batch_header.SerializeToString()

    batch = batch_pb2.Batch(
        header=batch_header_bytes,
        header_signature=batch_signer.sign(batch_header_bytes),
        transactions=[transaction])

    return batch
