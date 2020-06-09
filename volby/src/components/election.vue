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
                            <b-tooltip v-if="!this.canUpdate && this.alreadyVote" type="is-dark" label="You already have submitted a vote. The option multible votes is disabled for this election">
                                <b-tag class="has-margin-top-5 has-margin-right-5">Can't Vote any more.</b-tag>
                            </b-tooltip>
                            <b-tooltip v-else-if="this.canUpdate" type="is-dark" label="Voters can change their vote multiple times after their initial choice">
                                <b-tag class="has-margin-top-5 has-margin-right-5">Mutable Votes</b-tag>
                            </b-tooltip>
                            <b-button v-if="this.canUpdate && this.alreadyVote" tag="router-link" :to="'/vote/' + vote.vote_id + '/update'" rounded type="is-info">Update Vote</b-button>
                            <b-button v-else-if="!this.alreadyVote" tag="router-link" :to="'/election/' + election.election_id + '/vote'" rounded type="is-info">Vote</b-button>
                        </div>
                        <div class="column is-6 has-text-right" v-else>
                            <b-tag type="is-info" rounded>Terminated</b-tag>
                        </div>
                    </div>
                    <div class="columns">
                        <div class="column is-12">
                            <b-tabs v-model="activeTab" expanded>
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
                                                    <strong>Live Results - Total Votes</strong>
                                                </div>
                                                <div class="title is-3" v-else>
                                                    <strong>Results - Total Votes</strong>
                                                </div>
                                                <div v-if="this.switchGraph" class="small">
                                                    <pie-chart :chart-data="datacollection1"></pie-chart>
                                                </div>
                                                <div v-else class="small">
                                                    <bar-chart :chart-data="datacollection1"></bar-chart>
                                                </div>
                                                <b-switch v-model="switchGraph"> Show BarChart </b-switch>
                                            </div>
                                            <br>
                                            <div class="column is-6">
                                                <div class="title is-3" v-if="election.end_timestamp > currentTimestamp">
                                                    <strong>Live Results - Number of Votes Submitted</strong>
                                                </div>
                                                <div class="title is-3" v-else>
                                                    <strong>Results - Percentage of Votes Submitted</strong>
                                                </div>
                                                <div>
                                                    <span class="title is-5"> Votes Submitted - {{ this.percentage_n_vote }} % </span>
                                                    <span class="title is-5"> Votes Missing - {{ this.percentage_n_missing }} % </span>
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
            user: {},
            vote:{},
            canUpdate: false,
            alreadyVote: false,
            votingOptions: [],
            isLoading: true,
            currentTimestamp: Math.floor(new Date().getTime() / 1000),
            activeTab: 0,
            datacollection1: null,
            countLabels: [],
            numberVotes: [],
            colors:[],
            pollBookAux: [],
            num_votes_all: 0,
            num_votes_missing: 0,
            percentage_n_vote: 0,
            percentage_n_missing: 0,
            switchGraph: 0,
            options: {
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
                        },
                        barPercentage: 0.4
                    }]
                },
                responsive: true
            },
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

                console.log(this.election)

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

                                console.log(numVotes)

                                this.countLabels.push(element)
                                this.numberVotes.push(numVotes)
                            }
                        })

                        axios.get('api/elections/'+this.electionId+'/poll_book')
                        .then(response => {
                            this.pollBookAux = response.data
                            this.num_total_votes = this.pollBookAux.length
                            this.num_votes_missing = this.num_total_votes - this.num_votes_all

                            this.percentage_n_vote = (this.num_votes_all * 100) / this.num_total_votes
                            this.percentage_n_missing = (this.num_votes_missing * 100) / this.num_total_votes

                            this.user =  this.$store.getters.user

                            axios.get('api/votes/'+this.user.voter_id+'/election/'+this.election.election_id)
                            .then(response => {
                                this.vote = response.data
                                console.log(this.vote)

                                if(this.vote == null){
                                    this.alreadyVote = false
                                }else{
                                    this.alreadyVote = true
                                }

                                this.isLoading = false
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
            this.datacollection1 = {
                labels: this.countLabels,
                datasets: [
                    {
                        label: 'Votes',
                        backgroundColor: this.colors,
                        data: this.numberVotes
                    }
                ]
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
<style>
.small {
    max-width: 500px;
    margin:  30px auto;
}
</style>
