import Vue from 'vue'
import VueRouter from 'vue-router'
Vue.use(VueRouter)
import {store} from './store.js'
import {isAfter} from "date-fns"

import Home from './components/home'
import Login from './components/login'
import Register from './components/register'
import MainLayout from './components/mainLayout'
import Dashboard from './components/dashboard'
import CreateElection from './components/createElection'
import CreateVote from './components/createVote'
import Elections from './components/elections.vue'

const authGuard = (to, from, next) => {
    if(store.getters.accessToken){
        if(!isAfter(new Date(),new Date(localStorage.getItem("tokensExpiry")))){
            next()
        }else{
            store.commit("logout")
            next({name: "login"})
        }
    }else{
        next({name: "login"})
    }
}

const routes = [
    {path: '/home', component: Home, name: 'home'},
    {path: '/login', component: Login, name: 'login'},
    {path: '/register', component: Register, name: 'register'},
    {path: '/',component: MainLayout, redirect: 'dashboard',
        children: [
            {path: 'dashboard', component: Dashboard, name: 'dashboard'},
            {path: 'newelection', component: CreateElection, name: 'createElection'},
            {path: 'elections', component: Elections, name: 'elections'},
            {path: 'elections/:electionId/vote', component: CreateVote, name: 'createVote'}
        ],
        beforeEnter: authGuard
    }
]

export const router = new VueRouter({
    routes,
    linkActiveClass: "is-active"
});
