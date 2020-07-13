<template>
    <div>
        <div class="columns">
            <div class="column">
            <div class="card box shadow has-margin-bottom-40">
            <div class="card-content has-padding-bottom-0">
                <template v-if="isLoading">
                    <div class="columns is-centered">
                        <div class="column is-12 has-text-centered">
                            <b-icon pack="fas" icon="sync-alt" size="is-large" custom-class="fa-spin"></b-icon>
                        </div>
                    </div>
                </template>
                <template v-else>
                    <validation-observer ref="observer">
                        <b-tabs v-model="activeTab" expanded>
                            <b-tab-item label="Informations">
                                <div class="columns">
                                    <div class="column">
                                        <validation-provider vid="name" rules="required" name="Name" v-slot="validationContext">
                                            <b-field :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <template slot="label">Name <span class="has-text-danger">*</span></template>
                                                <b-input v-model="election.name"></b-input>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <b-field label="Description">
                                            <b-input v-model="election.description" maxlength="1000" type="textarea"></b-input>
                                        </b-field>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <validation-provider vid="startDate" rules="required" name="Start Date" v-slot="validationContext">
                                            <b-field expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <template slot="label">Start Date <span class="has-text-danger">*</span></template>
                                                <b-datetimepicker rounded v-model="election.startDate" placeholder="Click to select..." icon="calendar-today" :datepicker="{ showWeekNumber }" :timepicker="{ enableSeconds, hourFormat: format }" :min-datetime="dateNow" :max-datetime="election.endDate" horizontal-time-picker>
                                                </b-datetimepicker>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                    <div class="column">
                                        <validation-provider vid="endDate" rules="required" name="End Date" v-slot="validationContext">
                                            <b-field expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <template slot="label">End Date <span class="has-text-danger">*</span></template>
                                                <b-datetimepicker rounded v-model="election.endDate" placeholder="Click to select..." icon="calendar-today" :datepicker="{ showWeekNumber }" :timepicker="{ enableSeconds, hourFormat: format }" :min-datetime="election.startDate" horizontal-time-picker>
                                                </b-datetimepicker>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                </div>
                                <div class="columns is-vcentered">
                                    <div class="column">
                                        <validation-provider vid="resultsExposure" rules="required" name="Results Exposure" v-slot="validationContext">
                                            <b-field label="Results Exposure" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-select v-model="election.results_permission" expanded>
                                                    <option value="PRIVATE">Private</option>
                                                    <option value="VOTERS_ONLY">Voters Only</option>
                                                    <option value="PUBLIC">Public</option>
                                                </b-select>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                    <div class="column">
                                        {{election.results_permission == 'PRIVATE' ? 'Only the administrator can view the results.' : (election.results_permission == 'VOTERS_ONLY' ? 'Only the administrator and the voters can view the results.' : 'Everyone can view the results.' )}}
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <validation-provider vid="mutableVotes" rules="required" name="Mutable Votes" v-slot="validationContext">
                                            <b-field label="Mutable Votes" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-switch v-model="election.can_change_vote">
                                                    {{election.can_change_vote ? 'Voters can change their vote multiple times after their initial choice' : "Voters can't change their vote after their initial choice"}}
                                                </b-switch>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                    <div class="column">
                                        <validation-provider vid="realtimeResults" rules="required" name="Realtime Results Exposure" v-slot="validationContext">
                                            <b-field label="Realtime Results Exposure" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-switch v-model="election.can_show_realtime">
                                                    {{election.can_show_realtime ? 'Results can be viewed in real time' : "Results can't be viewed in real time"}}
                                                </b-switch>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                </div>
                                <hr />
                                <b-field class="is-pulled-right">
                                    <b-button rounded @click="nextTab()" icon-right="arrow-right">Next</b-button>
                                </b-field>
                            </b-tab-item>
                        <b-tab-item label="Ballot">
                            <div class="has-margin-bottom-20">
                                <b-tag type="is-info">NOTE</b-tag> <b>Blank</b> and <b>Null</b> votes are default options.</div>
                                <div class="card box">
                                    <div class="card-content">
                                        <b-table :data="currentVotingOptions"
                                            :paginated="isPaginatedVotingOptions"
                                            :per-page="perPageVotingOptions"
                                            :current-page.sync="currentPageVotingOptions"
                                            :pagination-simple="isPaginationSimpleVotingOptions"
                                            :pagination-position="paginationPositionVotingOptions"
                                            default-sort="voter_id"
                                            :default-sort-direction="'asc'"
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
                                                <b-table-column field="description" label="Description" sortable searchable>
                                                    <template slot="searchable" slot-scope="props">
                                                        <b-input v-model="props.filters[props.column.field]"
                                                        placeholder="Search..."
                                                        icon="magnify"
                                                        size="is-small" />
                                                    </template>
                                                    {{ props.row.description }}
                                                </b-table-column>
                                                <b-table-column v-if="currentVotingOptions.length > 1" label="Actions">
                                                    <b-button @click="confirmDeleteVotingOption(props.row.voting_option_id, props.row.name)" rounded type="is-danger" icon-right="delete" size="is-small"></b-button>
                                                </b-table-column>
                                            </template>
                                        </b-table>
                                    </div>
                                </div>
                                <div class="card box" v-for="(votingOption, index) in newVotingOptions" :key="index">
                                    <div class="card-content">
                                        <div class="columns">
                                            <div class="column is-one-third">
                                                <validation-provider :vid="'optionName_' + index" :rules="{
                                                    required: true,
                                                    uniqueName: [...newVotingOptions,...currentVotingOptions],
                                                    nullBlankCheck: newVotingOptions
                                                    }" :name="(index + 1) + '. Option Name'" v-slot="validationContext">
                                                    <b-field expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                        <template slot="label">{{(index + 1) + '. Option Name'}} <span class="has-text-danger">*</span></template>
                                                        <b-input v-model="votingOption.name"></b-input>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <div class="column">
                                                <validation-provider :vid="'optionDescription_' + index" rules="" :name="(index + 1) + '. Option Description'" v-slot="validationContext">
                                                    <b-field :label="(index + 1) + '. Option Description'" expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                        <b-input v-model="votingOption.description"></b-input>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <div class="column is-narrow" style="margin-top: auto;">
                                                <b-button rounded @click="removeVotingOption(index)" type="is-danger" icon-right="delete" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <b-button rounded @click="addVotingOption" class="is-pulled-right" icon-right="plus" type="is-info"></b-button>
                                    </div>
                                </div>
                                <hr />
                                <b-field class="is-pulled-left">
                                    <b-button rounded @click="prevTab()" icon-left="arrow-left">Previous</b-button>
                                </b-field>
                                <b-field class="is-pulled-right">
                                    <b-button rounded @click="nextTab()" icon-right="arrow-right">Next</b-button>
                                </b-field>
                            </b-tab-item>
                            <b-tab-item label="Poll Book">
                                <div class="card box">
                                    <div class="card-content">
                                        <b-table :data="currentPollBook"
                                            :paginated="isPaginatedPollBook"
                                            :per-page="perPagePollBook"
                                            :current-page.sync="currentPagePollBook"
                                            :pagination-simple="isPaginationSimplePollBook"
                                            :pagination-position="paginationPositionPollBook"
                                            default-sort="voter_id"
                                            :default-sort-direction="'asc'"
                                            aria-next-label="Next page"
                                            aria-previous-label="Previous page"
                                            aria-page-label="Page"
                                            aria-current-label="Current page">

                                            <template slot-scope="props">
                                                <b-table-column field="voter_id" label="Voter ID" sortable searchable>
                                                    <template slot="searchable" slot-scope="props">
                                                        <b-input v-model="props.filters[props.column.field]"
                                                        placeholder="Search..."
                                                        icon="magnify"
                                                        size="is-small" />
                                                    </template>
                                                    {{ props.row.voter_id }}
                                                </b-table-column>
                                                <b-table-column field="name" label="Name" sortable searchable>
                                                    <template slot="searchable" slot-scope="props">
                                                        <b-input v-model="props.filters[props.column.field]"
                                                        placeholder="Search..."
                                                        icon="magnify"
                                                        size="is-small" />
                                                    </template>
                                                    {{ props.row.name }}
                                                </b-table-column>
                                                <b-table-column v-if="currentPollBook.length > 1" label="Actions">
                                                    <b-button @click="confirmDeletePollRegistration(props.row.voter_id)" rounded type="is-danger" icon-right="delete" size="is-small"></b-button>
                                                </b-table-column>
                                            </template>
                                        </b-table>
                                    </div>
                                </div>
                                <div class="card box" v-for="(voter, index) in newPollBook" :key="index">
                                    <div class="card-content">
                                        <div class="columns">
                                            <div class="column is-one-third">
                                                <validation-provider :vid="'voterId_' + index" :rules="{
                                                    required: true,
                                                    email: true,
                                                    unique: [...newPollBook,...currentPollBook]
                                                    }" :name="(index + 1) + '. Voter Email'" v-slot="validationContext">
                                                    <b-field expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                        <template slot="label">{{(index + 1) + '. Voter Email'}} <span class="has-text-danger">*</span></template>
                                                        <b-input v-model="voter.id"></b-input>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <div class="column">
                                                <validation-provider :vid="'voterName_' + index" rules="required" :name="(index + 1) + '. Voter Name '" v-slot="validationContext">
                                                    <b-field expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                        <template slot="label">{{(index + 1) + '. Voter Name'}} <span class="has-text-danger">*</span></template>
                                                        <b-input v-model="voter.name"></b-input>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <div class="column is-narrow" style="margin-top: auto;" rounded>
                                                <b-button rounded @click="removeVoter(index)" type="is-danger" icon-right="delete" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <b-button rounded @click="addVoter" class="is-pulled-right" icon-right="plus" type="is-info"></b-button>
                                    </div>
                                </div>
                                <hr />
                                <b-field class="is-pulled-left">
                                    <b-button rounded @click="prevTab()" icon-left="arrow-left">Previous</b-button>
                                </b-field>
                                <b-field class="is-pulled-right">
                                    <b-button type="is-primary" rounded :loading="isLoadingSubmit" @click.prevent="submit">Update</b-button>
                                </b-field>
                            </b-tab-item>
                        </b-tabs>
                    </validation-observer>
                </template>
            </div>
        </div>
            </div>
        </div>
    </div>
</template>
<script>

import { extend } from 'vee-validate';
import { unique, uniqueName, nullBlankCheck } from 'vee-validate/dist/rules';
import { timestampToDateObject } from '../helpers.js'

extend('unique', {
    validate(value, obj) {
        if (obj.filter(o => o.id=== value || o.voter_id=== value).length > 1) {
            return  `${value} is already taken.`
        }else{
            return true;
        }
    }
});

extend('uniqueName', {
    validate(value, obj) {
        if (obj.filter(o => o.name === value).length > 1) {
            return  `${value} is already in the ballot.`
        }else{
            return true;
        }
    }
});

extend('nullBlankCheck', {
    validate(value, obj) {
        if (value.toUpperCase() == "NULL" || value.toUpperCase() == "BLANK" ) {
            return  `${value.toUpperCase()} is a default options in the election.`
        }else{
            return true;
        }
    }
});

export default{
    data(){
        return{
            title: "Update Election",
            activeTab: 0,
            dateNow: new Date(),
            showWeekNumber: false,
            format: '24',
            enableSeconds: false,
            newVotingOptions: [],
            newPollBook: [],
            isLoadingSubmit: false,
            isLoadingVotingOptions: true,
            isLoadingPollBook: true,
            electionId: this.$route.params.electionId,
            isLoading: true,
            election: {},
            currentVotingOptions: [],
            currentPollBook: [],
            currentPageVotingOptions: 1,
            perPageVotingOptions: 20,
            isPaginatedVotingOptions: true,
            isPaginationSimpleVotingOptions: false,
            paginationPositionVotingOptions: 'bottom',
            currentPagePollBook: 1,
            perPagePollBook: 20,
            isPaginatedPollBook: true,
            isPaginationSimplePollBook: false,
            paginationPositionPollBook: 'bottom',
            currentTimestamp: Math.floor(new Date().getTime() / 1000)
        }
    },
    methods: {
        prevTab(){
            this.activeTab--
        },
        nextTab(){
            this.activeTab++
        },
        getValidationState({ dirty, validated, valid = null }) {
            return dirty || validated ? (valid ? "" : "is-danger") : "";
        },
        addVotingOption(){
            this.newVotingOptions.push({
                name: "",
                description: ""
            })
        },
        removeVotingOption(index){
            this.newVotingOptions.splice(index,1)
        },
        addVoter(){
            this.newPollBook.push({
                id: "",
                name: ""
            })
        },
        removeVoter(index){
            this.newPollBook.splice(index,1)
        },
        toTimestamp(date){
            var timestamp = Date.parse(date);
            return timestamp/1000;
        },
        submit(){
            this.$refs.observer.validate()
            .then(result => {
                this.isLoadingSubmit = true
                const loadingSnackbar = this.$buefy.snackbar.open({
                    message: 'Writing to blockchain. This might take some time...',
                    position: 'is-bottom-left',
                    type: 'is-warning',
                    indefinite: true
                })

                if(!result){
                    if(this.$refs.observer.errors.name.length > 0 || this.$refs.observer.errors.startDate.length > 0 || this.$refs.observer.errors.endDate.length > 0
                    || this.$refs.observer.errors.resultsExposure.length > 0 || this.$refs.observer.errors.realtimeResults.length > 0 || this.$refs.observer.errors.mutableVotes.length > 0){
                        this.$buefy.snackbar.open({
                            message: 'Input errors on the <b>Informations</b> tab.',
                            type: 'is-warning',
                            position: 'is-bottom-left',
                            actionText: 'Go There',
                            indefinite: true,
                            queue: false,
                            onAction: () => {
                                this.activeTab = 0
                            }
                        })
                    }

                    let ballotFields = Object.keys(this.$refs.observer.errors).filter(key => {
                        return key.startsWith("optionName");
                    })

                    for(let field in ballotFields){
                        if(this.$refs.observer.errors[ballotFields[field]].length > 0){
                            this.$buefy.snackbar.open({
                                message: 'Input errors on the <b>Ballot</b> tab.',
                                type: 'is-warning',
                                position: 'is-bottom-left',
                                actionText: 'Go There',
                                indefinite: true,
                                queue: false,
                                onAction: () => {
                                    this.activeTab = 1
                                }
                            })
                            break
                        }
                    }

                    loadingSnackbar.close()
                    this.isLoadingSubmit = false
                    return
                }

                axios.put('api/elections/' + this.electionId, {
                "name": this.election.name,
                "description": this.election.description,
                "start_timestamp": this.toTimestamp(this.election.startDate),
                "end_timestamp": this.toTimestamp(this.election.endDate),
                "results_permission": this.election.results_permission,
                "can_change_vote": this.election.can_change_vote,
                "can_show_realtime": this.election.can_show_realtime,
                "voting_options": this.newVotingOptions,
                "poll_book": this.newPollBook
                })
                .then(response => {
                    this.$buefy.toast.open({
                        duration: 3000,
                        message: 'Election updated successfully!',
                        type: 'is-success'
                    })

                    this.$router.push("/myelections").catch(e => {})
                })
                .catch(error => {
                    if(error.response.status == 400) {
                        this.$router.push("/myelections")
                        this.$buefy.toast.open({
                            duration: 3000,
                            message: "This election can't be updated anymore.",
                            type: 'is-warning'
                        })
                    }
                    console.log(error)
                })
                .then(() => {
                    loadingSnackbar.close()
                    this.isLoadingSubmit = false
                })
            })
        },
        getElection(){
            axios.get(`/api/elections/${this.electionId}/?asAdmin=1`)
            .then(response => {
                this.election = response.data

                if(this.election.start_timestamp < this.currentTimestamp){
                    this.$router.push("/myelections")
                    this.$buefy.toast.open({
                        duration: 3000,
                        message: "This election can't be updated anymore.",
                        type: 'is-warning'
                    })
                    return
                }

                this.election.startDate = timestampToDateObject(this.election.start_timestamp)
                this.election.endDate = timestampToDateObject(this.election.start_timestamp)

                axios.get(`/api/elections/${this.electionId}/voting_options`)
                .then(response => {
                    this.currentVotingOptions = response.data

                    let nullOption = this.currentVotingOptions.findIndex(v => v.name == "NULL")
                    this.currentVotingOptions.splice(nullOption,1)

                    let blankOption = this.currentVotingOptions.findIndex(v => v.name == "BLANK")
                    this.currentVotingOptions.splice(blankOption,1)

                    axios.get(`/api/elections/${this.electionId}/poll_book`)
                    .then(response => {
                        this.currentPollBook = response.data
                    })
                    .catch(error => {
                        console.log(error)
                    })
                    .then(() => {
                        this.isLoadingPollBook = false
                    })
                })
                .catch(error => {
                    console.log(error)
                })
                .then(() => {
                    this.isLoadingVotingOptions = false
                })
            })
            .catch(error => {
                console.log(error)
                if(error.response.status == 404){
                    this.$router.push("*")
                }
            })
            .then(() => {
                this.isLoading = false
            })
        },
        confirmDeletePollRegistration(voterId){
            this.$buefy.dialog.confirm({
                title: 'Remove Poll Registration',
                message: 'Are you sure you want to remove "' + voterId + '" from the poll book?',
                confirmText: 'Remove',
                type: 'is-danger',
                hasIcon: true,
                onConfirm: () => {
                    axios.patch('/api/elections/' + this.electionId + '/poll_registration/' + voterId + '/status')
                    .then(response => {
                        for(let i = 0; i < this.currentPollBook.length; i++){
                            if(this.currentPollBook[i].voter_id == voterId){
                                this.currentPollBook.splice(i,1)
                                break
                            }
                        }
                        this.$buefy.toast.open({
                            duration: 5000,
                            message: 'Poll registration removed',
                            type: 'is-success'
                        })
                    })
                    .catch(error => {
                        if(error.response.status == 400) {
                            this.$router.push("/myelections")
                            this.$buefy.toast.open({
                                duration: 3000,
                                message: "This election can't be updated anymore.",
                                type: 'is-warning'
                            })
                        }
                        console.log(error)
                    })
                }

            })
        },
        confirmDeleteVotingOption(votingOptionId, name){
            this.$buefy.dialog.confirm({
                title: 'Remove Poll Registration',
                message: 'Are you sure you want to remove "' + name + '" from the ballot?',
                confirmText: 'Remove',
                type: 'is-danger',
                hasIcon: true,
                onConfirm: () => {
                    axios.patch('/api/voting_options/' + votingOptionId + '/status')
                    .then(response => {
                        for(let i = 0; i < this.currentVotingOptions.length; i++){
                            if(this.currentVotingOptions[i].voting_option_id == votingOptionId){
                                this.currentVotingOptions.splice(i,1)
                                break
                            }
                        }
                        this.$buefy.toast.open({
                            duration: 5000,
                            message: 'Voting option removed',
                            type: 'is-success'
                        })
                    })
                    .catch(error => {
                        if(error.response.status == 400) {
                            this.$router.push("/myelections")
                            this.$buefy.toast.open({
                                duration: 3000,
                                message: "This election can't be updated anymore.",
                                type: 'is-warning'
                            })
                        }
                        console.log(error)
                    })
                }

            })
        }
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back',"/election/" + this.electionId + "/admin")
        this.getElection()
    }
}
</script>
