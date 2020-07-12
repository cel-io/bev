<template>
    <div>
        <h3 class="title is-3">Future elections</h3>
        <div class="card box shadow">
            <div class="card-content">
                <template v-if="isLoading">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            <b-icon pack="fas" icon="sync-alt" size="is-large" custom-class="fa-spin"></b-icon>
                        </div>
                    </div>
                </template>
                <template v-else-if="futureElections.length == 0">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            No elections scheduled.
                        </div>
                    </div>
                </template>
                <template v-else>
                    <div class="card box" v-for="election in futureElections" :key="election.id">
                        <div class="card-content has-padding-top-0 has-padding-bottom-0">
                            <div class="columns is-vcentered">
                                <div class="column is-4">
                                    <router-link :to="'/election/' + election.election_id + '/admin'"><span class="is-size-5">{{election.name}}</span></router-link>
                                </div>
                                <div class="column is-4">
                                    <countdown :time="(election.start_timestamp - currentTimestamp ) * 1000">
                                        <template slot-scope="props"><span class="has-text-weight-bold">Starts In:</span> {{ props.days }} days, {{ props.hours }} hours, {{ props.minutes }} minutes, {{ props.seconds }} seconds.</template>
                                    </countdown>
                                </div>
                                <div class="column is-4 has-text-right">
                                    <b-button class="has-text-right" tag="router-link" :to="'/election/' + election.election_id + '/admin'" rounded type="is-info">Open</b-button>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </div>
        <h3 class="title is-3">Current elections</h3>
        <div class="card box shadow">
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
                                    <router-link :to="'/election/' + election.election_id + '/admin'"><span class="is-size-5">{{election.name}}</span></router-link>
                                </div>
                                <div class="column is-4">
                                    <countdown :time="(election.end_timestamp - currentTimestamp ) * 1000">
                                        <template slot-scope="props"><span class="has-text-weight-bold">Time Remaining:</span> {{ props.days }} days, {{ props.hours }} hours, {{ props.minutes }} minutes, {{ props.seconds }} seconds.</template>
                                    </countdown>
                                </div>
                                <div class="column is-4 has-text-right">
                                    <b-button class="has-text-right" tag="router-link" :to="'/election/' + election.election_id + '/admin'" rounded type="is-info">Open</b-button>
                                </div>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </div>
        <h3 class="title is-3">Past elections</h3>
        <div class="card box shadow">
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
                            No elections happened before.
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
                        <b-table-column field="name" label="Name" sortable searchable>
                            <template slot="searchable" slot-scope="props">
                                <b-input v-model="props.filters[props.column.field]"
                                placeholder="Search..."
                                icon="magnify"
                                size="is-small" />
                            </template>
                            {{ props.row.name }}
                        </b-table-column>
                        <b-table-column field="start_timestamp" label="Start Time" sortable>
                            {{ toDate(props.row.start_timestamp) }}
                        </b-table-column>
                        <b-table-column field="end_timestamp" label="End Time" sortable>
                            {{ toDate(props.row.start_timestamp) }}
                        </b-table-column>
                        <b-table-column label="Actions">
                            <b-button tag="router-link" :to="'/election/' + props.row.election_id + '/admin'" rounded icon-left="plus" type="is-info" size="is-small">Info</b-button>
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

export default {
    data(){
        return {
            title: "My Elections",
            futureElections: [],
            currentElections: [],
            pastElections: [],
            isLoading: true,
            currentPage: 1,
            perPage: 10,
            isPaginated: true,
            isPaginationSimple: false,
            paginationPosition: 'bottom',
            currentTimestamp: Math.floor(new Date().getTime() / 1000)
        }
    },
    methods: {
        getElections(){
            axios.get(`/api/voters/admins/${this.$parent.user.voter_id}/elections`)
            .then(response => {
                response.data.forEach(election => {
                    if(election.start_timestamp <= this.currentTimestamp && this.currentTimestamp <= election.end_timestamp){
                        this.currentElections.push(election)
                    }else if(election.end_timestamp < this.currentTimestamp){
                        this.pastElections.push(election)
                    }else if(election.start_timestamp > this.currentTimestamp){
                        this.futureElections.push(election)
                    }
                })
                this.isLoading = false
            })
            .catch(error => {
                console.log(error)
            })
        },
        toDate(timestamp){
            return timestampToDate(timestamp)
        }
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back',"")
        this.getElections()
    }
}
</script>
