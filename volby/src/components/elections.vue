<template>
    <div>
        <h3 class="title is-3">Current elections</h3>
        <h3 class="title is-3">Past elections</h3>
        <div class="card box">
            <div class="card-content">
                <template v-if="isLoading">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            <b-icon pack="fas" icon="sync-alt" size="is-large" custom-class="fa-spin">></b-icon>
                        </div>
                    </div>
                </template>
                <template v-else-if="pastElections.length == 0">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            You were not enrolled in an election yet.
                        </div>
                    </div>
                </template>
                <template v-else>
                    <b-table :data="pastElections">
                        <template slot-scope="props">
                            <b-table-column field="name" label="Name">
                                {{ props.row.name }}
                            </b-table-column>
                            <b-table-column field="admin_name" label="Created By">
                                {{ props.row.admin_name }}
                            </b-table-column>
                            <b-table-column field="start_timestamp" label="Start Time">
                                {{ toDate(props.row.start_timestamp) }}
                            </b-table-column>
                            <b-table-column field="end_timestamp" label="End Time">
                                {{ toDate(props.row.start_timestamp) }}
                            </b-table-column>
                            <b-table-column field="voted" label="Participation" centered>
                                <span v-if="showParticipation[props.row.id]" >
                                    <b-tag v-if="props.row.voted" type="is-success" rounded>Voted</b-tag>
                                    <b-tag v-else type="is-danger" rounded>Didn't Vote</b-tag>
                                </span>
                                <b-button rounded size="is-small" @click="toggleParticipation(props.row.id)" :icon-left="showParticipation[props.row.id] ? 'eye-off-outline' : 'eye-outline'"></b-button>
                            </b-table-column>
                            <b-table-column label="Actions">
                                <b-button rounded icon-left="plus" type="is-info" size="is-small">Info</b-button>
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
            title: "Elections",
            pastElections: [], //nome | admin | *abstinencia/participação* | start datetime | end datetime | voted/didnt vote | +info
            currentElections: [],
            isLoading: true,
            showParticipation: {}
        }
    },
    methods:{
        getPastElections(){
            axios.get('api/elections/past')
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
            axios.get('api/elections/current')
            .then(response => {
                this.getPastElections()
                this.currentElections = response.data
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
        }
    },
    created() {
        this.$emit('title',this.title)
        this.getCurrentElections()
    }
}
</script>
