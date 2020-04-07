<template>
    <div>
        <section>
            <div class="card box has-margin-bottom-40">
                <div class="card-content">
                    <b-field label="Name">
                        <b-input v-model="name"></b-input>
                    </b-field>
                    <b-field label="Description">
                        <b-input v-model="description" maxlength="200" type="textarea"></b-input>
                    </b-field>
                    <div class="columns">
                        <div class="column">
                            <b-field label="Start Date" expanded>
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
                        </div>
                        <div class="column">
                            <b-field label="End Date" expanded>
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
                        </div>
                    </div>
                    <div class="columns is-vcentered">
                        <div class="column">
                            <b-field label="Results Exposure">
                                <b-select v-model="resultsPermission" expanded>
                                    <option value="0">Private</option>
                                    <option value="1">Voters Only</option>
                                    <option value="2">Public</option>
                                </b-select>
                            </b-field>
                        </div>
                        <div class="column">
                            {{resultsPermission == '0' ? 'Only the administrator can view the results.' : (resultsPermission == '1' ? 'Only the administrator and the voters can view the results.' : 'Everyone can view the results.' )}}
                        </div>
                    </div>
                    <div class="columns">
                        <div class="column">
                            <b-field label="Mutable Votes">
                                <b-switch v-model="canChangeVote">
                                    {{canChangeVote ? 'Voters can change their vote multiple times after their initial choice' : "Voters can't change their vote after their initial choice"}}
                                </b-switch>
                            </b-field>
                        </div>
                        <div class="column">
                            <b-field label="Realtime Results Exposure">
                                <b-switch v-model="canShowRealtime">
                                    {{canShowRealtime ? 'Results can be viewed in real time' : "Results can't be viewed in real time"}}
                                </b-switch>
                            </b-field>
                        </div>
                    </div>
                    <b-field class="has-margin-bottom-20">
                        <b-button type="is-primary" class="is-pulled-right" rounded>Submit</b-button>
                    </b-field>
                </div>
            </div>
        </section>
    </div>
</template>
<script>
export default{
    data(){
        return{
            title: "New Election",
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
            canShowRealtime: true
        }
    },
    created() {
        this.$emit('title',this.title);
    }
}
</script>
