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
                <b-navbar-item tag="router-link" to="dashboard">
                    Dashboard
                </b-navbar-item>
                <b-navbar-item tag="router-link" to="elections">
                    Elections
                </b-navbar-item>
                <b-navbar-item tag="router-link" to="newelection">
                    New Election
                </b-navbar-item>
            </template>

            <template slot="end">
            </template>
        </b-navbar>
        <div class="container is-fluid section has-padding-top-0">
            <h1 class="title is-1">
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
