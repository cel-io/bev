<template>
    <div>
        <div class="columns">
            <div class="column">
                <div class="card box shadow has-margin-bottom-40">
            <div class="card-content has-padding-bottom-0">
                <validation-observer ref="observer">
                    <b-tabs v-model="activeTab" expanded>
                        <b-tab-item label="Informations">
                            <div class="columns">
                                <div class="column">
                                    <validation-provider vid="name" rules="required" name="Name" v-slot="validationContext">
                                        <b-field :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <template slot="label">Name <span class="has-text-danger">*</span></template>
                                            <b-input v-model="name"></b-input>
                                        </b-field>
                                    </validation-provider>
                                </div>
                            </div>
                            <div class="columns">
                                <div class="column">
                                    <b-field label="Description">
                                        <b-input v-model="description" maxlength="1000" type="textarea"></b-input>
                                    </b-field>
                                </div>
                            </div>
                            <div class="columns">
                                <div class="column">
                                    <validation-provider vid="startDate" rules="required" name="Start Date" v-slot="validationContext">
                                        <b-field expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <template slot="label">Start Date <span class="has-text-danger">*</span></template>
                                            <b-datetimepicker rounded v-model="startDate" placeholder="Click to select..." icon="calendar-today" :datepicker="{ showWeekNumber }" :timepicker="{ enableSeconds, hourFormat: format }" :min-datetime="dateNow" :max-datetime="endDate" horizontal-time-picker>
                                            </b-datetimepicker>
                                        </b-field>
                                    </validation-provider>
                                </div>
                                <div class="column">
                                    <validation-provider vid="endDate" rules="required" name="End Date" v-slot="validationContext">
                                        <b-field expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <template slot="label">End Date <span class="has-text-danger">*</span></template>
                                            <b-datetimepicker rounded v-model="endDate" placeholder="Click to select..." icon="calendar-today" :datepicker="{ showWeekNumber }" :timepicker="{ enableSeconds, hourFormat: format }" :min-datetime="startDate ? startDate : dateNow" horizontal-time-picker>
                                            </b-datetimepicker>
                                        </b-field>
                                    </validation-provider>
                                </div>
                            </div>
                            <div class="columns is-vcentered">
                                <div class="column">
                                    <validation-provider vid="resultsExposure" rules="required" name="Results Exposure" v-slot="validationContext">
                                        <b-field label="Results Exposure" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <b-select v-model="resultsPermission" expanded>
                                                <option value="PRIVATE">Private</option>
                                                <option value="VOTERS_ONLY">Voters Only</option>
                                                <option value="PUBLIC">Public</option>
                                            </b-select>
                                        </b-field>
                                    </validation-provider>
                                </div>
                                <div class="column">
                                    {{resultsPermission == 'PRIVATE' ? 'Only the administrator can view the results.' : (resultsPermission == 'VOTERS_ONLY' ? 'Only the administrator and the voters can view the results.' : 'Everyone can view the results.' )}}
                                </div>
                            </div>
                            <div class="columns">
                                <div class="column">
                                    <validation-provider vid="mutableVotes" rules="required" name="Mutable Votes" v-slot="validationContext">
                                        <b-field label="Mutable Votes" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <b-switch v-model="canChangeVote">
                                                {{canChangeVote ? 'Voters can change their vote multiple times after their initial choice' : "Voters can't change their vote after their initial choice"}}
                                            </b-switch>
                                        </b-field>
                                    </validation-provider>
                                </div>
                                <div class="column">
                                    <validation-provider vid="realtimeResults" rules="required" name="Realtime Results Exposure" v-slot="validationContext">
                                        <b-field label="Realtime Results Exposure" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <b-switch v-model="canShowRealtime">
                                                {{canShowRealtime ? 'Results can be viewed in real time' : "Results can't be viewed in real time"}}
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
                            <div class="card box" v-for="(votingOption, index) in votingOptions" :key="index">
                                <div class="card-content">
                                    <div class="columns">
                                        <div class="column is-one-third">
                                            <validation-provider :vid="'optionName_' + index" :rules="{
                                                required: true,
                                                nullBlankCheck: votingOptions
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
                                        <div v-if="votingOptions.length > 1" class="column is-narrow" style="margin-top: auto;">
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
                            <div class="card box" v-for="(voter, index) in pollBook" :key="index">
                                <div class="card-content">
                                    <div class="columns">
                                        <div class="column is-one-third">
                                            <validation-provider :vid="'voterId_' + index" :rules="{
                                                required: true,
                                                email: true,
                                                unique: pollBook
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
                                        <div v-if="pollBook.length > 1" class="column is-narrow" style="margin-top: auto;" rounded>
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
                                <b-button type="is-primary" rounded :loading="isLoading" @click.prevent="submit">Submit</b-button>
                            </b-field>
                        </b-tab-item>
                    </b-tabs>
                </validation-observer>
            </div>
        </div>
            </div>
        </div>
    </div>
</template>
<script>

import { extend } from 'vee-validate';
import { unique, nullBlankCheck } from 'vee-validate/dist/rules';

extend('unique', {
    validate(value, obj) {
        if (obj.filter(o => o.id === value).length > 1) {
            return  `${value} is already taken.`
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
            title: "New Election",
            activeTab: 0,
            name: "My Election",
            description: "",
            dateNow: new Date(),
            startDate: null,
            endDate: null,
            showWeekNumber: false,
            format: '24',
            enableSeconds: false,
            resultsPermission: "VOTERS_ONLY",
            canChangeVote: true,
            canShowRealtime: true,
            votingOptions: [
                {
                    name: "Option A",
                    description: ""
                },
                {
                    name: "Option B",
                    description: ""
                }
            ],
            pollBook: [
                {
                    id: "",
                    name: ""
                }
            ],
            isLoading: false
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
            this.votingOptions.push({
                name: "",
                description: ""
            })
        },
        removeVotingOption(index){
            this.votingOptions.splice(index,1)
        },
        addVoter(){
            this.pollBook.push({
                id: "",
                name: ""
            })
        },
        removeVoter(index){
            this.pollBook.splice(index,1)
        },
        toTimestamp(date){
            var timestamp = Date.parse(date);
            return timestamp/1000;
        },
        submit(){
            this.$refs.observer.validate()
            .then(result => {
                this.isLoading = true
                const loadingSnackbar = this.$buefy.toast.open({
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
                    this.isLoading = false
                    return
                }

                axios.post('api/elections', {
                "name": this.name,
                "description": this.description,
                "start_timestamp": this.toTimestamp(this.startDate),
                "end_timestamp": this.toTimestamp(this.endDate),
                "results_permission": this.resultsPermission,
                "can_change_vote": this.canChangeVote,
                "can_show_realtime": this.canShowRealtime,
                "voting_options": this.votingOptions,
                "poll_book": this.pollBook
                })
                .then(response => {
                    this.$buefy.toast.open({
                        duration: 3000,
                        message: 'Election created successfully!',
                        type: 'is-success'
                    })

                    this.$router.push("/myelections").catch(e => {})
                })
                .catch(error => {
                    console.log(error)
                })
                .then(() => {
                    loadingSnackbar.close()
                    this.isLoading = false
                })
            })
        }
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back',"")
        this.startDate = new Date()
        this.endDate = new Date()

        this.startDate.setDate(this.startDate.getDate() + 1)
        this.endDate.setDate(this.endDate.getDate() + 1)
        this.endDate.setHours(this.endDate.getHours() + 3)       
    }
}
</script>
