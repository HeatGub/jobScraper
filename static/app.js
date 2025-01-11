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

function buttonSwapInnerHtmlStartStop(button) { //because JS requires to return inner func inside outer func to use outer scope
    // console.log('\tbuttonSwapInnerHtmlStartStop')
    if (button.innerHTML === 'START') {
        button.innerHTML = 'STOP'
    }
    else {
        button.innerHTML = 'START'
    }
}

function buttonStateReadyToFetch(button){
    // console.log('\t\tbuttonStateReadyToFetch > button.disabled = ' + button.disabled)
    if (button.innerHTML === 'START') {
        if      (button.disabled === true)  {return true}     // START | disabled
        else if (button.disabled === false) {return false}    // START | enabled
    } else if (button.innerHTML === 'STOP') {
        if      (button.disabled === true)  {return false}    // STOP  | disabled
        else if (button.disabled === false) {return true}     // STOP  | enabled
    }
}

function createNewFullScrapingDiv () {
    const fullScrapingDivsContainer = document.getElementById('fullScrapingDivsContainer')
    const existingFullScrapingDivs = document.querySelectorAll('.fullScrapingDiv div')

    // SET INDEX
    let index = 0 // start indexing with 0
    if (existingFullScrapingDivs.length === 0) {
        // do nothing as index is already declared
    }
    else if (existingFullScrapingDivs.length > 0) {
        const lastElement = existingFullScrapingDivs[existingFullScrapingDivs.length - 1] // last element
        index = Number(lastElement.id.match(/\d+$/)) // regex for numbers at the end
        index += 1
    }
    index = index.toString()

    // DECLARE ELEMENTS
    const fullScrapingDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingDiv'+index, className: 'fullScrapingDiv'})
    const button = Object.assign(document.createElement('button'), {id: 'fullScrapingButton'+index, innerHTML:'START'})
    const input = Object.assign(document.createElement('input'), {id: 'fullScrapingInputUrl'+index, type:'text', value:'https://theprotocol.it/filtry/ai-ml;sp/', placeholder:'url'})
    const output = Object.assign(document.createElement('div'), {id: 'fullScrapingOutput'+index, innerHTML:'output text'})
    const deleteDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingDeleteDiv'+index, className: 'fullScrapingDeleteDiv', innerHTML:'DELETE'})
    const indexDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingIndexDiv'+index, innerHTML: 'index: '+index})

    // APPEND ELEMENTS
    fullScrapingDiv.appendChild(button)
    fullScrapingDiv.appendChild(input)
    fullScrapingDiv.appendChild(output)
    fullScrapingDiv.appendChild(deleteDiv)
    fullScrapingDiv.appendChild(indexDiv)
    fullScrapingDivsContainer.appendChild(fullScrapingDiv)

    function deleteThisFullScrapingDiv() {
        // console.log('deleteDiv index:' + index)
        fullScrapingDiv.remove()
    }

    // ADD EVENT LISTENERS
    button.addEventListener("click", () => { checkButtonStateAndFetchFullScrapingEndpoint(button, 'fullScrapingOutput'+index, 'fullScrapingInputUrl'+index) })
    deleteDiv.addEventListener("click", () => { deleteThisFullScrapingDiv() })
}

createNewFullScrapingDiv()

addNewProcessButton = document.getElementById('addNewProcessButton')
addNewProcessButton.addEventListener("click", () => { createNewFullScrapingDiv()})


function checkButtonStateAndFetchFullScrapingEndpoint (button, outputDiv, inputUrl) {
    const inputUrlDiv = document.getElementById(inputUrl)
    const url =  inputUrlDiv.value
    console.log('<<< BUTTON CLICKED >>> ')
    console.log(url)
    inputUrlDiv.disabled = true
    button.disabled = true // DISABLE BUTTON ON CLICK

    if (buttonStateReadyToFetch(button)) {  // if not don't bother sending a request
        fetchFullScrapingEndpoint()
    }

    function fetchFullScrapingEndpoint() {
        try {
            const output = document.getElementById(outputDiv)
            fetch(window.origin.toString() + '/fullScraping', {
                method: "POST",
                credentials: "include", // cookies etc
                body: JSON.stringify(url),
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
                        if (data.message.includes('SCRAPING DONE. ')) {
                            output.innerText = data.message.slice(0,250)
                            button.innerHTML = 'START'
                            button.disabled = false
                            inputUrlDiv.disabled = false
                            return // EXIT FETCHING IF DONE
                        }
                        else {
                            // RECURRENCE PATH
                            output.innerText = data.message.slice(0,250)
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