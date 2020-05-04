import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)

import {addSeconds} from 'date-fns'
export const store = new Vuex.Store({
    state(){
        return{
            accessToken: localStorage.getItem("accessToken"),
            tokensExpiry: localStorage.getItem("tokensExpiry"),
            user: localStorage.getItem("user")
        }
    },
    mutations: {
        setAuthToken(state, accessToken){
            localStorage.setItem("accessToken", accessToken)
            state.accessToken = localStorage.getItem("accessToken")

            const tokensExpiry = addSeconds(new Date(), 3600)
            state.tokensExpiry = tokensExpiry
            localStorage.setItem("tokensExpiry", tokensExpiry)
        },
        setUser(state, user){
            localStorage.setItem("user", user)
            state.user = localStorage.getItem("user")
        },
        logout(state){
            state.accessToken = null
            state.tokensExpiry = null
            state.user = null

            localStorage.removeItem("accessToken")
            localStorage.removeItem("tokensExpiry")
            localStorage.removeItem("user")
        }
    },
    getters: {
        accessToken: state => state.accessToken,
        tokensExpiry: state => state.tokensExpiry,
        user: state => state.user
    }
})
