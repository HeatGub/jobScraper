document.addEventListener('DOMContentLoaded', () => {

const buttonMessageStart = 'START'
const buttonMessagePause = 'PAUSE'
const checkAllText = '✓'
const uncheckAllText = '✗'
const sliceMessageToThisAmountOfCharacters = 350

// CHANGE CALENDAR TOOL FOR FLATPICKR - styling in CSS file
flatpickr("input[type='datetime-local']", {
    enableTime: true, // show hh:mm options
    enableSeconds: true,
    dateFormat: "Y-m-d H:i:S",
    allowInput: true, // Allow manual typing in the input field
    time_24hr: true,
    minuteIncrement: 1,

    onOpen: function(selectedDates, dateStr, instance) { // dateStr empty but required
        if (selectedDates.length === 0) { // update input if empty
            instance.setDate(new Date())
        }
    }
})

fetchProcesses() // HAS TO STAY AT THE TOP TO FETCH PROCESSES FIRST

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

document.getElementById("openBrowserButton").addEventListener("click", () => { fetchEndpointAndAwaitResponse('openBrowser', 'openBrowserOutput') })
document.getElementById("saveCookiesToJsonButton").addEventListener("click", () => { fetchEndpointAndAwaitResponse('saveCookiesToJson', 'saveCookiesToJsonOutput') })

function fetchEndpointAndAwaitResponse (endpoint, outputDiv) {
    const output = document.getElementById(outputDiv)
    output.innerText = 'working...'
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
        // url = "https://justjoin.it/job-offers/bialystok?experience-level=mid&remote=yes&orderBy=DESC&sortBy=published"
        url = "https://theprotocol.it/filtry/python;t/junior;p/zdalna;rw"
        // url =''
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
    const fullScrapingDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingDiv_'+index, className: 'fullScrapingDiv flexCentered flexDirectionColumn'})
    const button = Object.assign(document.createElement('button'), {id: 'fullScrapingButton_'+index, className:'disabledTextSelection', innerHTML:buttonMessageStart})
    const input = Object.assign(document.createElement('input'), {id: 'fullScrapingInputUrl_'+index, spellcheck:false, type:'text', value:url, placeholder:'https://theprotocol.it/filtry/python;t/...'})
    const output = Object.assign(document.createElement('div'), {id: 'fullScrapingOutput_'+index, className: 'fullScrapingDivOutput', innerHTML:lastMessage.slice(0,sliceMessageToThisAmountOfCharacters)})
    const deleteDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingDeleteDiv_'+index, className: 'fullScrapingDeleteDiv', innerHTML:'<i class="fa fa-trash-o"></i>'})
    // const indexDiv = Object.assign(document.createElement('div'), {id: 'fullScrapingIndexDiv_'+index, innerHTML: 'index: '+index})

    // APPEND ELEMENTS
    fullScrapingDiv.appendChild(input)
    fullScrapingDiv.appendChild(button)
    fullScrapingDiv.appendChild(output)
    fullScrapingDiv.appendChild(deleteDiv)
    // fullScrapingDiv.appendChild(indexDiv)
    fullScrapingDivsContainer.appendChild(fullScrapingDiv)

    // DECLARE INSIDE TO USE OUTER FUNCITON'S VARIABLES
    function fetchKillProcessIfExistsEndpoint() {
        output.innerHTML = 'working...'
        const url = input.value
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
                        // console.log('fetchKillProcessIfExistsEndpoint response status not 200: ' + response.status)
                        return //EXIT on error
                    }
                    response.json().then(function (data) {
                        // console.log(data.message)
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
            // console.log('JS ERROR CATCHED ' + error)
            return //EXIT on error
        }
    }

    // ADD EVENT LISTENERS
    button.addEventListener("click", () => { checkButtonStateAndFetchFullScrapingEndpointRecursively(button, 'fullScrapingOutput_'+index, 'fullScrapingInputUrl_'+index) })
    deleteDiv.addEventListener("click", () => { fetchKillProcessIfExistsEndpoint() })
} // createNewFullScrapingDiv ends here

addNewProcessButton = document.getElementById('addNewProcessButton')
addNewProcessButton.addEventListener("click", () => { createNewFullScrapingDiv()})

// CHECK BUTTON STATE AND FETCH FULL SCRAPING ENDPOINT RECURSIVELY
function checkButtonStateAndFetchFullScrapingEndpointRecursively (button, outputDiv, inputUrl) {
    // console.log('<<< BUTTON CLICKED >>> ')
    const output = document.getElementById(outputDiv)
    const inputUrlDiv = document.getElementById(inputUrl)
    const url =  inputUrlDiv.value
    const divIndex = Number(inputUrlDiv.id.match(/\d+$/)) // regex for numbers at the end of line

    output.innerText = 'working...'

    function isUrlValid(url) {
        try {
          const parsedUrl = new URL(url);
          // Validate the scheme is either http or https
          return /^(http|https):$/.test(parsedUrl.protocol);
        } catch (e) {
          return false;
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
                        // console.log('response status not 200: ' + response.status)
                        return //EXIT on error
                    }
                    response.json().then(function (data) {
                        output.style = 'color: var(--color-text-primary);' // usual color, could change on pause
                        // EXIT RECURRENCE PATH
                        if (data.killProcess === true) {
                            // KILL PROCESS
                            output.innerText = data.message.slice(0,sliceMessageToThisAmountOfCharacters)
                            button.innerHTML = buttonMessageStart
                            button.disabled = false
                            button.classList.remove('button-working-state')
                            inputUrlDiv.disabled = false
                            return // EXIT FETCHING
                        }
                        else if (data.pauseProcess === true) {
                            // PAUSE PROCESS - USUALLY BOT CHECK TRIGGERED
                            output.style = 'color: var(--color-text-warning);'
                            output.innerText = data.message.slice(0,sliceMessageToThisAmountOfCharacters)
                            button.innerHTML = buttonMessageStart
                            button.disabled = false
                            button.classList.remove('button-working-state')
                            // alert(data.message.slice(0,sliceMessageToThisAmountOfCharacters))
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
            // console.log('JS error catched ' + error) // never happened yet
            return //EXIT on error
        }
    }
}

// SEND FORM AND FETCH BOKEH
document.getElementById("sendFormAndFetchBokehButton").addEventListener("click", sendFormAndFetchBokeh)

function sendFormAndFetchBokeh(e) {
    document.getElementById('sendFormAndFetchBokehOutput').innerHTML = 'loading...' //reset output
    e.preventDefault() //prevent sending form default request

    if (atLeastOneCheckboxChecked() === false) {
        document.getElementById('sendFormAndFetchBokehOutput').innerHTML = 'select at least one parameter to show'
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
                // console.log('Error fetching. Response code: ' + response.status)
                return
            }
            else if (response.status == 200) {
                return response.json()
            }
        })
        .then(function (items) { // when response 200 and JSON items list received
            const queryDiv = document.getElementById('queryDiv')
            queryDiv.display = 'flex'
            queryDiv.innerHTML = items.query.replace(/\n/g, "<br>") //replace python newline with html <br>
            queryDiv.style = 'color: var(--color-text-primary);'
            // queryDiv.style.display = 'none'
            if (items.error === true){
                // queryDiv.style.display = 'flex'
                queryDiv.style = 'color: var(--color-text-warning);'
                document.getElementById('sendFormAndFetchBokehOutput').innerHTML = 'query error - check description'
            }

            if (items.resultsAmount === 0) {
                document.getElementById('plotDiv').innerHTML = ''
                document.getElementById('tableDiv').innerHTML = ''
                document.getElementById('downloadCsvContainer').style.display = 'none'
                document.getElementById('downloadCsvIcon').innerHTML = ''
                document.getElementById('downloadCsvText').innerHTML = ''
                document.getElementById('resultsAmount').innerHTML = '' //'no results ¯\\_(ツ)_/¯'
                if (items.error != true) {
                    document.getElementById('sendFormAndFetchBokehOutput').innerHTML = 'no results ¯\\_(ツ)_/¯'
                }
                return
            }
            // if all went good and results are not empty replace the divs with bokeh stuff
            else if (items.resultsAmount >= 1) {
                document.getElementById('plotDiv').innerHTML = '' //make div empty first
                document.getElementById('tableDiv').innerHTML = ''
                Bokeh.embed.embed_item(items.plot, 'plotDiv')
                Bokeh.embed.embed_item(items.table, 'tableDiv')
                document.getElementById('downloadCsvContainer').style.display = 'flex'
                document.getElementById('downloadCsvIcon').innerHTML = '<i class="fa fa-download" aria-hidden="true"></i>'
                document.getElementById('downloadCsvText').innerHTML = 'DOWNLOAD CSV'

                if (items.resultsAmount === 1) { //if 1 result
                    document.getElementById('resultsAmount').innerHTML = '1 result'
                    document.getElementById('sendFormAndFetchBokehOutput').innerHTML = '1 result'
                }
                else if (items.resultsAmount > 1) { // if >1 results
                    document.getElementById('resultsAmount').innerHTML = items.resultsAmount + ' results'
                    document.getElementById('sendFormAndFetchBokehOutput').innerHTML = items.resultsAmount + ' results'
                }
            }
        })
}

// BUTTON INNER HTML
function buttonSwapInnerHtmlStartStop(button) { //because JS requires to return inner func inside outer func to use outer scope
    // console.log('\tbuttonSwapInnerHtmlStartStop')
    if (button.innerHTML === buttonMessageStart) {
        button.innerHTML = buttonMessagePause
        button.className = 'button-working-state'
    }
    else {
        button.innerHTML = buttonMessageStart
        button.classList.remove('button-working-state')
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
    document.querySelectorAll('.checkBox').forEach(checkbox => {
        if (checkbox.checked === true) {checkboxesChecked += 1}
    })
    if (checkboxesChecked > 0) {return true}
    else {return false} //if not checked
}

// CHANGING CHECKBOXES STATE - CHECK/UNCHECK
document.getElementById('checkUncheckAll').addEventListener('click', () => {
    const checkUncheckAll = document.getElementById('checkUncheckAll')
    // The HTML entity &check; is converted into the Unicode character ✓ by the browser when the page is rendered
    if (checkUncheckAll.textContent == uncheckAllText) {
        document.querySelectorAll('.checkBox').forEach(checkbox => { checkbox.checked = false })
        checkUncheckAll.textContent = checkAllText
        checkUncheckAll.style = 'color: var(--color-secondary);' // root variable
    }
    else if (checkUncheckAll.textContent == checkAllText) {
        document.querySelectorAll('.checkBox').forEach(checkbox => { checkbox.checked = true })
        checkUncheckAll.textContent = uncheckAllText
        checkUncheckAll.style = 'color: var(--color-primary);'
    }
})

// MAKE WHOLE DOWNLOAD CSV CONTAINER CLICKABLE
document.getElementById('downloadCsvContainer').addEventListener('click', function() {
    let url = window.origin.toString() + "/downloadCsv"
    window.location.href = url
})

// HIDE / SHOW CATEGORIES
document.querySelectorAll('.categoryShowHideDiv').forEach(hideShowDiv => {
    hideShowDiv.addEventListener('click', () => {
        // Find the associated categoryContent sibling
        const content = hideShowDiv.nextElementSibling
        // Toggle the display property
        if (content.style.display === 'flex' || content.style.display === 'block') {
            content.style.display = 'none'
        } else if (content.style.display === 'none') {
            if (content.className === 'categoryContentBokeh') {
                content.style.display = 'block' // bokeh doesn't accept flex display
            }
            else { // content.className === 'categoryContent'
                content.style.display = 'flex'
            }
        }
    })
})

// CHANGE HEADER TEXT CONTENT ON MOUSEOVER
headerContainer = document.getElementById("headerContainer")

headerContainer.addEventListener("mouseover", function() {
    headerText2.textContent = "so much crap"
})
headerContainer.addEventListener("mouseout", function() {
    headerText2.textContent = "so much scrap";
})


// function printAllRootVariables() {
//     function getAllCSSVariableNames(styleSheets = document.styleSheets){
//         var cssVars = [];
//         // loop each stylesheet
//         for(var i = 0; i < styleSheets.length; i++){
//         // loop stylesheet's cssRules
//         try{ // try/catch used because 'hasOwnProperty' doesn't work
//             for( var j = 0; j < styleSheets[i].cssRules.length; j++){
//                 try{
//                     // loop stylesheet's cssRules' style (property names)
//                     for(var k = 0; k < styleSheets[i].cssRules[j].style.length; k++){
//                     let name = styleSheets[i].cssRules[j].style[k];
//                     // test name for css variable signiture and uniqueness
//                     if(name.startsWith('--') && cssVars.indexOf(name) == -1){
//                         cssVars.push(name);
//                     }
//                     }
//                 } catch (error) {}
//             }
//         } catch (error) {}
//         }
//         return cssVars;
//     }
    
//     function getElementCSSVariables (allCSSVars, element = document.body, pseudo){
//         var elStyles = window.getComputedStyle(element, pseudo);
//         var cssVars = {};
//         for(var i = 0; i < allCSSVars.length; i++){
//         let key = allCSSVars[i];
//         let value = elStyles.getPropertyValue(key)
//         if(value){cssVars[key] = value;}
//         }
//         return cssVars;
//     }
    
//     var cssVars = getAllCSSVariableNames();
//     console.log(':root variables', getElementCSSVariables(cssVars, document.documentElement));
// }
// printAllRootVariables()

}) //onDOMContentLoaded ends here