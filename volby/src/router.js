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
import UpdateVote from './components/updateVote'

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
            {path: 'election/:electionId/vote', component: CreateVote, name: 'createVote'},
            {path: 'vote/:voteId/update', component: UpdateVote, name: 'updateVote'}
        ],
        beforeEnter: authGuard
    }
]

export const router = new VueRouter({
    routes
});
