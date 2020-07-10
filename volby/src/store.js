import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)

import {addSeconds} from 'date-fns'
export const store = new Vuex.Store({
    state(){
        return{
            accessToken: localStorage.getItem("accessToken"),
            tokensExpiry: localStorage.getItem("tokensExpiry"),
            user: JSON.parse(localStorage.getItem("user"))
        }
    },
    mutations: {
        setAuthToken(state, accessToken){
            localStorage.setItem("accessToken", accessToken)
            state.accessToken = accessToken

            const tokensExpiry = addSeconds(new Date(), 3600)
            state.tokensExpiry = tokensExpiry
            localStorage.setItem("tokensExpiry", tokensExpiry)
        },
        setUser(state, user){
            localStorage.setItem("user", JSON.stringify(user))
            state.user = user
        },
        logout(state){
            axios.defaults.headers.common.Authorization = ""

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
