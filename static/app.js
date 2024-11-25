
document.addEventListener('DOMContentLoaded', () => {

function tryFetchingEndpoint (endpoint, outputDiv) { //event just for the need of .bind()
    // console.log('tryFetchingEndpoint')
    output = document.getElementById(outputDiv)
    try {
        url = window.origin.toString() + "/" + endpoint.toString()
        fetch( url, {
            cache: "no-cache",
        }) //fetch returns async promise, then do something with the results
            .then(function (response) {
                if (response.status !== 200) { //response status from flask
                    output.innerText = 'response status code: ' + response.status
                    return
                }
                response.json().then(function (data) {
                    output.innerText = data.message.slice(0,250) //slice if str too long
                })
            })
    }
    catch (error) { //doesnt really reach this point
        console.log('JS ERROR CATCHED' + error)
        return
    }
}

document.getElementById("openBrowserButton").addEventListener("click", () => { tryFetchingEndpoint('openBrowser', 'openBrowserOutput') })
document.getElementById("saveCookiesToJsonButton").addEventListener("click", () => { tryFetchingEndpoint('saveCookiesToJson', 'saveCookiesToJsonOutput') })
document.getElementById("fullScrapingButton").addEventListener("click", () => { tryFetchingEndpoint('fullScraping', 'fullScrapingOutput') })








// document.getElementById("openBrowserButton").addEventListener("click", openBrowser)

// function openBrowser() {
//     output = document.getElementById('openBrowserOutput')
//     try {
//         fetch(window.origin + '/openBrowser', {
//             cache: "no-cache",
//         }) //fetch returns async promise, then do something with the results
//             .then(function (response) {
//                 if (response.status !== 200) { //response status from flask
//                     output.innerText = 'response status code: ' + response.status
//                     return
//                 }
//                 response.json().then(function (data) {
//                     output.innerText = data.message.slice(0,250) //slice if str too long
//                 })
//             })
//     }
//     catch (error) { //doesnt really reach this point
//         console.log('ERROR CATCHED' + error)
//         return
//     }
// }


// document.getElementById("fetchWorkerButton").addEventListener("click", startTimer)
//  MAKE IT STOP FETCHING WHEN NO CONNECTION 

function fetchWorker() {
    output = document.getElementById('fetchWorkerOutput')
    try {
        fetch(window.origin + '/worker', {
            credentials: "include", //cookies etc
            cache: "no-cache",
            headers: new Headers({
                "content-type": "application/json"
            })
        }) //fetch returns async promise, then do something
            .then(function (response) {
                if (response.status !== 200) {
                    console.log('response status not 200: ' + response.status)
                    clearInterval(runningTimer) //TURN OFF THE TIMER IF ERROR
                    return
                }
                response.json().then(function (data) {
                    output.innerText = data
                    console.log(data)
                    if (data === 'TASK ENDED') { //TURN OFF THE TIMER IF DONE
                        clearInterval(runningTimer)
                        return
                    }
                })
            })
    }
    catch (error) { //DOESNT REACH THIS POINT
        console.log('ERROR CATCHED' + error)
        clearInterval(runningTimer) //stops timer - stops sending the requests}
    }
}


function startTimer() {
    //STOP IF ALREADY SET
    if (typeof runningTimer !== 'undefined') {
        clearInterval(runningTimer) //stops timer - stops sending the requests 
    }
    intervalInMiliseconds = 500
    runningTimer = setInterval(fetchWorker, intervalInMiliseconds); //100ms interval
}


document.getElementById("sendFormAndFetchBokehBtn").addEventListener("click", sendFormAndFetchBokeh)


function sendFormAndFetchBokeh(e) {
    e.preventDefault() //prevent sending form default request
    const form = document.getElementById('mainForm')
    var formData = new FormData(form)
    //remove T from datetimes for further processing
    listToRegexp = ['datetimeFirstAbove', 'datetimeFirstBelow', 'datetimeLastAbove', 'datetimeLastBelow']
    listToRegexp.forEach((param) => {
        if (formData.get(param)) {
            oldValue = formData.get(param)
            newValue = oldValue.replace('T', ' ') //replace T with space to fit SQL
            formData.set(param, newValue)
            // console.log(formData.get(param))
        }
    })

    formDataJson = JSON.stringify(Object.fromEntries(formData))
    // console.log(formDataJson)

    fetch(window.origin + '/', {
        method: "POST",
        credentials: "include", //cookies etc
        body: formDataJson,
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }) //fetch returns async promise, then do something
        .then(function (response) {
            if (response.status !== 200) {
                console.log('Error fetching. Response code: ' + response.status)
                return
            }
            else if (response.status == 200) {
                return response.json()
            }
        })
        .then(function (items) { //when response 200 and JSON items list received
            //when no results
            if (items[0] === 'noResultsFound') {
                document.getElementById('plotDiv').innerHTML = 'no data'
                document.getElementById('tableDiv').innerHTML = 'no data'
                document.getElementById('downloadCsv').innerHTML = ''
                document.getElementById('resultsAmount').innerHTML = 'no results ¯\\_(ツ)_/¯'
            }
            //if all went good and results are not empty replace the divs with bokeh stuff
            else if (items[0] && items[1] && items[2]) { //plot, table, and amount of results
                document.getElementById('plotDiv').innerHTML = '' //make div empty first
                document.getElementById('tableDiv').innerHTML = ''
                Bokeh.embed.embed_item(items[0], 'plotDiv')
                Bokeh.embed.embed_item(items[1], 'tableDiv')
                document.getElementById('downloadCsv').innerHTML = 'Download CSV'
                if (items[2] === 1) { //if 1 result
                    document.getElementById('resultsAmount').innerHTML = '1 result'
                }
                else if (items[2] > 1) { // if >1 results
                    document.getElementById('resultsAmount').innerHTML = items[2] + ' results'
                }
            }
        })
}

//CHANGING CHECKBOXES STATE - CHECK/UNCHECK
document.querySelector('.checkUncheckAll').addEventListener('click', (event) => {
    if (document.querySelector('.checkUncheckAll').textContent == 'UNCHECK ALL') {
        document.querySelectorAll('.ckeckBox').forEach(checkbox => { checkbox.checked = false })
        document.querySelector('.checkUncheckAll').textContent = 'CHECK ALL'
    }
    else if (document.querySelector('.checkUncheckAll').textContent == 'CHECK ALL') {
        document.querySelectorAll('.ckeckBox').forEach(checkbox => { checkbox.checked = true })
        document.querySelector('.checkUncheckAll').textContent = 'UNCHECK ALL'
    }
})

}) //onDOMContentLoaded ends here
