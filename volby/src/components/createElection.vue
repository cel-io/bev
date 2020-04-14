<template>
    <div>
        <ValidationObserver v-slot="{ handleSubmit }">
            <section>
                <div class="card box has-padding-bottom-40 has-margin-bottom-40">
                    <div class="card-content">
                        <b-tabs v-model="activeTab">
                            <b-tab-item label="Informations">
                                <ValidationProvider rules="required|alpha_spaces" name="Name" v-slot="{ errors, valid }">
                                    <b-field label="Name"  :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                        <b-input v-model="name"></b-input>
                                    </b-field>
                                </ValidationProvider>
                                <ValidationProvider rules="required|alpha_spaces" name="Description" v-slot="{ errors, valid }">
                                    <b-field label="Description" :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                        <b-input v-model="description" maxlength="200" type="textarea"></b-input>
                                    </b-field>
                                </ValidationProvider>
                                <div class="columns">
                                    <div class="column">
                                        <ValidationProvider rules="required" name="Start Date" v-slot="{ errors, valid }">
                                            <b-field label="Start Date" expanded :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                                <b-datetimepicker
                                                rounded
                                                v-model="startDate"
                                                placeholder="Click to select..."
                                                icon="calendar-today"
                                                :datepicker="{ showWeekNumber }"
                                                :timepicker="{ enableSeconds, hourFormat: format }"
                                                :min-datetime="dateNow"
                                                :max-datetime="endDate"
                                                horizontal-time-picker>
                                            </b-datetimepicker>
                                        </b-field>
                                    </ValidationProvider>
                                </div>
                                <div class="column">
                                    <ValidationProvider rules="required" name="End Date" v-slot="{ errors, valid }">
                                        <b-field label="End Date" expanded :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                            <b-datetimepicker
                                            rounded
                                            v-model="endDate"
                                            placeholder="Click to select..."
                                            icon="calendar-today"
                                            :datepicker="{ showWeekNumber }"
                                            :timepicker="{ enableSeconds, hourFormat: format }"
                                            :min-datetime="startDate ? startDate : dateNow"
                                            horizontal-time-picker>
                                        </b-datetimepicker>
                                    </b-field>
                                </ValidationProvider>
                            </div>
                        </div>
                        <div class="columns">
                            <div class="column">
                                <ValidationProvider rules="required" name="Results Exposure" v-slot="{ errors, valid }">
                                    <b-field label="Results Exposure" :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                        <b-select v-model="resultsPermission" expanded>
                                            <option value="0">Private</option>
                                            <option value="1">Voters Only</option>
                                            <option value="2">Public</option>
                                        </b-select>
                                    </b-field>
                                </ValidationProvider>
                            </div>
                            <div class="column">
                                {{resultsPermission == '0' ? 'Only the administrator can view the results.' : (resultsPermission == '1' ? 'Only the administrator and the voters can view the results.' : 'Everyone can view the results.' )}}
                            </div>
                        </div>
                        <div class="columns">
                            <div class="column">
                                <ValidationProvider rules="required" name="Can change Vote" v-slot="{ errors, valid }">
                                    <b-field label="Mutable Votes" :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                        <b-switch v-model="canChangeVote">
                                            {{canChangeVote ? 'Voters can change their vote multiple times after their initial choice' : "Voters can't change their vote after their initial choice"}}
                                        </b-switch>
                                    </b-field>
                                </ValidationProvider>
                            </div>
                            <div class="column">
                                <ValidationProvider rules="required" name="Realtime Results Exposure" v-slot="{ errors, valid }">
                                    <b-field label="Realtime Results Exposure" :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                        <b-switch v-model="canShowRealtime">
                                            {{canShowRealtime ? 'Results can be viewed in real time' : "Results can't be viewed in real time"}}
                                        </b-switch>
                                    </b-field>
                                </ValidationProvider>
                            </div>
                        </div>
                    </b-tab-item>
                    <b-tab-item label="Voting Options">
                        <div class="has-margin-bottom-20"><b-tag type="is-info">NOTE</b-tag> <b>Blank</b> and <b>Null</b> votes are default options.</div>
                        <div class="card box" v-for="(votingOption, index) in votingOptions" :key="index">
                            <div class="card-content">
                                <div class="columns">
                                    <div class="column is-one-third">
                                        <ValidationProvider rules="required|alpha_spaces|required_if:votingOption.description,''" name="Voting Name" v-slot="{ errors, valid }">
                                            <b-field label="Name" expanded :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                                <b-input v-model="votingOption.name"></b-input>
                                            </b-field>
                                        </ValidationProvider>
                                    </div>
                                    <div class="column">
                                        <ValidationProvider rules="alpha_spaces" name="Voting Description" v-slot="{ errors, valid }">
                                            <b-field label="Description" expanded :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                                <b-input v-model="votingOption.description"></b-input>
                                            </b-field>
                                        </ValidationProvider>
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
                    </b-tab-item>
                    <b-tab-item label="Poll Book">
                        <div class="card box" v-for="(voter, index) in pollBook" :key="index">
                            <div class="card-content">
                                <div class="columns">
                                    <div class="column is-one-third">
                                        <ValidationProvider rules="required|digits:9" name="Citizen ID" v-slot="{ errors, valid }">
                                            <b-field label="Citizen ID" expanded :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                                <b-input v-model="voter.id"></b-input>
                                            </b-field>
                                        </ValidationProvider>
                                    </div>
                                    <div class="column">
                                        <ValidationProvider rules="required|alpha_spaces" name="Voting Description" v-slot="{ errors, valid }">
                                            <b-field label="Name" expanded :type="{ 'is-danger': errors[0], 'is-success': valid }" :message="errors">
                                                <b-input v-model="voter.name"></b-input>
                                            </b-field>
                                        </ValidationProvider>
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
                    </b-tab-item>
                </b-tabs>
                <hr />
                <b-field>
                    <b-button type="is-primary" class="is-pulled-right" rounded @click.prevent="handleSubmit(submit)">Submit</b-button>
                </b-field>
            </div>
        </div>
    </section>
</ValidationObserver>
</div>
</template>
<script>
import {
    ValidationProvider,
    ValidationObserver
} from 'vee-validate/dist/vee-validate.full';

const api = require('../services/api');

export default{
    components: {
        ValidationObserver,
        ValidationProvider
    },
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
            resultsPermission: "1",
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

            // 'name': this.name,
            // 'description': this.description,
            // 'start_timestamp': this.toTimestamp(this.startDate),
            // 'end_timestamp': this.toTimestamp(this.endDate),
            // 'results_permission': this.resultsPermission,
            // 'can_change_vote': this.canChangeVote,
            // 'can_show_realtime': this.canShowRealtime,
            // "id_admin" : "1",
            // "id_vote" : "1",
            // "id_voting_options" : "1",
            // "id_poll_registration" : "1"

            api.post('elections', {
                "name" : "teste",
                "description" : "teste",
                "start_timestamp" : 1586527635,
                "end_timestamp" : 1586537635,
                "results_permission" : 0,
                "can_change_vote" : 0,
                "can_show_realtime" : 0,
                "id_admin" : "1",
                "id_vote" : "1",
                "id_voting_options" : "1",
                "id_poll_registration" : "1"
            })
            .then(response => {
                this.$router.push("home")
                console.log("Eleição criada");
            })
            .catch(api.alertError);
        }
    },
    created() {
        this.$emit('title',this.title);

    }
}
</script>
