export function timestampToDate(timestamp){
    let date = new Date(timestamp * 1000)
    return ("0" + date.getDate()).slice(-2) + "/" + ("0" + (date.getMonth() + 1)).slice(-2) + "/" + date.getFullYear() + " " + ("0" + date.getHours()).slice(-2) + ":" + ("0" + date.getMinutes()).slice(-2)
}

export function timestampToDateObject(timestamp){
    return new Date(timestamp * 1000)
}