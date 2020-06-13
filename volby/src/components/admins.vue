<template>
    <div>
        <div class="columns">
            <div class="column is-6">
                <h3 class="title is-3">Promote to Admin</h3>
                <div class="card box">
                    <div class="card-content">
                        <b-message v-show="isNotFound" type="is-danger">
                            No voter found with the submitted ID.
                        </b-message>
                        <b-message v-show="isAlreadyAdmin" type="is-danger">
                            The chosen voter is already an admin or a superadmin.
                        </b-message>
                        <validation-observer ref="observer" v-slot="{handleSubmit}">
                            <form @submit.prevent="handleSubmit(confirmSubmit)">
                                <div class="columns">
                                    <div class="column">
                                        <validation-provider vid="voterId" rules="required|email" name="Voter ID" v-slot="validationContext">
                                            <b-field :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <template slot="label">Voter ID <span class="has-text-danger">*</span></template>
                                                <b-input v-model="voterId"></b-input>
                                            </b-field>
                                        </validation-provider>
                                    </div>                                
                                </div>
                                <div class="columns">
                                    <div class="column">
                                        <b-button type="is-primary" expanded rounded native-type="submit" :loading="isLoadingPromote">Promote</b-button>
                                    </div>                                    
                                </div>
                            </form>
                        </validation-observer>
                    </div>
                </div>
            </div>
            <div class="column is-6">
                <h3 class="title is-3">Current Admins</h3>
                <div class="card box">
                    <div class="card-content">

                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
export default {
    data: function(){
        return {
            title: 'Admins',
            voterId: '',
            admins: [],
            isNotFound: false,
            isAlreadyAdmin: false,
            isLoadingPromote: false,
            isLoadingList: true
        }
    },
    methods: {
        getValidationState({ dirty, validated, valid = null }) {
            return dirty || validated ? (valid ? "" : "is-danger") : "";
        },
        confirmSubmit(){
            this.$buefy.dialog.confirm({
                title: 'Promote to Admin?',
                message: `Are you sure you want to <b>promote</b> ${this.voterId} to the Admin role?`,
                confirmText: 'Promote',
                type: 'is-success',
                onConfirm: () => this.submit()
            })
        },
        submit(){
            this.isLoadingPromote = true
            this.isNotFound = false
            this.isAlreadyAdmin = false

            axios.patch(`api/voters/${this.voterId}/type`,{
                'type': 'ADMIN'
            })
            .then(response => {
                this.admins.push(response.data.voter)
                this.$buefy.toast.open({
                    duration: 3000,
                    message: 'Admin added!',
                    type: 'is-success'
                })
            })
            .catch(error => {
                console.log(error)
                switch(error.response.status){
                    case 401:
                        this.$store.commit("logout")
                        this.$router.push("/login")
                        break
                    case 409:
                        this.isAlreadyAdmin = true
                        break
                    case 404:
                        this.isNotFound = true
                        break
                }
            })
            .then(() => {
                this.isLoadingPromote = false
            })
        },
        getAdmins(){

        }
    },
    created(){
        this.$emit('title',this.title)
        this.getAdmins()
    }
}
</script>