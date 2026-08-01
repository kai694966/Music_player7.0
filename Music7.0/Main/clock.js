const timezone = document.getElementById("timezone")
const clock = document.getElementById("clock")

function newDate() {
    const now = new Date()
    const utc = now.getTime() + now.getTimezoneOffset() * 60 * 1000
    return new Date(utc+timezone.value*60*60*1000)
}

function updateClock() {
    let time = newDate()
    let days = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]
    let months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    let year = time.getFullYear()
    let month = months[time.getMonth()]
    let date = time.getDate()
    let day = days[time.getDay()]
    let hour = String(time.getHours()).padStart(2,"0")
    let minute = String(time.getMinutes()).padStart(2,"0")
    let second = String(time.getSeconds()).padStart(2,"0")
    let mSecond = String(time.getMilliseconds()).padStart(3,"0")
    let utcString = String(timezone.value)
    if (0 < utcString) {utcString = "+"+utcString}
    else if (0===utcString) {utcString=""}
    else if (0>utcString) {utcString=utcString}
    clock.innerHTML = `${day}, ${month} ${date}, ${year} ${hour}:${minute}:${second}:${mSecond} UTC${utcString}`
}

document.addEventListener("DOMContentLoaded",function() {
    const id = setInterval(() => {updateClock()},1000)
})

    let hour = String(time.getHours()).padStart(2, "0");
    let minute = String(time.getMinutes()).padStart(2, "0");
    let second = String(time.getSeconds()).padStart(2, "0");
    let mSecond = String(time.getMilliseconds()).padStart(3, "0");