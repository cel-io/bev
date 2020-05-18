<template>
    <div>
        <b-navbar :shadow="true" :spaced="true" class="has-margin-bottom-20">
            <template slot="brand">
                <b-navbar-item tag="router-link" :to="{ path: '/' }">
                    <img
                    src="img/icon.png"
                    alt="Volby"
                    >
                </b-navbar-item>
            </template>
            <template slot="start">
                <b-navbar-item tag="router-link" to="/dashboard">
                    Dashboard
                </b-navbar-item>
                <b-navbar-item tag="router-link" to="/elections">
                    Elections
                </b-navbar-item>
                <b-navbar-item tag="router-link" to="/newelection">
                    New Election
                </b-navbar-item>
            </template>

            <template slot="end">
                <b-navbar-dropdown>
                    <template slot="label"><span class="has-margin-right-10">{{user.name}}</span> <b-tag type="is-volby" rounded>{{user.type}}</b-tag></template>
                    <b-navbar-item @click="logout">
                        Logout
                    </b-navbar-item>
                </b-navbar-dropdown>
            </template>
        </b-navbar>
        <div class="container is-fluid section has-padding-top-0">
            <div class="is-flex is-vcentered has-margin-bottom-30">
                <b-button class="has-margin-top-15 has-margin-right-15" v-if="backRedirect" tag="router-link" :to="backRedirect" rounded type="is-info" size="is-small" icon-left="arrow-left"></b-button>
                <h1 class="title is-1">
                    {{title}}
                </h1>
            </div>            
            <router-view @title="onTitle" @back="onBackButton"></router-view>
        </div>
    </div>
</template>
<script>
export default{
    data: function(){
        return{
            title: "",
            backRedirect: "",
            user: this.$store.getters.user
        }
    },
    methods: {
        onTitle: function(title){
            this.title = title
        },
        onBackButton: function(redirect){
            this.backRedirect = redirect
        },
        logout(){
            axios.post("api/logout")
            .then(response => {
                this.$store.commit('logout')
                this.$router.push("/home").catch(e => {})
            })
            .catch(error => {
                if(error.response.status == 401){
                    this.$store.commit('logout')
                    this.$router.push("/home").catch(e => {})
                }else{
                    console.log(error)
                }                                
            })            
        }
    }
}
</script>
