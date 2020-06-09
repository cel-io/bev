<template>
    <div class="section has-padding-top-10">
        <div class="container">
            <div class="columns is-centered is-full-height is-vcentered">
                <div class="column has-text-centered has-padding-top-30">
                    <img class="image is-128x128 is-horizontal-center" src="img/icon.png"/>
                    <h1 id="home_title">Volby</h1>
                    <h4 id="home_subtitle">Login</h4>
                    <div class="columns is-centered">
                        <div class="column is-5">
                            <div class="card box has-padding-top-0 has-padding-left-0 has-padding-right-0 has-padding-bottom-0<">
                                <div class="card-content">
                                    <b-message v-show="isInvalidLogin" type="is-danger">
                                        Invalid email or password.
                                    </b-message>
                                    <validation-observer ref="observer" v-slot="{handleSubmit}">
                                        <validation-provider rules="required|email" name="Email" v-slot="validationContext">
                                            <b-field label="Email" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-input rounded v-model="email"></b-input>
                                            </b-field>
                                        </validation-provider>
                                        <validation-provider rules="required" name="Password" v-slot="validationContext">
                                            <b-field label="Password" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                                <b-input rounded type="password" v-model="password"></b-input>
                                            </b-field>
                                        </validation-provider>
                                        <b-button class="has-margin-top-20" type="is-primary" expanded rounded @click.prevent="handleSubmit(submit)">Login</b-button>
                                    </validation-observer>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>        
    </div>
</template>
<script>
export default{
    data(){
        return{
            email: "",
            password: "",
            isInvalidLogin: false
        }
    },
    methods: {
        submit(){
            this.isInvalidLogin = false

            axios.post('api/authentication',{
                voter_id: this.email,
                password: this.password
            })
            .then(response => {
                axios.defaults.headers.common.Authorization = "Bearer " + response.data.accessToken

                this.$store.commit("setAuthToken",response.data.accessToken)
                this.$store.commit("setUser",response.data.user)

                this.$buefy.toast.open({
                    duration: 3000,
                    message: 'Welcome to Volby!',
                    type: 'is-success'
                })

                this.$router.push("/dashboard").catch(e => {})
            })
            .catch(error => {
                if(error.response.status == 401){
                    this.isInvalidLogin = true
                }
            })
        },
        getValidationState({ dirty, validated, valid = null }) {
            return dirty || validated ? (valid ? "" : "is-danger") : "";
        }
    }
}
</script>
