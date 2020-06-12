<template>
    <div>
        <div class="column">
            <div class="column is-6">
                
            </div>
            <div class="column is-6">

            </div>
        </div>
    </div>
</template>
<script>
export default {
    data: function(){
        return {
            title: 'Admins'
        }
    },
    created(){
        this.$emit('title',this.title)
    }
}
</script>