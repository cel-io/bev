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
                                        <validation-provider rules="required|alpha_spaces" name="Name" v-slot="validationContext">
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
                                <div class="columns">
                                    <div class="column">
                                        <validation-provider rules="required" name="Multiple Options" v-slot="validationContext">
                                            <b-field label="Multiple Options" expanded>
                                                <b-switch v-model="canChooseMultipleOptions" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                    {{canChooseMultipleOptions ? 'Voters can choose multiple options based on a defined criteria' : "Voters can only choose one option"}}
                                                </b-switch>
                                            </b-field>
                                        </validation-provider>
                                    </div>
                                    <div class="column">
                                        <div class="columns" v-if="canChooseMultipleOptions">
                                            <div class="column">
                                                <validation-provider rules="required_if:canChooseMultipleOptions,true" name="Criteria" v-slot="validationContext">
                                                    <b-field label="Criteria" expanded>
                                                        <b-select v-model="multipleOptionsCriteria" @input="criteriaChange" :type="getValidationState(validationContext)" :message="validationContext.errors[0]" expanded>
                                                            <option value="AT_MOST">At most</option>
                                                            <option value="EQUAL_TO">Equal to</option>
                                                            <option value="AT_LEAST">At least</option>
                                                            <option value="BETWEEN">Between</option>
                                                        </b-select>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <div class="column">
                                                <validation-provider :rules="{required: canChooseMultipleOptions, min_value: 2, max_value: multipleOptionsCriteria != 'BETWEEN' ? Infinity : multipleOptionsValueMax}" :name="multipleOptionsCriteria != 'BETWEEN' ? 'Criteria Value' : 'Criteria Min. Value'" v-slot="validationContext">
                                                    <b-field :label="multipleOptionsCriteria != 'BETWEEN' ? 'Criteria Value' : 'Criteria Min. Value'" :type="getValidationState(validationContext)" :message="validationContext.errors[0]" expanded>
                                                        <b-numberinput expanded v-model="multipleOptionsValueMin" controls-position="compact"></b-numberinput>
                                                    </b-field>
                                                </validation-provider>
                                            </div>
                                            <template v-if="multipleOptionsCriteria == 'BETWEEN'">
                                                <div class="column">
                                                    <validation-provider :rules="{required: canChooseMultipleOptions, min_value: multipleOptionsCriteria != 'BETWEEN' ? -Infinity : multipleOptionsValueMin}" :name="multipleOptionsCriteria != 'BETWEEN' ? 'Criteria Value' : 'Criteria Min. Value'" v-slot="validationContext">
                                                        <b-field label="Criteria Max. Value" :type="getValidationState(validationContext)" :message="validationContext.errors[0]" expanded>
                                                            <b-numberinput expanded v-model="multipleOptionsValueMax" controls-position="compact"></b-numberinput>
                                                        </b-field>
                                                    </validation-provider>
                                                </div>
                                            </template>
                                        </div>
                                    </b-field>
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
                                <b-message :closable="false" v-if="canChooseMultipleOptions" title="Multiple Options" type="is-info" has-icon>
                                    There must be <b>at least {{multipleOptionsCriteria != 'BETWEEN' ? multipleOptionsValueMin : multipleOptionsValueMax }} voting options</b> to comply with the <b>multiple options criteria</b> chosen in the 'Informations' section.
                                </b-message>
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
                                            <div v-if="votingOptions.length > 1" class="column is-narrow" style="margin-top: auto;" rounded>
                                                <b-button @click="removeVotingOption(index)" type="is-danger" icon-right="delete" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <b-button @click="addVotingOption" class="is-pulled-right" icon-right="plus" type="is-info" rounded></b-button>
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
                                                <b-button @click="removeVoter(index)" type="is-danger" icon-right="delete" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <b-button @click="addVoter" class="is-pulled-right" icon-right="plus" type="is-info" rounded></b-button>
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
            canChooseMultipleOptions: false,
            multipleOptionsCriteria: 'EQUAL_TO', //AT_MOST, EQUAL_TO, AT_LEAST, BETWEEN
            multipleOptionsValueMin: 2,
            multipleOptionsValueMax: 4,
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
        criteriaChange(){
            if(this.multipleOptionsCriteria == 'BETWEEN')
            this.multipleOptionsValueMax = this.multipleOptionsValueMin + 2
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
            if(this.canChooseMultipleOptions && this.multipleOptionsCriteria != 'BETWEEN' && this.votingOptions.length < this.multipleOptionsValueMin){
                this.activeTab = 1
                this.$buefy.toast.open({
                    duration: 5000,
                    message: 'Please, create at least <b>' + this.multipleOptionsValueMin + ' voting options</b> or change the defined criteria',
                    type: 'is-danger'
                })
                return
            }else if(this.canChooseMultipleOptions && this.multipleOptionsCriteria == 'BETWEEN' && this.votingOptions.length < this.multipleOptionsValueMax){
                this.activeTab = 1
                this.$buefy.toast.open({
                    duration: 5000,
                    message: 'Please, create at least <b>' + this.multipleOptionsValueMax + ' voting options</b> or change the defined criteria',
                    type: 'is-danger'
                })
                return
            }


            let token = "eyJhbGciOiJIUzUxMiIsImlhdCI6MTU4NzQxMzUzMywiZXhwIjoxNTg3NDE3MTMzfQ.eyJwdWJsaWNfa2V5IjoiMDNmMzNjNmEzYzExYzczYjFjYTQ3MWQ0ODVkZmM3OTkxMjEzMGIwNTVjMWM1MTZkMGFhNWYwMDVmMTRjOWJiODM5In0.rMr7tiCRSYYv0DO1ImzCjeH29arhO5p2Welir_SNLm1nr0fINBGB9bWvi7VCVo27JiCUTesXETD5SjtjWL7D1w"
            axios.defaults.headers.common.Authorization = "Bearer " + token;

            axios.post('api/elections', {
                "name": this.name,
                "description": this.description,
                "start_timestamp": this.toTimestamp(this.startDate),
                "end_timestamp": this.toTimestamp(this.startDate),
                "results_permission": this.resultsPermission,
                "can_change_vote": this.canChangeVote,
                "can_show_realtime": this.canShowRealtime,
                "voting_options": this.votingOptions,
                "poll_book": this.pollBook,
                "can_choose_multiple_options": this.canChooseMultipleOptions,
                "multiple_options_criteria": this.canChooseMultipleOptions ? this.multipleOptionsCriteria : "",
                "multiple_options_value_min": this.canChooseMultipleOptions ? this.multipleOptionsValueMin : 0,
                "multiple_options_value_max": this.canChooseMultipleOptions && this.multipleOptionsCriteria == 'BETWEEN' ? this.multipleOptionsValueMax : 0
            })
            .then(response => {
                this.$router.push("home")
                console.log("Eleição criada")
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
