<template>
    <div>
        <b-navbar :shadow="true" :spaced="true" class="has-margin-bottom-20">
            <template slot="brand">
                <b-navbar-item tag="router-link" :to="{ path: '/' }">
                    <!--<img
                    src="https://raw.githubusercontent.com/buefy/buefy/dev/static/img/buefy-logo.png"
                    alt="Lightweight UI components for Vue.js based on Bulma"
                    > -->
                    VOLBY
                </b-navbar-item>
            </template>
            <template slot="start">
                <b-navbar-item href="#">
                    Home
                </b-navbar-item>
                <b-navbar-item href="#">
                    Documentation
                </b-navbar-item>
                <b-navbar-dropdown label="Info">
                    <b-navbar-item href="#">
                        About
                    </b-navbar-item>
                    <b-navbar-item href="#">
                        Contact
                    </b-navbar-item>
                </b-navbar-dropdown>
            </template>

            <template slot="end">
                <b-navbar-item tag="div">
                    <div class="buttons">
                        <a class="button is-primary">
                            <strong>Sign up</strong>
                        </a>
                        <a class="button is-light">
                            Log in
                        </a>
                    </div>
                </b-navbar-item>
            </template>
        </b-navbar>
        <div class="container">
            <h1 class="title">
                {{title}}
            </h1>
            <router-view @title="onTitle"></router-view>
        </div>
    </div>
</template>
<script>
export default{
    data: function(){
        return{
            title: ""
        }
    },
    methods: {
        onTitle: function(title){
            this.title = title
        }
    }
}
</script>
