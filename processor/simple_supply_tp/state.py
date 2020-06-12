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

from simple_supply_addressing import addresser

from simple_supply_protobuf import agent_pb2
from simple_supply_protobuf import record_pb2
from simple_supply_protobuf import election_pb2
from simple_supply_protobuf import votingOption_pb2
from simple_supply_protobuf import pollRegistration_pb2
from simple_supply_protobuf import voter_pb2
from simple_supply_protobuf import vote_pb2


class SimpleSupplyState(object):
    def __init__(self, context, timeout=2):
        self._context = context
        self._timeout = timeout

    def set_election(self,
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
                     timestamp):
        """Creates a new election in state

            Args:
                election_id (str): Unique ID of the election
                name (str): Name of the election
                description (str): Description of the election
                start_timestamp (int): Unix UTC timestamp of when the election start
                end_timestamp (int): Unix UTC timestamp of when the election end
                results_permission (string): Defines if its possible to change the voting option of the election
                can_show_realtime (bool): Defines if the results of the election will be show realtime
                can_change_vote  (bool): Defines if the results of the election will be presented
                admin_id (int):  Unique ID of the administrator
                status (bool): Defines if the election is online or canceled
                timestamp (int): Timestamp
        """
        address = addresser.get_election_address(election_id)

        election = election_pb2.Election(
            election_id=election_id,
            name=name,
            description=description,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            results_permission=results_permission,
            can_change_vote=can_change_vote,
            can_show_realtime=can_show_realtime,
            admin_id=admin_id,
            status=status,
            timestamp=timestamp)

        container = election_pb2.ElectionContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([election])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def set_voting_option(self,
                          voting_option_id,
                          name,
                          description,
                          election_id,
                          status):
        """Creates a new voting option in state

            Args:
                voting_option_id (str): Unique ID of the voting option
                name (str): Name of the voting option
                description (str): Description of the voting option
                election_id (str): Unique ID of the election
                status (bool): Defines if the voting option is activated or disable
        """
        address = addresser.get_voting_option_address(voting_option_id)

        voting_option = votingOption_pb2.VotingOption(
            voting_option_id=voting_option_id,
            name=name,
            description=description,
            election_id=election_id,
            status=status)

        container = votingOption_pb2.VotingOptionContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([voting_option])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def set_poll_registration(self,
                              voter_id,
                              name,
                              election_id,
                              status):
        """Creates a new poll registration in state

            Args:
                voter_id (str): Unique ID of the voter
                name (str): Name of the voting option
                election_id (str): Unique ID of the election
                status (bool): Defines if the user in poll registration is activated or disable
        """
        address = addresser.get_poll_registration_address(voter_id)

        poll_registration = pollRegistration_pb2.PollRegistration(
            voter_id=voter_id,
            name=name,
            election_id=election_id,
            status=status)

        container = pollRegistration_pb2.PollRegistrationContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([poll_registration])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_voter(self,
                  public_key):
        """Gets the voter associated with the public_key

        Args:
            public_key (str): The public key of the voter

        Returns:
            voter_pb2.Voter: Voter with the provided public_key
        """
        address = addresser.get_voter_address(public_key)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = voter_pb2.VoterContainer()
            container.ParseFromString(state_entries[0].data)
            for voter in container.entries:
                if voter.public_key == public_key:
                    return voter

        return None

    def set_voter(self,
                  voter_id,
                  public_key,
                  name,
                  created_at,
                  type):
        """Creates a new voter in state

        Args:
            voter_id (str): The email of the voter
            public_key (str): The public key of the voter
            name (str): The human-readable name of the voter
            created_at (int): Unix UTC timestamp of when the agent was created
            type (str): The type of user of the voter
        """
        address = addresser.get_voter_address(public_key)
        voter = voter_pb2.Voter(
            voter_id=voter_id,
            public_key=public_key,
            name=name,
            created_at=created_at,
            type=type)
        container = voter_pb2.VoterContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([voter])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def set_vote(self,
                 vote_id,
                 timestamp,
                 voter_id,
                 election_id,
                 voting_option_id):
        """Creates a new vote in state

            Args:
                vote_id (str): Unique ID of the vote
                timestamp (int): Timestamp
                voter_id (str): Unique ID of the voting option
                election_id (str): Unique ID of the election
                voting_option_id (str): Unique ID of the voting option
        """
        address = addresser.get_vote_address(vote_id)
        vote = vote_pb2.Vote(
            vote_id=vote_id,
            timestamp=timestamp,
            voter_id=voter_id,
            election_id=election_id,
            voting_option_id=voting_option_id)

        container = vote_pb2.VoteContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([vote])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_vote(self,
                    vote_id,
                    timestamp,
                    voting_option_id):

        address = addresser.get_vote_address(vote_id)
        container = vote_pb2.VoteContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)

        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for vote in container.entries:
                if vote.vote_id == vote_id:
                    vote.timestamp = timestamp
                    vote.voting_option_id = voting_option_id

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_election(self,
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
                        timestamp):

        address = addresser.get_election_address(election_id)
        container = election_pb2.ElectionContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)

        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for election in container.entries:
                if election.election_id == election_id:
                    election.name = name
                    election.description = description
                    election.start_timestamp = start_timestamp
                    election.end_timestamp = end_timestamp
                    election.results_permission = results_permission
                    election.can_change_vote = can_change_vote
                    election.can_show_realtime = can_show_realtime
                    election.admin_id = admin_id
                    election.status = status
                    election.timestamp = timestamp

        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_agent(self, public_key):
        """Gets the agent associated with the public_key

        Args:
            public_key (str): The public key of the agent

        Returns:
            agent_pb2.Agent: Agent with the provided public_key
        """
        address = addresser.get_agent_address(public_key)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = agent_pb2.AgentContainer()
            container.ParseFromString(state_entries[0].data)
            for agent in container.entries:
                if agent.public_key == public_key:
                    return agent

        return None

    def set_agent(self, public_key, name, timestamp):
        """Creates a new agent in state

        Args:
            public_key (str): The public key of the agent
            name (str): The human-readable name of the agent
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        address = addresser.get_agent_address(public_key)
        agent = agent_pb2.Agent(
            public_key=public_key, name=name, timestamp=timestamp)
        container = agent_pb2.AgentContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([agent])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def get_record(self, record_id):
        """Gets the record associated with the record_id

        Args:
            record_id (str): The id of the record

        Returns:
            record_pb2.Record: Record with the provided record_id
        """
        address = addresser.get_record_address(record_id)
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container = record_pb2.RecordContainer()
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    return record

        return None

    def set_record(self,
                   public_key,
                   latitude,
                   longitude,
                   record_id,
                   timestamp):
        """Creates a new record in state

        Args:
            public_key (str): The public key of the agent creating the record
            latitude (int): Initial latitude of the record
            longitude (int): Initial latitude of the record
            record_id (str): Unique ID of the record
            timestamp (int): Unix UTC timestamp of when the agent was created
        """
        address = addresser.get_record_address(record_id)
        owner = record_pb2.Record.Owner(
            agent_id=public_key,
            timestamp=timestamp)
        location = record_pb2.Record.Location(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp)
        record = record_pb2.Record(
            record_id=record_id,
            owners=[owner],
            locations=[location])
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)

        container.entries.extend([record])
        data = container.SerializeToString()

        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def transfer_record(self, receiving_agent, record_id, timestamp):
        owner = record_pb2.Record.Owner(
            agent_id=receiving_agent,
            timestamp=timestamp)
        address = addresser.get_record_address(record_id)
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    record.owners.extend([owner])
        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)

    def update_record(self, latitude, longitude, record_id, timestamp):
        location = record_pb2.Record.Location(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp)
        address = addresser.get_record_address(record_id)
        container = record_pb2.RecordContainer()
        state_entries = self._context.get_state(
            addresses=[address], timeout=self._timeout)
        if state_entries:
            container.ParseFromString(state_entries[0].data)
            for record in container.entries:
                if record.record_id == record_id:
                    record.locations.extend([location])
        data = container.SerializeToString()
        updated_state = {}
        updated_state[address] = data
        self._context.set_state(updated_state, timeout=self._timeout)
