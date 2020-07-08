<template>
    <div>
        <div class="columns">
            <div class="column is-6">
                <h3 class="title is-3">Promote to Admin</h3>
                <div class="card box shadow">
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
                        <template v-if="isLoadingList">
                            <div class="columns is-centered">
                                <div class="column is-12 has-text-centered">
                                    <b-icon pack="fas" icon="sync-alt" size="is-large" custom-class="fa-spin"></b-icon>
                                </div>
                            </div>
                        </template>
                        <template v-else>
                            <b-table :data="admins"
                                :paginated="isPaginated"
                                :per-page="perPage"
                                :current-page.sync="currentPage"
                                :pagination-simple="isPaginationSimple"
                                :pagination-position="paginationPosition"
                                default-sort="type"
                                :default-sort-direction="'desc'"
                                aria-next-label="Next page"
                                aria-previous-label="Previous page"
                                aria-page-label="Page"
                                aria-current-label="Current page">

                                <template slot-scope="props">
                                    <b-table-column field="voter_id" label="Voter ID" sortable>
                                        {{ props.row.voter_id }}
                                    </b-table-column>
                                    <b-table-column field="name" label="Name" sortable>
                                        {{ props.row.name }}
                                    </b-table-column>
                                    <b-table-column field="type" label="Type" sortable>
                                        <b-tag type="is-volby">{{props.row.type}}</b-tag>
                                    </b-table-column>
                                </template>
                            </b-table>
                        </template>
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
            isLoadingList: true,
            isPaginated: true,
            perPage: 10,
            currentPage: 1,
            isPaginationSimple: false,
            paginationPosition: 'bottom'
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

            axios.patch(`/api/voters/${this.voterId}/type`,{
                'type': 'ADMIN'
            })
            .then(response => {
                this.admins.push(response.data.voter)

                this.voterId = ""
                this.$refs.observer.reset()

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
            axios.get('api/voters/admins')
            .then(response => {
                this.admins = response.data
                this.isLoadingList = false
            })
            .catch(error => {
                console.log(error)
                if(error.response.status == 401){
                    this.$store.commit("logout")
                    this.$router.push("/login")
                }
            })
        }
    },
    created(){
        this.$emit('title',this.title)
        this.getAdmins()
    }
}
</script>