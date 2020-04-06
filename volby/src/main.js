
window.Vue = require('vue')
import Vue from 'vue'

import Home from './components/home'
import CreateElection from './components/home'

import Buefy from 'buefy'
import 'buefy/dist/buefy.css'
Vue.use(Buefy)

import VueRouter from 'vue-router'
Vue.use(VueRouter)

const routes = [
    {path: '/', component: Home, name: 'home'}, //redirecionar para Dashboard se nao existir autenticação
    {path: '/newelection', component: CreateElection, name: 'createElection'}
]

const router = new VueRouter({
    routes
});

const app = new Vue({
    el: '#app',
    router,
    data: {

    },
    methods: {},
    mounted() {}
});
