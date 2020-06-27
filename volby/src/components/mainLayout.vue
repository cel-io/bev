<template>
    <div>
        <b-navbar :shadow="true" :spaced="true">
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
                <b-navbar-item v-if="user.type == 'ADMIN' || user.type == 'SUPERADMIN'" tag="router-link" to="/newelection">
                    New Election
                </b-navbar-item>
                <b-navbar-item v-if="user.type == 'SUPERADMIN'" tag="router-link" to="/admins">
                    Admins
                </b-navbar-item>
            </template>

            <template slot="end">
                <b-navbar-dropdown>
                    <template slot="label"><span class="has-margin-right-10">{{user.name}}</span> <b-tag type="is-volby">{{user.type}}</b-tag></template>
                    <b-navbar-item @click="logout">
                        Logout
                    </b-navbar-item>
                </b-navbar-dropdown>
            </template>
        </b-navbar>
        <div class="section">
            <div class="container main has-padding-top-0 has-margin-bottom-70">
                <div class="is-flex is-vcentered has-margin-bottom-30">
                    <b-button class="has-margin-top-15 has-margin-right-15" v-if="backRedirect" tag="router-link" :to="backRedirect" rounded type="is-info" size="is-small" icon-left="arrow-left"></b-button>
                    <h1 class="title is-1">
                        {{title}}
                    </h1>
                </div>
                <router-view @title="onTitle" @back="onBackButton"></router-view>
            </div>
        </div>
        <footer class="footer volby-footer has-padding-top-100">
            <div class="columns is-vcentered has-text-centered">
                <div class="column is-3">
                    <img class="image is-horizontal-center" width="50%" src="img/ipleiria.png" />
                </div>
                <div class="column is-6">
                    <p>Copyright © 2020 Bernardo Figueiredo and Célio Mendes @ IPLeiria.</p>
                    <p>All Rights Reserved</p>
                </div>
                <div class="column is-3">
                    <b-button type="is-text" tag="router-link" to="/about" target='_blank'>About Volby</b-button>
                </div>
            </div>
        </footer>
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
                this.$router.push("/").catch(e => {})
            })
            .catch(error => {
                if(error.response.status == 401){
                    this.$store.commit('logout')
                    this.$router.push("/").catch(e => {})
                }else{
                    console.log(error)
                }
            })
        }
    }
}
</script>
