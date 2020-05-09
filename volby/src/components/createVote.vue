<template>
    <h1>{{this.electionId}}</h1>
</template>
<script>
export default{
    data(){
        return{
            electionId: this.$route.params.electionId,
            title: "Vote",
        }
    },
    created() {
        this.$emit('title',this.title);
    }
}
</script>
