<template>
    <div>
        <div class="card box">
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
                        <div class="column is-6 has-text-right" v-if="election.end_timestamp > currentTimestamp">
                            <b-tag class="has-margin-top-5 has-margin-right-5" type="is-danger">Live</b-tag>
                            <b-tooltip v-if="!this.canUpdate && this.alreadyVote" type="is-dark" label="You already have submitted a vote. The option multible votes is disabled for this election">
                                <b-tag class="has-margin-top-5 has-margin-right-5">Can't Vote any more.</b-tag>
                            </b-tooltip>
                            <b-tooltip v-else-if="this.canUpdate" type="is-dark" label="Voters can change their vote multiple times after their initial choice">
                                <b-tag class="has-margin-top-5 has-margin-right-5">Mutable Votes</b-tag>
                            </b-tooltip>
                            <b-button v-if="this.canUpdate && this.alreadyVote" tag="router-link" :to="'/vote/' + vote.vote_id + '/update'" rounded type="is-info">Update Vote</b-button>
                            <b-button v-else-if="!this.alreadyVote" tag="router-link" :to="'/election/' + election.election_id + '/vote'" rounded type="is-info">Vote</b-button>
                        </div>
                    </div>
                    <div class="columns">
                        <div class="column is-12">
                            <b-tabs v-model="activeTab" expanded>
                                <b-tab-item label="My Vote">
                                    <br>
                                    <div v-if="!this.alreadyVote" class="has-text-centered" >
                                        <span>No Votes made.</span>
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
                                        <div class="column" v-if="election.end_timestamp > currentTimestamp">
                                            <countdown :time="(election.end_timestamp - currentTimestamp ) * 1000">
                                                <template slot-scope="props"><span class="has-text-weight-bold">Time Remaining:</span> {{ props.days }} days, {{ props.hours }} hours, {{ props.minutes }} minutes, {{ props.seconds }} seconds.</template>
                                            </countdown>
                                        </div>
                                    </div>
                                    <div class="columns">
                                        <div class="column">
                                            <span class="has-text-weight-bold">Created By:</span> {{election.admin_name}}
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
                                    <div class=" has-text-centered" v-if="this.num_votes_all == 0">
                                        <span>No Votes found to Generate Chart.</span>
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
            switchGraph: 0
        }
    },
    methods: {
        getElection(){
            axios.get('api/elections/'+ this.electionId)
            .then(response => {
                this.election = response.data

                if(this.election.can_change_vote == 1){
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

                            axios.get('api/votes/'+this.$parent.user.voter_id+'/election/'+this.election.election_id)
                            .then(response => {
                                this.vote = response.data

                                if(this.vote == null){
                                    this.alreadyVote = false
                                }else{
                                    this.alreadyVote = true
                                }

                                this.isLoading = false

                                if(this.vote != null){

                                    axios.get('api/voting_options/'+this.vote.voting_option_id)
                                    .then(response => {
                                        this.my_voting_option = response.data

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
        getRandomInt () {
            return Math.floor(Math.random() * (50 - 5 + 1)) + 5
        },
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back','/elections')
    },
    mounted(){
        this.getElection()

        this.fillData()
    }
}
</script>
