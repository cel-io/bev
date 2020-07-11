<template>
    <div>
        <div class="card box shadow">
            <div class="card-content">
                <template v-if="isLoading">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            <b-icon pack="fas" icon="sync-alt" size="is-large" custom-class="fa-spin">></b-icon>
                        </div>
                    </div>
                </template>
                <template v-else>
                    <div class="columns is-vcentered">
                        <div class="column is-6">
                            <span class="is-size-3 has-margin-right-5">{{election.name}}</span>
                        </div>
                        <template v-if="asAdmin">
                            <div class="column is-6 has-text-right" v-if="election.end_timestamp >= currentTimestamp && currentTimestamp >= election.start_timestamp">
                                <b-tooltip v-if="canUpdate" type="is-dark" label="Voters can change their vote multiple times after their initial choice">
                                    <b-tag class="has-margin-top-5 has-margin-right-5">Mutable Votes</b-tag>
                                </b-tooltip>
                                <b-tag class="has-margin-top-5 has-margin-right-5" type="is-danger">Live</b-tag>
                            </div>
                            <div class="column is-6 has-text-right" v-else-if="election.end_timestamp < currentTimestamp">
                                <b-tag class="has-margin-top-5 has-margin-right-5" type="is-danger">Terminated</b-tag>
                            </div>
                            <div class="column is-6 has-text-right" v-else-if="election.start_timestamp > currentTimestamp">
                                <b-tooltip v-if="canUpdate" type="is-dark" label="Voters can change their vote multiple times after their initial choice">
                                    <b-tag class="has-margin-top-5 has-margin-right-5">Mutable Votes</b-tag>
                                </b-tooltip>
                                <b-button type="is-primary" rounded tag="router-link" :to="'/election/' + election.election_id + '/update'">Update</b-button>
                                <b-tooltip :active="election.status" type="is-dark" label="Disabled elections won't take place">
                                    <b-button rounded :type="election.status ? 'is-danger' : 'is-success'" @click="toggleElectionStatus" :loading="isLoadingToggle">{{election.status ? 'Disable' : 'Enable'}}</b-button>
                                </b-tooltip>
                            </div>
                        </template>
                        <template v-else>
                            <div class="column is-6 has-text-right" v-if="election.end_timestamp >= currentTimestamp && currentTimestamp >= election.start_timestamp">
                                <b-tag class="has-margin-top-5 has-margin-right-5" type="is-danger">Live</b-tag>
                                <b-tooltip v-if="!canUpdate && alreadyVote" type="is-dark" label="You already have submitted a vote. This election doesn't allow mutable votes.">
                                    <b-tag class="has-margin-top-5 has-margin-right-5">Can't vote anymore.</b-tag>
                                </b-tooltip>
                                <b-tooltip v-else-if="canUpdate" type="is-dark" label="Voters can change their vote multiple times after their initial choice">
                                    <b-tag class="has-margin-top-5 has-margin-right-5">Mutable Votes</b-tag>
                                </b-tooltip>
                                <b-button v-if="canUpdate && alreadyVote && election.can_vote" tag="router-link" :to="'/vote/' + vote.vote_id + '/update'" rounded type="is-info">Update Vote</b-button>
                                <b-button v-else-if="!alreadyVote && election.can_vote" tag="router-link" :to="'/election/' + election.election_id + '/vote'" rounded type="is-info">Vote</b-button>
                            </div>
                            <div class="column is-6 has-text-right" v-else-if="election.end_timestamp < currentTimestamp">
                                <b-tag class="has-margin-top-5 has-margin-right-5" type="is-danger">Terminated</b-tag>
                            </div>
                        </template>
                    </div>
                    <div class="columns">
                        <div class="column is-12">
                            <b-tabs v-model="activeTab" expanded>
                                <b-tab-item label="My Vote" v-if="!asAdmin && election.can_vote">
                                    <br>
                                    <div v-if="!this.alreadyVote" class="has-text-centered" >
                                        <span>You didn't vote yet.</span>
                                    </div>
                                    <div v-else class="card box">
                                        <div class="card-content">
                                            <div class="columns">
                                                <div class="column">
                                                    <span class="has-text-weight-bold">Name: </span> {{my_voting_option.name}}
                                                </div>
                                            </div>
                                            <div class="columns">
                                                <div class="column">
                                                    <span class="has-text-weight-bold">Description: </span> {{my_voting_option.description}}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </b-tab-item>
                                <b-tab-item label="Informations">
                                    <div class="columns">
                                        <div class="column is-12">
                                            <span class="has-text-weight-bold">Description: </span> {{election.description}}
                                        </div>
                                    </div>
                                    <div class="columns">
                                        <div class="column">
                                            <span class="has-text-weight-bold">Start Time: </span> {{ toDate(election.start_timestamp) }}
                                        </div>
                                        <div class="column">
                                            <span class="has-text-weight-bold">End Time: </span> {{ toDate(election.end_timestamp) }}
                                        </div>
                                        <div class="column" v-if="election.end_timestamp >= currentTimestamp && currentTimestamp >= election.start_timestamp">
                                            <countdown :time="(election.end_timestamp - currentTimestamp ) * 1000">
                                                <template slot-scope="props"><span class="has-text-weight-bold">Time Remaining:</span> {{ props.days }} days, {{ props.hours }} hours, {{ props.minutes }} minutes, {{ props.seconds }} seconds.</template>
                                            </countdown>
                                        </div>
                                        <div class="column" v-if="currentTimestamp < election.start_timestamp">
                                            <countdown :time="(election.start_timestamp - currentTimestamp ) * 1000" v-if="election.status">
                                                <template slot-scope="props"><span class="has-text-weight-bold">Starts In:</span> {{ props.days }} days, {{ props.hours }} hours, {{ props.minutes }} minutes, {{ props.seconds }} seconds.</template>
                                            </countdown>
                                            <span v-else><span class="has-text-weight-bold">Starts In: </span> The election won't start if it is <b>disabled</b>.</span>
                                        </div>
                                    </div>
                                    <div class="columns" v-if="!asAdmin">
                                        <div class="column">
                                            <span class="has-text-weight-bold">Created By:</span> {{election.admin_name}}
                                        </div>
                                    </div>
                                    <div class="columns" v-else>
                                        <div class="column">
                                            <span class="has-text-weight-bold">Results Exposure:</span> {{election.results_permission == 'PRIVATE' ? 'Private - Only the administrator can view the results.' : (election.results_permission == 'VOTERS_ONLY' ? 'Voters Only - Only the administrator and the voters can view the results.' : 'Public - Everyone can view the results.' )}}
                                        </div>
                                        <div class="column">
                                            <span class="has-text-weight-bold">Realtime Results Exposure:</span> {{election.can_show_realtime ? 'Results can be viewed in real time.' : "Results can't be viewed in real time." }}
                                        </div>
                                    </div>
                                </b-tab-item>
                                <b-tab-item label="Ballot">
                                    <div class="card box" v-for="votingOption in votingOptions" :key="votingOption.id">
                                        <div class="card-content">
                                            <div class="columns">
                                                <div class="column">
                                                    <span class="has-text-weight-bold">Name: </span> {{votingOption.name}}
                                                </div>
                                            </div>
                                            <div class="columns">
                                                <div class="column">
                                                    <span class="has-text-weight-bold">Description: </span> {{votingOption.description}}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </b-tab-item>
                                <b-tab-item label="Results">
                                    <br>
                                    <div class=" has-text-centered" v-if="election.results_permission == 'PRIVATE' && this.$parent.user.type == 'VOTER' ">
                                        <span>Results are exclusive to the Adminstrator.</span>
                                    </div>
                                    <div v-else>
                                        <div class=" has-text-centered" v-if="!election.can_show_realtime && election.end_timestamp >= currentTimestamp && currentTimestamp >= election.start_timestamp ">
                                            <span>Election can't show realtime results during election time.</span>
                                        </div>
                                        <div v-else>
                                            <div class=" has-text-centered" v-if="this.num_votes_all == 0">
                                                <span>No votes submitted.</span>
                                            </div>
                                            <div v-else class="has-text-centered">
                                                <div class="columns">
                                                    <div class="column is-6">
                                                        <div class="title is-3" v-if="election.end_timestamp > currentTimestamp">
                                                            <strong>Total Votes</strong>
                                                        </div>
                                                        <div v-if="this.switchGraph" class="small_chart">
                                                            <pie-chart :chart-data="datacollectionPie"></pie-chart>
                                                        </div>
                                                        <div v-else class="small_chart">
                                                            <bar-chart :chart-data="datacollectionBar" :options="options"></bar-chart>
                                                        </div>
                                                        <b-switch v-model="switchGraph"> Show Pie Chart </b-switch>
                                                    </div>
                                                    <br>
                                                    <div class="column is-6">
                                                        <div class="title is-3" v-if="election.end_timestamp > currentTimestamp">
                                                            <strong>Votes Submitted</strong>
                                                        </div>
                                                        <div>
                                                            <div class="columns">
                                                                <div class="column is-6">
                                                                    <h6 class="title is-6">Participation Rate</h6>
                                                                    <b-message type="is-success" class="shadow">
                                                                        <h4 class="title is-4">{{ this.percentage_n_vote }} % Of Voters</h4>
                                                                    </b-message>
                                                                </div>
                                                                <div class="column is-6">
                                                                    <h6 class="title is-6">Abstention Rate</h6>
                                                                    <b-message type="is-danger" class="shadow">
                                                                        <h4 class="title is-4">{{ this.percentage_n_missing }} % Of Voters</h4>
                                                                    </b-message>
                                                                </div>
                                                            </div>
                                                            <div class="columns">
                                                                <div class="column is-6">
                                                                    <h6 class="title is-6">Participation Count</h6>
                                                                    <b-message type="is-success" class="shadow">
                                                                        <h4 class="title is-4">{{ this.num_votes_all }} Voters</h4>
                                                                    </b-message>
                                                                </div>
                                                                <div class="column is-6">
                                                                    <h6 class="title is-6">Abstention Count</h6>
                                                                    <b-message type="is-danger" class="shadow">
                                                                        <h4 class="title is-4">{{ this.num_votes_missing }} Voters</h4>
                                                                    </b-message>
                                                                </div>
                                                            </div>
                                                            <div class="columns">
                                                                <div class="column is-12">
                                                                    <h6 class="title is-6">Total Number of Poll Book Registrations: {{this.num_total_votes}}</h6>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </b-tab-item>
                            </b-tabs>
                        </div>
                    </div>
                </template>

            </div>
        </div>
    </div>
</template>
<script>
import {timestampToDate} from '../helpers.js'
import { Line } from 'vue-chartjs'
import PieChart from './Charts/PieChart.js'
import BarChart from './Charts/BarChart.js'

export default{
    components: {
        PieChart,
        BarChart
    },
    data(){
        return{
            title: "Election",
            electionId: this.$route.params.electionId,
            election: {},
            vote:{},
            canUpdate: false,
            alreadyVote: false,
            votingOptions: [],
            isLoading: true,
            currentTimestamp: Math.floor(new Date().getTime() / 1000),
            activeTab: 0,
            datacollectionPie: null,
            datacollectionBar: null,
            options: null,
            countLabels: [],
            numberVotes: [],
            colors:[],
            my_voting_option:{},
            num_votes_all: 0,
            num_votes_missing: 0,
            percentage_n_vote: 0,
            percentage_n_missing: 0,
            switchGraph: 0,
            asAdmin: false
        }
    },
    methods: {
        getElection(){
            axios.get('api/elections/'+ this.electionId)
            .then(response => {
                this.election = response.data
                console.log(this.election)

                if(this.election.can_change_vote){
                    this.canUpdate = true
                }else{
                    this.canUpdate = false
                }

                axios.get('api/elections/'+ this.electionId +'/voting_options')
                .then(response => {
                    this.votingOptions = response.data

                    let nullOption = this.votingOptions.findIndex(v => v.name == "NULL")
                    this.votingOptions.splice(nullOption,1)

                    let blankOption = this.votingOptions.findIndex(v => v.name == "BLANK")
                    this.votingOptions.splice(blankOption,1)

                    this.votingOptions.sort(function(a, b){
                        if(a.id < b.id) { return -1; }
                        if(a.id > b.id) { return 1; }
                        return 0;
                    })

                    axios.get('api/elections/'+this.electionId+'/number_of_votes')
                    .then(response => {
                        let votingOptionsAux = response.data

                        votingOptionsAux.sort((a,b) => {
                            if(a.name < b.name) { return -1; }
                            if(a.name > b.name) { return 1; }
                            return 0;
                        })

                        votingOptionsAux.forEach(voting_option => {
                            this.countLabels.push(voting_option.name.toUpperCase())
                            this.numberVotes.push(voting_option.num_votes)
                            this.num_votes_all += voting_option.num_votes
                            this.colors.push("#"+Math.floor(Math.random()*16777215).toString(16))
                        })

                        this.countLabels.forEach((element,index) => {
                            if(element == "NULL" || element == "BLANK"){
                                this.countLabels.splice(index,1)[0]
                                let numVotes = this.numberVotes.splice(index,1)[0]

                                this.countLabels.push(element)
                                this.numberVotes.push(numVotes)
                            }
                        })

                        axios.get('api/elections/'+this.electionId+'/poll_book/count')
                        .then(response => {
                            this.num_total_votes = response.data.count
                            this.num_votes_missing = this.num_total_votes - this.num_votes_all

                            this.percentage_n_vote = (this.num_votes_all * 100) / this.num_total_votes
                            this.percentage_n_missing = (this.num_votes_missing * 100) / this.num_total_votes

                            if(this.asAdmin){
                                this.isLoading = false
                                return
                            }

                            axios.get('api/votes/'+this.$parent.user.voter_id+'/election/'+this.election.election_id)
                            .then(response => {
                                this.vote = response.data

                                if(this.vote == null){
                                    this.alreadyVote = false
                                    this.isLoading = false
                                }else{
                                    this.alreadyVote = true
                                }

                                this.isLoading = false

                                if(this.vote != null){

                                    axios.get('api/voting_options/'+this.vote.voting_option_id)
                                    .then(response => {
                                        this.my_voting_option = response.data

                                        this.alreadyVote = true
                                        this.isLoading = false
                                    })
                                    .catch(error => {
                                        console.log(error)
                                        if(error.response.status == 401){
                                            this.$store.commit("logout")
                                            this.$router.push("/login")
                                        }
                                    })

                                }
                            })
                            .catch(error => {
                                console.log(error)
                                if(error.response.status == 401){
                                    this.$store.commit("logout")
                                    this.$router.push("/login")
                                }
                            })
                        })
                        .catch(error => {
                            console.log(error)
                            if(error.response.status == 401){
                                this.$store.commit("logout")
                                this.$router.push("/login")
                            }
                        })
                    })
                    .catch(error => {
                        console.log(error)
                        if(error.response.status == 401){
                            this.$store.commit("logout")
                            this.$router.push("/login")
                        }
                    })
                })
                .catch(error => {
                    console.log(error)
                    if(error.response.status == 401){
                        this.$store.commit("logout")
                        this.$router.push("/login")
                    }
                })
            })
            .catch(error => {
                console.log(error)
                if(error.response.status == 401){
                    this.$store.commit("logout")
                    this.$router.push("/login")
                }
            })
        },
        toDate(timestamp){
            return timestampToDate(timestamp)
        },
        fillData () {
            this.datacollectionPie = {
                labels: this.countLabels,
                datasets: [
                    {
                        label: 'Votes',
                        backgroundColor: this.colors,
                        data: this.numberVotes
                    }
                ]
            },
            this.datacollectionBar = {
                labels: this.countLabels,
                datasets: [
                    {
                        label: 'Votes',
                        backgroundColor: '#de4937',
                        data: this.numberVotes
                    }
                ]
            },
            this.options = {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        },
                        gridLines: {
                            display: true
                        }
                    }],
                    xAxes: [{
                        ticks: {
                            beginAtZero: true
                        },
                        gridLines: {
                            display: false
                        }
                    }]
                },
                legend: {
                    display: false
                },
                responsive: true,
            }
        },
        toggleElectionStatus(){
            if(this.election.status){
                this.$buefy.dialog.confirm({
                    title: 'Disable Election',
                    message: 'Are you sure you want to disable this election? Disabled elections won\'t take place.',
                    confirmText: 'Disable',
                    type: 'is-danger',
                    hasIcon: true,
                    onConfirm: () => {
                        this.isLoadingToggle = true
                        axios.put('/api/elections/'+ this.election.election_id, {
                            "status": false
                        })
                        .then(response => {
                            this.election.status = false
                            this.$buefy.toast.open({
                                duration: 5000,
                                message: 'Election disabled',
                                type: 'is-success'
                            })
                        })
                        .catch(error => {
                            if(error.response.status == 400){
                                this.getElection()
                                this.fillData()

                                this.$buefy.toast.open({
                                    duration: 5000,
                                    message: 'Election already started. No updates allowed.',
                                    type: 'is-warning'
                                })
                            }
                            console.log(error)
                        })
                        .then(() => {
                            this.isLoadingToggle = false
                        })
                    }

                })
            }else{
                this.isLoadingToggle = true
                axios.put('/api/elections/'+ this.election.election_id, {
                    "status": true
                })
                .then(response => {
                    this.election.status = true
                    this.$buefy.toast.open({
                        duration: 5000,
                        message: 'Election enabled',
                        type: 'is-success'
                    })
                })
                .catch(error => {
                    if(error.response.status == 400){
                        this.getElection()
                        this.fillData()

                        this.$buefy.toast.open({
                            duration: 5000,
                            message: 'Election already started. No updates allowed.',
                            type: 'is-warning'
                        })
                    }
                    console.log(error)
                })
                .then(() => {
                    this.isLoadingToggle = false
                })
            }
        }
    },
    created() {
        if(this.$router.currentRoute.name == 'electionAdmin'){
            this.asAdmin = true
            this.title = "Election Administration"
            this.$emit('back','/myelections')
        }else{
            this.$emit('back','/elections')
        }
        this.$emit('title',this.title)
    },
    mounted(){
        this.getElection()

        this.fillData()
    }
}
</script>
