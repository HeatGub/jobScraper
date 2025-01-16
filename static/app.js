document.addEventListener('DOMContentLoaded', () => {

const buttonMessageStart = 'START'
const buttonMessagePause = 'PAUSE'
const sliceMessageToThisAmountOfCharacters = 250

fetchProcesses() // HAS TO STAY AT THE TOP TO FETCH PROCESSES FIRST

document.getElementById("openBrowserButton").addEventListener("click", () => { fetchEndpointAndAwaitResponse('openBrowser', 'openBrowserOutput') })
document.getElementById("saveCookiesToJsonButton").addEventListener("click", () => { fetchEndpointAndAwaitResponse('saveCookiesToJson', 'saveCookiesToJsonOutput') })

function fetchProcesses() {
    // const output = document.getElementById(outputDiv)
    try {
        let url = window.origin.toString() + "/getProcesses"
        fetch( url, {
            cache: "no-cache",
        }) // FETCH RETURNS ASYNC PROMISE AND AWAITS RESPONSE
            .then(function (response) {
                if (response.status !== 200) { //response status from flask
                    output.innerText = 'response status code: ' + response.status + '. Check python console for more info'
                    return
                }
                response.json().then(function (processesList) {
                    if (processesList.length === 0) {
                        createNewFullScrapingDiv()  // no arguments provided, just a div ready to start
                        return
                    }
                    // console.log(data)
                    processesList.forEach((process) => {
                        // console.log(process.divIndex, process.url)
                        createNewFullScrapingDiv(process.url, process.divIndex, process.lastMessage)
                    })
                    return
                })
            })
    }
    catch (error) {
        console.log('JS ERROR CATCHED' + error)
        return
    }
}

function fetchEndpointAndAwaitResponse (endpoint, outputDiv) {
    const output = document.getElementById(outputDiv)
    try {
        let url = window.origin.toString() + "/" + endpoint.toString()
        fetch( url, {
            cache: "no-cache",
        }) // FETCH RETURNS ASYNC PROMISE AND AWAITS RESPONSE
            .then(function (response) {
                if (response.status !== 200) { //response status from flask
                    output.innerText = 'response status code: ' + response.status + '. Check python console for more info'
                    return
                }
                response.json().then(function (data) {
                    output.innerText = data.message.slice(0,sliceMessageToThisAmountOfCharacters) //slice if str too long
                })
            })
    }
    catch (error) {
        console.log('JS ERROR CATCHED' + error)
        return
    }
}

function createNewFullScrapingDiv (url, index, lastMessage) {
    const fullScrapingDivsContainer = document.getElementById('fullScrapingDivsContainer')
    const existingFullScrapingDivs = document.querySelectorAll('.fullScrapingDiv div')

    // HANDLING UNDEFINED ARGUMENTS
    if (url === undefined) { // IF URL ARGUMENT NOT PROVIDED
        url = "https://theprotocol.it/filtry/ai-ml;sp/"
    }
    if (index === undefined) { // IF INDEX ARGUMENT NOT PROVIDED
        index = 0 // start indexing with 0
        if (existingFullScrapingDivs.length === 0) {
            // do nothing as index is already declared
        }
        else if (existingFullScrapingDivs.length > 0) {
            const lastElement = existingFullScrapingDivs[existingFullScrapingDivs.length - 1] // last element
            index = Number(lastElement.id.match(/\d+$/)) // regex for numbers at the end of line
            index += 1
        }
    }
    index = index.toString()
    if (lastMessage === undefined) { // IF LAST MESSAGE ARGUMENT NOT PROVIDED
        lastMessage = 'ready to start'
    }

    // DECLARE ELEMENTS
    const fullScrapingDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingDiv_'+index, className: 'fullScrapingDiv'})
    const button = Object.assign(document.createElement('button'), {id: 'fullScrapingButton_'+index, innerHTML:buttonMessageStart})
    const input = Object.assign(document.createElement('input'), {id: 'fullScrapingInputUrl_'+index, type:'text', value:url, placeholder:'url'})
    const output = Object.assign(document.createElement('div'), {id: 'fullScrapingOutput_'+index, innerHTML:lastMessage})
    const deleteDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingDeleteDiv_'+index, className: 'fullScrapingDeleteDiv', innerHTML:'DELETE'})
    const indexDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingIndexDiv_'+index, innerHTML: 'index: '+index})

    // APPEND ELEMENTS
    fullScrapingDiv.appendChild(button)
    fullScrapingDiv.appendChild(input)
    fullScrapingDiv.appendChild(output)
    fullScrapingDiv.appendChild(deleteDiv)
    fullScrapingDiv.appendChild(indexDiv)
    fullScrapingDivsContainer.appendChild(fullScrapingDiv)

    // DECLARE INSIDE TO USE OUTER FUNCITON'S VARIABLES
    function fetchKillProcessIfExistsEndpoint() {
        const url = input.value
        console.log('fetchKillProcessIfExistsEndpoint')
        console.log(url)
        try {
            fetch(window.origin.toString() + '/killProcessIfExists', {
                method: "POST",
                credentials: "include", // cookies etc
                body: JSON.stringify({url:url, divIndex:index}),
                cache: "no-cache",
                headers: new Headers({"content-type": "application/json"})
            }) // FETCH RETURNS ASYNC PROMISE AND AWAITS RESPONSE
                .then(function (response) {
                    // console.log('RESPONSE RECEIVED')
                    if (response.status !== 200) {
                        console.log('fetchKillProcessIfExistsEndpoint response status not 200: ' + response.status)
                        return //EXIT on error
                    }
                    response.json().then(function (data) {
                        console.log(data.message)
                        if (data.success === true) {
                            fullScrapingDiv.remove()
                            // PROCESS KILLED
                            return
                        }
                        else if (data.success === false) {
                            output.innerText = data.message.slice(0,sliceMessageToThisAmountOfCharacters)
                            return
                        }
                    })
                })
        }
        catch (error) {
            console.log('JS ERROR CATCHED ' + error)
            return //EXIT on error
        }
    }

    // ADD EVENT LISTENERS
    button.addEventListener("click", () => { checkButtonStateAndFetchFullScrapingEndpointRecursively(button, 'fullScrapingOutput_'+index, 'fullScrapingInputUrl_'+index) })
    deleteDiv.addEventListener("click", () => { fetchKillProcessIfExistsEndpoint() })
}

addNewProcessButton = document.getElementById('addNewProcessButton')
addNewProcessButton.addEventListener("click", () => { createNewFullScrapingDiv()})

// CHECK BUTTON STATE AND FETCH FULL SCRAPING ENDPOINT RECURSIVELY
function checkButtonStateAndFetchFullScrapingEndpointRecursively (button, outputDiv, inputUrl) {
    console.log('<<< BUTTON CLICKED >>> ')
    const output = document.getElementById(outputDiv)
    const inputUrlDiv = document.getElementById(inputUrl)
    const url =  inputUrlDiv.value
    const divIndex = Number(inputUrlDiv.id.match(/\d+$/)) // regex for numbers at the end of line

    function isUrlValid(url) {
        try {
          new URL(url)
          return true
        } catch (e) {
          return false
        }
    }

    // CHECK IF URL VALID FIRST
    if (isUrlValid(url) === false) {
        output.innerText = 'invalid URL. Use full address like https://theprotocol.it/filtry/ai-ml;sp/'
        return // exit
    }

    inputUrlDiv.disabled = true
    button.disabled = true // DISABLE BUTTON ON CLICK

    if (buttonStateReadyToFetch(button)) {  // if not don't bother sending a request
        fetchFullScrapingEndpoint()
    }

    function fetchFullScrapingEndpoint() {
        try {
            fetch(window.origin.toString() + '/fullScraping', {
                method: "POST",
                credentials: "include", // cookies etc
                body: JSON.stringify({url:url, divIndex:divIndex}),
                cache: "no-cache",
                headers: new Headers({"content-type": "application/json"})
            }) // FETCH RETURNS ASYNC PROMISE AND AWAITS RESPONSE
                .then(function (response) {
                    // console.log('RESPONSE RECEIVED')
                    if (response.status !== 200) {
                        console.log('response status not 200: ' + response.status)
                        return //EXIT on error
                    }
                    response.json().then(function (data) {
                        console.log(data.message)
                        if (data.message.includes('SCRAPING DONE. ') | data.message.includes('process for that URL already exists')) {
                            // EXIT RECURRENCE WHEN THAT PHRASES ARE FOUND
                            output.innerText = data.message.slice(0,sliceMessageToThisAmountOfCharacters)
                            button.innerHTML = buttonMessageStart
                            button.disabled = false
                            inputUrlDiv.disabled = false
                            return // EXIT FETCHING
                        }
                        else {
                            // RECURRENCE PATH
                            output.innerText = data.message.slice(0,sliceMessageToThisAmountOfCharacters)
                            // console.log('\tRECURRENCE CHECK > buttonStateReadyToFetch = ' + buttonStateReadyToFetch())
                            if (buttonStateReadyToFetch(button)) {
                                // console.log('\t<<< RECURRENCE CALL >>> \n\tbuttonStateReadyToFetch === true')
                                fetchFullScrapingEndpoint() // RECURRENCE IF NOT PAUSED OR NOT DONE YET
                            }
                            if (button.disabled === true) { //CHANGE BUTTON AS IT'S ALREADY AFTER STATE CHECK buttonStateReadyToFetch()
                                buttonSwapInnerHtmlStartStop(button)
                                button.disabled = false
                            }
                        }
                    })
                })
        }
        catch (error) {
            console.log('JS ERROR CATCHED ' + error)
            return //EXIT on error
        }
    }
}

// SEND FORM AND FETCH BOKEH
document.getElementById("sendFormAndFetchBokehButton").addEventListener("click", sendFormAndFetchBokeh)

function sendFormAndFetchBokeh(e) {
    document.getElementById('sendFormAndFetchBokehOutput').innerHTML = '' //reset output
    e.preventDefault() //prevent sending form default request

    if (atLeastOneCheckboxChecked() === false) {
        document.getElementById('sendFormAndFetchBokehOutput').innerHTML = 'select at least one column to display'
        return //exit
    }

    const form = document.getElementById('mainForm')
    let formData = new FormData(form)
    //remove T from datetimes for further processing
    const listToRegexp = ['datetimeFirstAbove', 'datetimeFirstBelow', 'datetimeLastAbove', 'datetimeLastBelow']
    listToRegexp.forEach((param) => {
        if (formData.get(param)) {
            oldValue = formData.get(param)
            newValue = oldValue.replace('T', ' ') //replace T with space to fit SQL
            formData.set(param, newValue)
        }
    })
    let formDataJson = JSON.stringify(Object.fromEntries(formData))

    fetch(window.origin + '/', {
        method: "POST",
        credentials: "include", // cookies etc
        body: formDataJson, // form results
        cache: "no-cache",
        headers: new Headers({"content-type": "application/json"})
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
        .then(function (items) { // when response 200 and JSON items list received
            document.getElementById('queryDiv').innerHTML = items.query.replace(/\n/g, "<br>") //replace python newline with html <br>

            if (items.resultsAmount === 0) {
                document.getElementById('plotDiv').innerHTML = 'no data'
                document.getElementById('tableDiv').innerHTML = 'no data'
                document.getElementById('downloadCsv').innerHTML = ''
                document.getElementById('resultsAmount').innerHTML = 'no results ¯\\_(ツ)_/¯'
                return
            }
            // if all went good and results are not empty replace the divs with bokeh stuff
            else if (items.resultsAmount >= 1) {
                document.getElementById('plotDiv').innerHTML = '' //make div empty first
                document.getElementById('tableDiv').innerHTML = ''
                Bokeh.embed.embed_item(items.plot, 'plotDiv')
                Bokeh.embed.embed_item(items.table, 'tableDiv')
                document.getElementById('downloadCsv').innerHTML = 'Download CSV'

                if (items.resultsAmount === 1) { //if 1 result
                    document.getElementById('resultsAmount').innerHTML = '1 result'
                }
                else if (items.resultsAmount > 1) { // if >1 results
                    document.getElementById('resultsAmount').innerHTML = items.resultsAmount + ' results'
                }
            }
        })
}

// BUTTON INNER HTML
function buttonSwapInnerHtmlStartStop(button) { //because JS requires to return inner func inside outer func to use outer scope
    // console.log('\tbuttonSwapInnerHtmlStartStop')
    if (button.innerHTML === buttonMessageStart) {
        button.innerHTML = buttonMessagePause
    }
    else {
        button.innerHTML = buttonMessageStart
    }
}

// CHECK BUTTON STATE
function buttonStateReadyToFetch(button){
    // console.log('\t\tbuttonStateReadyToFetch > button.disabled = ' + button.disabled)
    if (button.innerHTML === buttonMessageStart) {
        if      (button.disabled === true)  {return true}     // START | disabled
        else if (button.disabled === false) {return false}    // START | enabled
    } else if (button.innerHTML === buttonMessagePause) {
        if      (button.disabled === true)  {return false}    // STOP  | disabled
        else if (button.disabled === false) {return true}     // STOP  | enabled
    }
}

// AT LEAST 1 CHECKBOX HAS TO BE CHECKED
function atLeastOneCheckboxChecked () {
    checkboxesChecked = 0
    document.querySelectorAll('.ckeckBox').forEach(checkbox => {
        if (checkbox.checked === true) {checkboxesChecked += 1}
    })
    if (checkboxesChecked > 0) {return true}
    else {return false} //if not checked
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