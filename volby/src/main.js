window._ = require('lodash');

window.axios = require('axios');
window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
window.axios.interceptors.response.use(function (response) {
    return response;
}, function (error) {
    switch (error.response.status) {
        case 401:
            if(error.config.url != '/api/authentication'){
                this.$store.commit('logout')
                this.$router.push("/login")
                this.$buefy.toast.open({
                    duration: 3000,
                    message: 'Your session expired.',
                    type: 'is-warning'
                })
            }            
            break
        case 403:
            this.$router.push("/start")
            this.$buefy.toast.open({
                duration: 3000,
                message: "You don't have permission to make this action.",
                type: 'is-warning'
            })
            break
    }

    return Promise.reject(error);
});

window.Vue = require('vue')
import Vue from 'vue'

import Buefy from 'buefy'
Vue.use(Buefy)
import 'bulma-spacing/css/bulma-spacing.min.css'

import {ValidationObserver, ValidationProvider, Validator, extend, localize} from "vee-validate";
import en from "vee-validate/dist/locale/en.json";
import * as rules from "vee-validate/dist/rules";
Object.keys(rules).forEach(rule => {
  extend(rule, rules[rule]);
});
localize("en", en);
Vue.component("ValidationObserver", ValidationObserver);
Vue.component("ValidationProvider", ValidationProvider);

import VueCountdown from '@chenfengyuan/vue-countdown';
Vue.component(VueCountdown.name, VueCountdown);

import {isAfter} from "date-fns"

import {store} from './store.js'

import {router} from './router.js'

const app = new Vue({
    el: '#app',
    router,
    store,
    data: {

    },
    methods: {},
    created() {
        if(localStorage.getItem("accessToken") !== null){
            if(isAfter(new Date(),new Date(localStorage.getItem("tokensExpiry")))){
                this.$store.commit('logout')

                return this.$router.push("/login")
            }
            window.axios.defaults.headers.common.Authorization = "Bearer " + localStorage.getItem("accessToken")
        }
    }
});
