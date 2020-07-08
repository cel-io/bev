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
        <h3 class="title is-3">Past elections</h3>
        <div class="card box">
            <div class="card-content">
                <template v-if="isLoading">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            <b-icon pack="fas" icon="sync-alt" size="is-large" custom-class="fa-spin"></b-icon>
                        </div>
                    </div>
                </template>
                <template v-else-if="pastElections.length == 0">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            There were not any public elections yet.
                        </div>
                    </div>
                </template>
                <template v-else>
                    <b-table :data="pastElections"
                    :paginated="isPaginated"
                    :per-page="perPage"
                    :current-page.sync="currentPage"
                    :pagination-simple="isPaginationSimple"
                    :pagination-position="paginationPosition"
                    default-sort="start_timestamp"
                    :default-sort-direction="'desc'"
                    aria-next-label="Next page"
                    aria-previous-label="Previous page"
                    aria-page-label="Page"
                    aria-current-label="Current page">

                    <template slot-scope="props">
                        <b-table-column field="name" label="Name" sortable>
                            {{ props.row.name }}
                        </b-table-column>
                        <b-table-column field="admin_name" label="Created By" sortable>
                            {{ props.row.admin_name }}
                        </b-table-column>
                        <b-table-column field="start_timestamp" label="Start Time" sortable>
                            {{ toDate(props.row.start_timestamp) }}
                        </b-table-column>
                        <b-table-column field="end_timestamp" label="End Time" sortable>
                            {{ toDate(props.row.start_timestamp) }}
                        </b-table-column>
                        <b-table-column field="voted" label="Participation" centered sortable>
                            <span v-if="showParticipation[props.row.id]" >
                                <b-tag v-if="props.row.voted" type="is-success" rounded>Voted</b-tag>
                                <b-tag v-else type="is-danger" rounded>Didn't Vote</b-tag>
                            </span>
                            <b-button rounded size="is-small" @click="toggleParticipation(props.row.id)" :icon-left="showParticipation[props.row.id] ? 'eye-off-outline' : 'eye-outline'"></b-button>
                        </b-table-column>
                        <b-table-column label="Actions">
                            <b-button tag="router-link" :to="'/election/' + props.row.election_id" rounded icon-left="plus" type="is-info" size="is-small">Info</b-button>
                        </b-table-column>
                    </template>
                </b-table>
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
            pastElections: [],
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
        getPastElections(){
            axios.get('api/elections/public/past')
            .then(response => {
                this.pastElections = response.data

                this.pastElections.forEach(item => {
                    this.$set(this.showParticipation, item.id, false)
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
        },
        getCurrentElections(){
            axios.get('api/elections/public')
            .then(response => {
                this.getPastElections()
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
        },
        toDate(timestamp){
            return timestampToDate(timestamp)
        },
        toggleParticipation(id){
            this.$set(this.showParticipation, id, !this.showParticipation[id])
        },
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back',"")
        this.getCurrentElections()
    },
}
</script>
