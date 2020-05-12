<template>
    <div>
        <section>
            <div class="card box has-margin-bottom-40">
                <div class="card-content has-padding-bottom-0">
                    <b-field class="title is-1 has-text-centered">
                        <h1 ><strong>{{ this.election.name }}</strong></h1>
                    </b-field>
                    <b-field class="title is-5 has-text-centered">
                        <span>{{ this.election.description }}</span>
                    </b-field>
                    <p class="content title is-6">
                        <b> Voting Options </b>
                    </p>
                    <b-field v-for="(voting_option, index) in this.voting_options_array" :key="index">
                        <b-radio v-model="votingOptionSelected" type="is-sucess" name="name" :native-value="voting_option">
                            {{ (voting_option.name).toUpperCase() }}
                        </b-radio>
                        <hr v-if="voting_option == voting_options_array[voting_options_array.length - 2]">
                    </b-field >
                    <b-field class="is-pulled-right">
                        <b-button type="is-success" icon-left="check-circle" rounded @click.prevent="submit()">Vote</b-button>
                    </b-field>
                </br>
            </div>
        </div>
    </section>
</div>
</template>
<script>
export default{
    data(){
        return{
            title: "Vote",
            electionId: this.$route.params.electionId,
            election: {},
            voting_options_array: [],
            votingOptionSelected: ""
        }
    },
    methods: {
        submit(){
            console.log(this.votingOptionSelected)

            if(this.votingOptionSelected.name == "NULL" || this.votingOptionSelected.name == "BLANK" ){

                this.$buefy.dialog.confirm({
                    title: 'Default Voting Option Selected',
                    message: 'You just selected a default voting option (<b> NULL / BLANK</b>). If you sure of your vote click <b>Vote</b>',
                    confirmText: 'Vote',
                    type: 'is-warning',
                    hasIcon: true,
                    onConfirm: () => {
                        this.$buefy.toast.open('Vote submited!')

                        axios.post('api/vote/'+ this.votingOptionSelected.voting_option_id, {})
                        .then(response => {
                            this.$router.push("home")
                            console.log("Vote criado")
                        })
                        .catch(error => {
                            console.log(error)
                        })
                    }

                })
            }else{
                axios.post('api/vote/'+ this.votingOptionSelected.voting_option_id, {})
                .then(response => {
                    this.$router.push("home")
                    console.log("Vote criado")
                })
                .catch(error => {
                    console.log(error)
                })
            }
        }
    },
    mounted(){
        let token = "eyJhbGciOiJIUzUxMiIsImlhdCI6MTU4OTE5NzAyNiwiZXhwIjoxNTg5MjAwNjI2fQ.eyJwdWJsaWNfa2V5IjoiMDNhYmVmNmFlMTNhZGUzY2UzZDZiMjg0NzE3MGIzOGM0YmRhMDJhZGE3ZDYzYjkwYTc5OWQ0N2I3MzcyNDc5MzdjIn0.MrvzhQ8P9kiHx0Ou_qzjqoVdgNYq0FzzxYAopeMaZo8d3kVDjCQ8ujtiuYu7sUOvrCSShxm1roc0KnrheYjDbg"
        axios.defaults.headers.common.Authorization = "Bearer " + token;

        axios.get('api/elections/'+ this.electionId)
        .then(response => {
            this.election = response.data

            axios.get('api/elections/'+ this.electionId +'/voting_options')
            .then(response => {
                this.voting_options_array = response.data
                this.voting_options_array.sort(function(a, b){
                    if(a.id < b.id) { return -1; }
                    if(a.id > b.id) { return 1; }
                    return 0;
                })
            })
            .catch(error => {
                console.log(error)
            })
        })
        .catch(error => {
            console.log(error)
        })


    },
    created() {
        this.$emit('title',this.title);
    }
}
</script>
