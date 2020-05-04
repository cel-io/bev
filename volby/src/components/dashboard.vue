<template>
    <div>
        <h1>Dashboard</h1>
    </div>
</template>
<script>
export default{
    data(){
        return{
            title: "Dashboard",
        }
    },
    created() {
        this.$emit('title',this.title);
    }
}
</script>
