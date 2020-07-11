<template>
    <div>
        <div class="columns">
            <div class="column">
                <b-tooltip class="is-full-width" multilined type="is-dark" label="Vote in elections that you are registered in or check past elections.">
                    <b-button tag="router-link" to="/elections" type="is-volby" size="is-large" icon-left="vote" rounded expanded outlined>Elections</b-button>
                </b-tooltip>
            </div>
            <div class="column">
                <b-tooltip class="is-full-width"  multilined type="is-dark" label="View elections that are open to the public.">
                    <b-button tag="router-link" to="/public" type="is-volby" size="is-large" icon-left="earth" rounded expanded outlined>Public Elections</b-button>
                </b-tooltip>
            </div>
        </div>
        <div class="columns">
            <template v-if="$parent.user.type != 'VOTER'">
                <div class="column">
                    <b-tooltip class="is-full-width" multilined type="is-dark" label="Create a new election.">
                        <b-button tag="router-link" to="/newelection" type="is-volby" size="is-large" icon-left="folder-plus" rounded expanded outlined>New Election</b-button>
                    </b-tooltip>
                </div>
                <div class="column">
                    <b-tooltip class="is-full-width"  multilined type="is-dark" label="Access and manage elections that you created.">
                        <b-button tag="router-link" to="/myelections" type="is-volby" size="is-large" icon-left="view-list" rounded expanded outlined>My Elections</b-button>
                    </b-tooltip>
                </div>
            </template>            
            <div class="column" v-if="$parent.user.type == 'SUPERADMIN'">
                <b-tooltip class="is-full-width"  multilined type="is-dark" label="Manage the Administrators in the platform.">
                    <b-button tag="router-link" to="/admins" type="is-volby" size="is-large" icon-left="account-group" rounded expanded outlined>Admins</b-button>
                </b-tooltip>
            </div>
        </div>
    </div>
</template>
<script>
export default{
    data(){
        return{
            title: "Start",
        }
    },
    created() {
        this.$emit('title',this.title)
        this.$emit('back',"")
    }
}
</script>

