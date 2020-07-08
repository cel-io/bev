<template>
    <div>
        <h3 class="title is-3">Current elections</h3>
        <div class="card box">
            <div class="card-content">
                <template v-if="isLoading">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            <b-icon pack="fas" icon="sync-alt" size="is-large" custom-class="fa-spin"></b-icon>
                        </div>
                    </div>
                </template>
                <template v-else-if="currentElections.length == 0">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            No elections happening now.
                        </div>
                    </div>
                </template>
                <template v-else>
                    <div class="card box" v-for="election in currentElections" :key="election.id">
                        <div class="card-content has-padding-top-0 has-padding-bottom-0">
                            <div class="columns is-vcentered">
                                <div class="column is-4">
                                    <router-link :to="'/election/' + election.election_id"><span class="is-size-5">{{election.name}}</span></router-link>
                                </div>
                                <div class="column is-4">
                                    <countdown :time="(election.end_timestamp - currentTimestamp ) * 1000">
                                        <template slot-scope="props"><span class="has-text-weight-bold">Time Remaining:</span> {{ props.days }} days, {{ props.hours }} hours, {{ props.minutes }} minutes, {{ props.seconds }} seconds.</template>
                                    </countdown>
                                </div>
                                <div class="column is-4 has-text-right">
                                    <b-button class="has-text-right" tag="router-link" :to="'/election/' + election.election_id" rounded type="is-info">Open</b-button>
                                </div>
                            </div>
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
            title: "Public Elections",
            currentElections: [],
            isLoading: true,
            showParticipation: {},
            currentPage: 1,
            perPage: 10,
            isPaginated: true,
            isPaginationSimple: false,
            paginationPosition: 'bottom',
            currentTimestamp: Math.floor(new Date().getTime() / 1000),
            canUpdate: false,
            alreadyVote: false
        }
    },
    methods:{
        getCurrentElections(){
            axios.get('api/elections/public')
            .then(response => {
                this.currentElections = response.data

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
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back',"")
        this.getCurrentElections()
    },
}
</script>
