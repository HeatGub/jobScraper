document.addEventListener('DOMContentLoaded', () => {

document.getElementById("openBrowserButton").addEventListener("click", () => { fetchEndpointAndAwaitResponse('openBrowser', 'openBrowserOutput') })
document.getElementById("saveCookiesToJsonButton").addEventListener("click", () => { fetchEndpointAndAwaitResponse('saveCookiesToJson', 'saveCookiesToJsonOutput') })

function fetchEndpointAndAwaitResponse (endpoint, outputDiv) { //event just for the need of .bind()
    const output = document.getElementById(outputDiv)
    try {
        let url = window.origin.toString() + "/" + endpoint.toString()
        fetch( url, {
            cache: "no-cache",
        }) // FETCH RETURNS ASYNC PROMISE AND AWAITS RESPONSE
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
    catch (error) {
        console.log('JS ERROR CATCHED' + error)
        return
    }
}

const fullScrapingButton = document.getElementById("fullScrapingButton")
fullScrapingButton.addEventListener("click", checkButtonStateAndFetchFullScrapingEndpoint)

function buttonSwapInnerHtmlStartStop() { //because JS requires to return inner func inside outer func to use outer scope
    // console.log('\tbuttonSwapInnerHtmlStartStop')
    if (fullScrapingButton.innerHTML === 'START') {
        fullScrapingButton.innerHTML = 'STOP'
    }
    else {
        fullScrapingButton.innerHTML = 'START'
    }
}

function buttonStateReadyToFetch(){
    // console.log('\t\tbuttonStateReadyToFetch > fullScrapingButton.disabled = ' + fullScrapingButton.disabled)
    if (fullScrapingButton.innerHTML === 'START') {
        if      (fullScrapingButton.disabled === true)  {return true}     // START | disabled
        else if (fullScrapingButton.disabled === false) {return false}    // START | enabled
    } else if (fullScrapingButton.innerHTML === 'STOP') {
        if      (fullScrapingButton.disabled === true)  {return false}    // STOP  | disabled
        else if (fullScrapingButton.disabled === false) {return true}     // STOP  | enabled
    }
}

function checkButtonStateAndFetchFullScrapingEndpoint () {
    console.log('<<< BUTTON CLICKED >>>')
    fullScrapingButton.disabled = true // DISABLE BUTTON ON CLICK

    fetchFullScrapingEndpoint()

    function fetchFullScrapingEndpoint() {
        // console.log('\tfetchFullScrapingEndpoint')
        try {
            if (buttonStateReadyToFetch()) {
            const output = document.getElementById('fullScrapingOutput')
            fetch(window.origin + '/fullScraping', {
                credentials: "include", //cookies etc
                cache: "no-cache",
                headers: new Headers({
                    "content-type": "application/json"
                })
            }) // FETCH RETURNS ASYNC PROMISE AND AWAITS RESPONSE
                .then(function (response) {
                    console.log('RESPONSE RECEIVED')
                    if (response.status !== 200) {
                        console.log('response status not 200: ' + response.status)
                        return //EXIT on error
                    }
                    response.json().then(function (data) {
                        console.log(data.message)
                        if (data.message.includes('SCRAPING DONE. ')) { 
                            output.innerText = data.message.slice(0,250)
                            fullScrapingButton.innerHTML = 'START'
                            fullScrapingButton.disabled = false
                            return // EXIT FETCHING IF DONE
                        }
                        else {
                            // RECURRENCE PATH
                            output.innerText = data.message.slice(0,250)
                            console.log('\tRECURRENCE CHECK > buttonStateReadyToFetch = ' + buttonStateReadyToFetch())
                            if (buttonStateReadyToFetch()) {
                                console.log('\t<<< RECURRENCE CALL >>> \n\tbuttonStateReadyToFetch === true')
                                fetchFullScrapingEndpoint() // RECURRENCE IF NOT PAUSED OR NOT DONE YET
                                // fullScrapingButton.disabled = false // enable button
                            }
                            if (fullScrapingButton.disabled === true) { //CHANGE BUTTON AS IT'S ALREADY AFTER STATE CHECK buttonStateReadyToFetch()
                                buttonSwapInnerHtmlStartStop()
                                fullScrapingButton.disabled = false 
                            }
                        }
                    })
                })
            }
        }
        catch (error) {
            console.log('JS ERROR CATCHED' + error)
            return //EXIT on error
        }
    }
}

// SEND FORM AND FETCH BOKEH
document.getElementById("sendFormAndFetchBokehButton").addEventListener("click", sendFormAndFetchBokeh)

function sendFormAndFetchBokeh(e) {
    e.preventDefault() //prevent sending form default request
    const form = document.getElementById('mainForm')
    let formData = new FormData(form)
    //remove T from datetimes for further processing
    const listToRegexp = ['datetimeFirstAbove', 'datetimeFirstBelow', 'datetimeLastAbove', 'datetimeLastBelow']
    listToRegexp.forEach((param) => {
        if (formData.get(param)) {
            oldValue = formData.get(param)
            newValue = oldValue.replace('T', ' ') //replace T with space to fit SQL
            formData.set(param, newValue)
            // console.log(formData.get(param))
        }
    })
    let formDataJson = JSON.stringify(Object.fromEntries(formData))
    // console.log(formDataJson)

    fetch(window.origin + '/', {
        method: "POST",
        credentials: "include", // cookies etc
        body: formDataJson, // form results
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    }) // FETCH RETURNS ASYNC PROMISE AND AWAITS RESPONSE
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

// CHANGING CHECKBOXES STATE - CHECK/UNCHECK
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