<template>
    <div class="section has-padding-top-10">
        <div class="container">
            <div class="columns is-centered is-full-height is-vcentered">
                <div class="column is-half has-text-centered has-padding-top-0">
                    <img class="image is-256x256 is-horizontal-center" src="img/icon.png"/>
                    <h1 id="home_title">Volby</h1>
                    <h4 id="home_subtitle">Blockchain-Enabled E-Voting</h4>
                    <div class="columns has-margin-top-10">
                        <div class="column">
                            <b-button tag="router-link" to="/login" type="is-volby" size="is-large" rounded expanded outlined>Login</b-button>
                        </div>
                        <div class="column">
                            <b-button tag="router-link" to="/register" type="is-volby" size="is-large" rounded expanded outlined>Register</b-button>
                        </div>
                    </div>
                </div>
            </div>
        </div>        
    </div>
</template>
<script>
export default {

}
</script>
