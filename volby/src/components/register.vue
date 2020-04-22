<template>
    <div class="is-full-height section has-padding-top-10">
        <div class="columns is-centered is-full-height is-vcentered">
            <div class="column has-text-centered has-padding-top-30">
                <img class="image is-128x128 is-horizontal-center" src="img/icon.png"/>
                <h4 id="home_subtitle">Register on <b>Volby</b></h4>
                <div class="columns is-centered">
                    <div class="column is-5">
                        <div class="card box  has-padding-top-0 has-padding-left-0 has-padding-right-0 has-padding-bottom-0<">
                            <div class="card-content">
                                <b-message v-if="isEmailUnique" type="is-danger">
                                    The email is already taken. Please, choose another one.
                                </b-message>
                                <validation-observer ref="observer" v-slot="{handleSubmit}">
                                    <validation-provider rules="required|min:2|alpha_spaces" name="Name" v-slot="validationContext">
                                        <b-field label="Name" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <b-input rounded v-model="name"></b-input>
                                        </b-field>
                                    </validation-provider>
                                    <validation-provider rules="required|email" name="Email" v-slot="validationContext">
                                        <b-field label="Email" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <b-input rounded v-model="email"></b-input>
                                        </b-field>
                                    </validation-provider>
                                    <validation-provider rules="required|min:6|confirmed:confirmation" name="Password" v-slot="validationContext">
                                        <b-field label="Password" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <b-input rounded type="password" v-model="password"></b-input>
                                        </b-field>
                                    </validation-provider>
                                    <validation-provider vid="confirmation" rules="required" v-slot="validationContext">
                                        <b-field label="Password Confirmation" :type="getValidationState(validationContext)" :message="validationContext.errors[0]">
                                            <b-input rounded type="password" v-model="confirmation"></b-input>
                                        </b-field>
                                    </validation-provider>
                                    <b-button class="has-margin-top-20" type="is-primary" expanded rounded @click.prevent="handleSubmit(submit)">Register</b-button>
                                </validation-observer>
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
            name: "",
            email: "",
            password: "",
            confirmation: "",
            isEmailUnique: ""
        }
    },
    methods: {
        submit(){
            this.isEmailUnique = false

            axios.post('api/voters',{
                name: this.name,
                voter_id: this.email,
                password: this.password,
                type: 'VOTER'
            })
            .then(response => {
                this.$buefy.toast.open({
                    duration: 3000,
                    message: 'Welcome to Volby!',
                    type: 'is-success'
                })
                this.$router.push("/newelection")
            })
            .catch(error => {
                if(error.response.status == 409){
                    this.isEmailUnique = true
                }
            })
        },
        getValidationState({ dirty, validated, valid = null }) {
            return dirty || validated ? (valid ? "" : "is-danger") : "";
        }
    }
}
</script>
