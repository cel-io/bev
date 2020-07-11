import Vue from 'vue'
import VueRouter from 'vue-router'
Vue.use(VueRouter)
import {store} from './store.js'
import {isAfter} from "date-fns"

import Home from './components/home'
import Login from './components/login'
import Register from './components/register'
import MainLayout from './components/mainLayout'
import Start from './components/start'
import CreateElection from './components/createElection'
import CreateVote from './components/createVote'
import Elections from './components/elections.vue'
import UpdateVote from './components/updateVote'
import Election from './components/election'
import About from './components/about'
import Admins from './components/admins'
import MyElections from './components/myElections'
import UpdateElection from './components/updateElection'
import Public from './components/public'
import NotFound from './components/notFound'

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

const alreadyLoggedGuard = (to, from, next) => {
    if(store.getters.accessToken){
        next({name: "start"})
    }else{
        next()
    }
}

const adminGuard = (to, from, next) => {
    if(store.getters.user.type == 'ADMIN' || store.getters.user.type == 'SUPERADMIN'){
        next()
    }else{
        next({name: "start"})
    }
}

const superadminGuard = (to, from, next) => {
    if(store.getters.user.type == 'SUPERADMIN'){
        next()
    }else{
        next({name: "start"})
    }
}

const routes = [
    {path: "*", component: NotFound},
    {path: '/', component: Home, name: 'home', beforeEnter: alreadyLoggedGuard},
    {path: '/login', component: Login, name: 'login', beforeEnter: alreadyLoggedGuard},
    {path: '/register', component: Register, name: 'register', beforeEnter: alreadyLoggedGuard},
    {path: '/about', component: About, name: 'about'},
    {path: '',component: MainLayout, redirect: 'start',
        children: [
            {path: 'start', component: Start, name: 'start'},
            {path: 'newelection', component: CreateElection, name: 'createElection', beforeEnter: adminGuard},
            {path: 'elections', component: Elections, name: 'elections'},
            {path: 'election/:electionId/vote', component: CreateVote, name: 'createVote'},
            {path: 'vote/:voteId/update', component: UpdateVote, name: 'updateVote'},
            {path: 'election/:electionId', component: Election, name: 'election'},
            {path: 'election/:electionId/admin', component: Election, name: 'electionAdmin', beforeEnter: adminGuard},
            {path: 'myelections', component: MyElections, name: 'myElections', beforeEnter: adminGuard},
            {path: 'election/:electionId/update', component: UpdateElection, name: 'updateElection', beforeEnter: adminGuard},
            {path: 'admins', component: Admins, name: 'admins', beforeEnter: superadminGuard},
            {path: 'public', component: Public, name: 'public'}
        ],
        beforeEnter: authGuard
    }
]

export const router = new VueRouter({
    routes,
    linkActiveClass: "is-active"
});
