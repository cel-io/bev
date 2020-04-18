window._ = require('lodash');

window.axios = require('axios');
window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

window.Vue = require('vue')
import Vue from 'vue'

import Home from './components/home'
import Login from './components/login'
import Register from './components/register'
import MainLayout from './components/mainLayout'
import CreateElection from './components/createElection'

import Buefy from 'buefy'
import 'buefy/dist/buefy.css'
Vue.use(Buefy)
import 'bulma-spacing/css/bulma-spacing.min.css'

import {ValidationObserver, ValidationProvider, extend, localize} from "vee-validate";
import en from "vee-validate/dist/locale/en.json";
import * as rules from "vee-validate/dist/rules";
Object.keys(rules).forEach(rule => {
  extend(rule, rules[rule]);
});
localize("en", en);
Vue.component("ValidationObserver", ValidationObserver);
Vue.component("ValidationProvider", ValidationProvider);

import VueRouter from 'vue-router'
Vue.use(VueRouter)

const routes = [
    {path: '/home', component: Home, name: 'home'},
    {path: '/login', component: Login, name: 'login'},
    {path: '/register', component: Register, name: 'register'},
    {path: '/',component: MainLayout, redirect: 'newelection',
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
