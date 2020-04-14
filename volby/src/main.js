window._ = require('lodash');

window.axios = require('axios');
window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

window.Vue = require('vue')
import Vue from 'vue'

import Home from './components/home'
import MainLayout from './components/mainLayout'
import CreateElection from './components/createElection'

import Buefy from 'buefy'
import 'buefy/dist/buefy.css'
Vue.use(Buefy)
import 'bulma-spacing/css/bulma-spacing.min.css'

import VueRouter from 'vue-router'
Vue.use(VueRouter)

const routes = [
    {path: '/home', component: Home, name: 'home'}, //redirecionar para Dashboard se nao existir autenticação
    {path: '/', component: MainLayout,
        children: [
            {path: 'newelection', component: CreateElection, name: 'createElection'}
        ]
    }
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
