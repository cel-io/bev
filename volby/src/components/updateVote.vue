<template>
    <div>
        <div class="card box has-margin-bottom-40">
            <div class="card-content has-padding-bottom-0">
                <b-field class="title is-1 has-text-centered">
                    <h1 ><strong>{{ this.election.name }}</strong></h1>
                </b-field>
                <b-field class="title is-5 has-text-centered">
                    <span>{{ this.election.description }}</span>
                </b-field>
                <p class="content title is-6">
                    <b> Voting Options: </b>
                </p>
                <b-field v-for="(voting_option, index) in this.voting_options_array" :key="index">
                    <b-radio v-model="votingOptionSelectedId" type="is-sucess" name="name" :native-value="voting_option.voting_option_id">
                        {{ (voting_option.name).toUpperCase() }}
                    </b-radio>
                    <hr v-if="voting_option == voting_options_array[voting_options_array.length - 2]">
                </b-field >
                <b-field class="is-pulled-right">
                    <b-button type="is-success" icon-left="check-circle" rounded @click.prevent="submit()">Vote</b-button>
                </b-field>
            </div>
        </div>
    </div>
</template>
<script>
export default{
    data(){
        return{
            title: "Update Vote",
            voteId: this.$route.params.voteId,
            election: {},
            old_vote: {},
            voting_options_array: [],
            votingOptionSelected: {},
            votingOptionSelectedId: 0
        }
    },
    methods: {
        submit(){
            if(this.votingOptionSelectedId == this.old_vote.voting_option_id){
                this.$buefy.toast.open({
                    duration: 5000,
                    message: `Invalid Operation! Can't vote in the same option.`,
                    type: 'is-danger'
                })
                return
            }


            this.voting_options_array.forEach(voting_option => {
                if(voting_option.voting_option_id == this.votingOptionSelectedId ){
                    Object.assign(this.votingOptionSelected,voting_option)
                    return
                }
            })

            if(this.votingOptionSelected.name == "NULL" || this.votingOptionSelected.name == "BLANK" ){
                this.$buefy.dialog.confirm({
                    title: 'Default Voting Option Selected',
                    message: 'You just selected a default voting option (<b> NULL / BLANK</b>). If you sure of your vote click <b>Vote</b>',
                    confirmText: 'Vote',
                    type: 'is-warning',
                    hasIcon: true,
                    onConfirm: () => {
                        axios.put('api/votes/'+ this.old_vote.vote_id + '/update', {
                            "voting_option_id": this.votingOptionSelected.voting_option_id
                        })
                        .then(response => {
                            this.$router.push("/dashboard")
                            this.$buefy.toast.open({
                                duration: 5000,
                                message: 'Vote updated',
                                position: 'is-top-right',
                                type: 'is-sucess'
                            })
                        })
                        .catch(error => {
                            console.log(error)
                        })
                    }

                })
            }else{
                axios.put('api/votes/'+ this.old_vote.vote_id + '/update', {
                    "voting_option_id": this.votingOptionSelected.voting_option_id
                })
                .then(response => {
                    this.$buefy.toast.open({
                        duration: 5000,
                        message: 'Vote successfully!',
                        position: 'is-top-right',
                        type: 'is-sucess'
                    })
                    this.$router.push('/eletions')                    
                })
                .catch(error => {
                    console.log(error)
                })
            }
        }
    },
    mounted(){
        axios.get('api/votes/'+ this.voteId)
        .then(response => {
            this.old_vote = response.data
            this.votingOptionSelectedId = this.old_vote.voting_option_id

            axios.get('api/elections/'+ this.old_vote.election_id)
            .then(response => {
                this.election = response.data
                
                axios.get('api/elections/'+ this.old_vote.election_id +'/voting_options')
                .then(response => {
                    this.voting_options_array = response.data
                    this.voting_options_array.sort(function(a, b){
                        if(a.id < b.id) { return -1; }
                        if(a.id > b.id) { return 1; }
                        return 0;
                    })

                })
                .catch(error => {
                    console.log(error.data)
                })
            })
            .catch(error => {
                console.log(error.data)
            })
        })
        .catch(error => {
            console.log(error.data)
        })
    },
    created(){
        this.$emit('title',this.title)
        this.$emit('back',"")
    }
}
</script>
