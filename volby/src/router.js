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
import UpdateVote from './components/updateVote'
import Election from './components/election'
import About from './components/about'
import Admins from './components/admins'
import MyElections from './components/myElections'
import UpdateElection from './components/updateElection'

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

const adminGuard = (to, from, next) => {
    if(store.getters.user.type == 'ADMIN' || store.getters.user.type == 'SUPERADMIN'){
        next()
    }else{
        next({name: "dashboard"})
    }
}

const superadminGuard = (to, from, next) => {
    if(store.getters.user.type == 'SUPERADMIN'){
        next()
    }else{
        next({name: "dashboard"})
    }
}

const routes = [
    {path: '/', component: Home, name: 'home'},
    {path: '/login', component: Login, name: 'login'},
    {path: '/register', component: Register, name: 'register'},
    {path: '/about', component: About, name: 'about'},
    {path: '',component: MainLayout, redirect: 'dashboard',
        children: [
            {path: 'dashboard', component: Dashboard, name: 'dashboard'},
            {path: 'newelection', component: CreateElection, name: 'createElection'},
            {path: 'elections', component: Elections, name: 'elections'},
            {path: 'election/:electionId/vote', component: CreateVote, name: 'createVote'},
            {path: 'vote/:voteId/update', component: UpdateVote, name: 'updateVote'},
            {path: 'election/:electionId', component: Election, name: 'election'},
            {path: 'election/:electionId/admin', component: Election, name: 'electionAdmin', beforeEnter: adminGuard},
            {path: 'myelections', component: MyElections, name: 'myElections', beforeEnter: adminGuard},
            {path: 'election/:electionId/update', component: UpdateElection, name: 'updateElection', beforeEnter: adminGuard},
            {path: 'admins', component: Admins, name: 'admins', beforeEnter: superadminGuard}
        ],
        beforeEnter: authGuard
    }
]

export const router = new VueRouter({
    routes,
    linkActiveClass: "is-active"
});
