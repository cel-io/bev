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
                            <b-tooltip type="is-dark" label="Voters can change their vote multiple times after their initial choice"><b-tag type="is-success" class="has-margin-top-5 has-margin-right-5" rounded>Mutable Votes</b-tag></b-tooltip>
                            <b-button tag="router-link" :to="'/election/' + election.election_id + '/vote'" rounded type="is-info">Vote</b-button>
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
                                    results
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

export default{
    data(){
        return{
            title: "Election",
            electionId: this.$route.params.electionId,
            election: {},
            votingOptions: [],
            isLoading: true,
            currentTimestamp: Math.floor(new Date().getTime() / 1000),
            activeTab: 0
        }
    },
    methods: {
        getElection(){
            axios.get('api/elections/'+ this.electionId)
            .then(response => {
                this.election = response.data

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
        },
        toDate(timestamp){
            return timestampToDate(timestamp)
        }
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back','/elections')
    },
    mounted(){
        this.getElection()
    }
}
</script>
