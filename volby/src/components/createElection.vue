<template>
    <div>
        <section>
            <div class="card box has-margin-bottom-40">
                <div class="card-content has-padding-bottom-0">
                    <validation-observer ref="observer" v-slot="{ handleSubmit }">
                        <b-tabs v-model="activeTab">
                            <b-tab-item label="Informations">
                                <div class="columns">
                                    <div class="column">
                                        <validation-provider rules="required" name="Name" v-slot="validationContext">
                                            <b-field label="Name" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-input v-model="name"></b-input>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <b-field label="Description">
                                            <b-input v-model="description" maxlength="200" type="textarea"></b-input>
                                        </b-field>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <validation-provider rules="required" name="Start Date" v-slot="validationContext">
                                            <b-field label="Start Date" expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-datetimepicker rounded v-model="startDate" placeholder="Click to select..." icon="calendar-today" :datepicker="{ showWeekNumber }" :timepicker="{ enableSeconds, hourFormat: format }" :min-datetime="dateNow" :max-datetime="endDate" horizontal-time-picker>
                                                </b-datetimepicker>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                    <div class="column">
                                        <validation-provider rules="required" name="End Date" v-slot="validationContext">
                                            <b-field label="End Date" expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-datetimepicker rounded v-model="endDate" placeholder="Click to select..." icon="calendar-today" :datepicker="{ showWeekNumber }" :timepicker="{ enableSeconds, hourFormat: format }" :min-datetime="startDate ? startDate : dateNow" horizontal-time-picker>
                                                </b-datetimepicker>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                </div>
                                <div class="columns is-vcentered">
                                    <div class="column">
                                        <validation-provider rules="required" name="Results Exposure" v-slot="validationContext">
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
                                        <validation-provider rules="required" name="Mutable Votes" v-slot="validationContext">
                                            <b-field label="Mutable Votes" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-switch v-model="canChangeVote">
                                                    {{canChangeVote ? 'Voters can change their vote multiple times after their initial choice' : "Voters can't change their vote after their initial choice"}}
                                                </b-switch>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                    <div class="column">
                                        <validation-provider rules="required" name="Realtime Results Exposure" v-slot="validationContext">
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
                                                <validation-provider rules="required" :name="(index + 1) + '. Option Name'" v-slot="validationContext">
                                                    <b-field :label="(index + 1) + '. Option Name'" expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                        <b-input v-model="votingOption.name"></b-input>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <div class="column">
                                                <validation-provider rules="" :name="(index + 1) + '. Option Description'" v-slot="validationContext">
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
                                                <validation-provider :rules="{
                                                    required: true,
                                                    email: true,
                                                    unique: pollBook
                                                    }" :name="(index + 1) + '. Voter Email'" v-slot="validationContext">
                                                    <b-field :label="(index + 1) + '. Voter Email'" expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                        <b-input v-model="voter.id"></b-input>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <div class="column">
                                                <validation-provider rules="required|alpha_spaces" :name="(index + 1) + '. Voter Name '" v-slot="validationContext">
                                                    <b-field :label="(index + 1) + '. Voter Name'" expanded :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
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
                                    <b-button type="is-primary" rounded @click.prevent="handleSubmit(submit)">Submit</b-button>
                                </b-field>
                            </b-tab-item>
                        </b-tabs>

                    </validation-observer>
                </div>
            </div>
        </section>
    </div>
</template>
<script>

import { extend } from 'vee-validate';
import {unique} from 'vee-validate/dist/rules';

extend('unique', {
    validate(value, obj) {
        if (obj.filter(o => o.id === value).length > 1) {
            return  `${value} is already taken.`
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
            name: "",
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
                    name: "",
                    description: ""
                }
            ],
            pollBook: [
                {
                    id: "",
                    name: ""
                }
            ]
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
            axios.post('api/elections', {
                "name": this.name,
                "description": this.description,
                "start_timestamp": this.toTimestamp(this.startDate),
                "end_timestamp": this.toTimestamp(this.startDate),
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

                this.$router.push("/dashboard").catch(e => {})
            })
            .catch(error => {
                console.log(error)
            })
        }
    },
    created() {
        this.$emit('title',this.title);
    }
}
</script>
