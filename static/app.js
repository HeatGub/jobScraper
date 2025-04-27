document.addEventListener('DOMContentLoaded', () => {

// GENERAL CONSTS
const buttonMessageStart = 'START'
const buttonMessagePause = 'PAUSE'
const checkAllText = '✓'
const uncheckAllText = '✗'
const sliceMessageToThisAmountOfCharacters = 350

// QUERY EDITOR FUNCTIONALITY
const queryHistoryRecordsLimit = 100 // list of last executed queries
const queryUndoMaxHistoryLength = 200 // ctrl + z list
const queryUndoStack = [] // ctrl + z
const queryRedoStack = [] // ctrl + y
const queryAutoBatchTimeout = 500 // time in ms to group changes together
let queryLastSaveTime = 0
let queryEditorHistory = JSON.parse(localStorage.getItem('queryEditorHistory') || '[]')
let historyIndex = Math.max(0, queryEditorHistory.length - 1)
// console.log(historyIndex)

fetchProcesses() // FETCH EXISTING PROCESSES


// ================================================================================ HIGHLIGHT SQL SYNTAX IN QUERY EDITOR


const queryEditor = document.getElementById('queryEditor')
const executeQueryOutput = document.getElementById('executeQueryOutput')
const executeQueryButton = document.getElementById('executeQueryButton')

const SQL_CORE_KEYWORDS = ['SELECT', 'FROM', 'WHERE', 'LIKE', 'INSERT', 'INTO', 'VALUES', 'UPDATE', 'SET', 'DELETE', 'CREATE', 'DROP', 'TABLE', 
    'VIEW', 'INDEX', 'IF', 'EXISTS', 'DISTINCT', 'ALL', 'IN', 'IS', 'NOT', 'NULL', 'AS', 'AND', 'OR', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END', 
    'GROUP', 'BY', 'ORDER', 'HAVING', 'LIMIT', 'OFFSET', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'CROSS', 'ON', 'USING', 'UNION', 
    'INTERSECT', 'EXCEPT', 'INTEGER', 'TEXT', 'BLOB', 'REAL', 'NUMERIC', 'BOOLEAN', 'DATETIME', 'VARCHAR', 'CHAR', 'ASC', 'DESC']

const SQL_FUNCTIONS_KEYWORDS = ['JULIANDAY', 'DATE', 'TIME', 'DATETIME', 'STRFTIME', 'ABS', 'ROUND', 'LENGTH', 'LOWER', 'UPPER', 'TRIM', 'COALESCE', 'IFNULL', 'NULLIF', 
    'RANDOM', 'RANDOMBLOB', 'TOTAL', 'SUM', 'AVG', 'MIN', 'MAX', 'COUNT']
    
// const SQL_SPECIAL_CHARACTERS = ['[', ']', '(', ')', '+', '-', '/', '*']
const SQL_SPECIAL_CHARACTERS = ['(', ')']

function highlightQuerySyntax(text) {
    // console.log(text)
    const escapeHTML = str => str.replace(/</g, "&lt;").replace(/>/g, "&gt;")
    // const tokens = text.match(/"[^"]*"|'[^']*'|\[.*\]|\s\d+\s|\w+|\n|\s|--|[^\s]/g) // divide text into 'tokens'
    const tokens = text.match(/"[^"]*"|'[^']*'|\[.*\]|\w+|\d+|\n|\s|--|[^\s]/g) // divide text into 'tokens'

    let commentModeOn = false
    // when encountered '--' return comment span until <br> hit (boolean var)
    const highlighted = tokens.map(token => {
        // console.log('token: ' + token)
        if (/^\n$/.test(token)) {
            commentModeOn = false // turn off comment mode on a newline
            return '<br>'
        }
        // check comment mode status
        if (commentModeOn === true){
            return `<span class="queryTextComment">${token}</span>`
        }
        // turning on comment mode on '--'
        else if (/--.*/.test(token)) {
            commentModeOn = true 
            return `<span class="queryTextComment">${token}</span>`
        }
        else if (SQL_CORE_KEYWORDS.includes(token.toUpperCase())) {
            return `<span class="queryCoreKeyword">${token}</span>`
        }
        else if (SQL_FUNCTIONS_KEYWORDS.includes(token.toUpperCase())) {
            return `<span class="queryFunctionKeyword">${token}</span>`
        }
        else if (SQL_SPECIAL_CHARACTERS.includes(token)) {
            return `<span class="querySpecialCharacter">${token}</span>`
        } 
        // else if (/^\'.*?\'$/.test(token) || /^\".*?\"$/.test(token)) {
        else if (/^\'.*?\'$/.test(token) || /^\".*?\"$/.test(token) || /^\[.*?\]$/.test(token)) {
            return `<span class="queryTextString">${token}</span>`
        }
        else if (/^\d+$/.test(token)) {
            return `<span class="queryTextNumber">${token}</span>`
        }
        else {
            return escapeHTML(token);
        }
    })
    .join("")
    return highlighted
}

function preserveCaret(callback) { // because highlighting moves caret back to beginning 
    // function preserveCaret() {
    const selection = window.getSelection()
    const range = selection.getRangeAt(0)
    const preCaretRange = range.cloneRange()
    preCaretRange.selectNodeContents(queryEditor)
    preCaretRange.setEnd(range.endContainer, range.endOffset)
    const caretOffset = preCaretRange.toString().length

    // Restore caret
    function setCaret(node, offset) {
        const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null)
        
        let pos = 0
        let foundNode = null
        let foundOffset = 0

        while (walker.nextNode()) {
            const textNode = walker.currentNode
            const nextPos = pos + textNode.length
            // console.log(textNode, nextPos)

            if (nextPos >= offset) {
                foundNode = textNode
                // console.log('foundNode')
                // console.log(foundNode)
                foundOffset = offset - pos
                break
            }
            pos = nextPos
        }

        if (foundNode) {
            const newRange = document.createRange()
            newRange.setStart(foundNode, foundOffset)
            newRange.setEnd(foundNode, foundOffset)
            const sel = window.getSelection()
            sel.removeAllRanges()
            sel.addRange(newRange)
        }
    }
    callback() // highlightQuerySyntax() - modifying queryEditor.innerHTML resets caret position
    setCaret(queryEditor, caretOffset)
}

// Highlight and save undo/redo content as you type
queryEditor.addEventListener('input', () => {
    saveQuerySnapshot()
    preserveCaret(() => {
    const text = queryEditor.innerText
    queryEditor.innerHTML = highlightQuerySyntax(text)
    })
})

// Paste: force plain text
queryEditor.addEventListener('paste', e => {
    e.preventDefault();
    const text = e.clipboardData.getData('text/plain');
    document.execCommand('insertText', false, text);
})

// Initial query queryEditor state
queryEditor.innerHTML = "-- EXISTING TABLES LIST<br>SELECT name FROM sqlite_master WHERE type='table'<br>ORDER BY name;"
queryEditor.innerHTML = highlightQuerySyntax(queryEditor.innerText)


// ================================================================================ QUERY EDITOR HISTORY (LOCAL BROWSER STORAGE) WITH HOTKEYS


function appendToQueryEditorHistory(newItem) {
    queryEditorHistory = JSON.parse(localStorage.getItem('queryEditorHistory')) || [] // empty list when null
    queryEditorHistory.push(newItem)
    queryEditorHistory = queryEditorHistory.slice(-queryHistoryRecordsLimit) // keep n newest queries
    localStorage.setItem('queryEditorHistory', JSON.stringify(queryEditorHistory))
    queryEditorHistory = queryEditorHistory
    queryEditorHistory = JSON.parse(localStorage.getItem('queryEditorHistory') || '[]')
    historyIndex = Math.max(0, queryEditorHistory.length - 1)
}

executeQueryButton.addEventListener('click', () => {
    if (queryEditor.innerHTML != queryEditorHistory.at(-1)) { 
        appendToQueryEditorHistory(queryEditor.innerHTML) // append if not the same as the last one
    }
})

// 1, 2, 3 to 1st, 2nd, 3rd etc.
function getOrdinal(n) { 
    const s = ["th", "st", "nd", "rd"]
    const v = n % 100
    return n + (s[(v - 20) % 10] || s[v] || s[0])
}

//  QUERY EDITOR KEY BINDINGS (HOTKEYS)
queryEditor.addEventListener("keydown", (e) => {
    // shift + enter
    if (e.shiftKey && e.key === "Enter") {
        e.preventDefault() // disable newline
        executeQueryButton.click()
        // console.log('shift + enter')
    }
    // ctrl + z
    else if (e.ctrlKey && e.key === 'z') {
        e.preventDefault()
        undoQueryChanges()
        // console.log('ctrl + z')
    }
    // ctrl + y
    else if (e.ctrlKey && e.key === 'y') {
        e.preventDefault()
        redoQueryChanges()
        // console.log('ctrl + y')
    }
    // ctrl + < (,)
    else if (e.ctrlKey && e.key === ",") {
        e.preventDefault() // some extensions may use ctrl+< or ctrl+>
        if (queryEditorHistory.length === 0) {
            executeQueryOutput.innerHTML = 'hotkey pressed, but query history is empty'
            return
        }
        if (historyIndex > 0) {historyIndex -= 1}
        queryEditor.innerHTML = queryEditorHistory[historyIndex]
        executeQueryOutput.style = 'color: var(--color-text-primary);' // normal color
        executeQueryOutput.innerHTML = `loaded ${getOrdinal(historyIndex+1)} out of ${queryEditorHistory.length} last executed queries`
    }
    // ctrl + > (.)
    else if (e.ctrlKey && e.key === ".") {
        e.preventDefault()
        if (queryEditorHistory.length === 0) {
            executeQueryOutput.innerHTML = 'hotkey pressed, but query history is empty'
            return
        }
        if (historyIndex < queryEditorHistory.length - 1) {historyIndex += 1}
        queryEditor.innerHTML = queryEditorHistory[historyIndex]
        executeQueryOutput.style = 'color: var(--color-text-primary);' // normal color
        executeQueryOutput.innerHTML = `loaded ${getOrdinal(historyIndex+1)} out of ${queryEditorHistory.length} last executed queries`
    }
})

function saveQuerySnapshot() {
    const currentTime = Date.now()
    // Save a snapshot only if enough time has passed to avoid batching too quickly
    if (currentTime - queryLastSaveTime > queryAutoBatchTimeout) {
        const snapshot = {
            html: queryEditor.innerHTML,
            caretPosition: saveCaretPosition(queryEditor)
        }

        if (queryUndoStack.length === queryUndoMaxHistoryLength) queryUndoStack.shift() // Limit history length - shift() removes first element
        queryUndoStack.push(snapshot)
        queryRedoStack.length = 0 // Clear redo stack when new change happens
        queryLastSaveTime = currentTime
    }
}

function restoreQuerySnapshot(snapshot) {
    queryEditor.innerHTML = snapshot.html
    restoreCaretPosition(queryEditor, snapshot.caretPosition)
}

function saveCaretPosition(containerEl) {
    const selection = window.getSelection()
    if (!selection.rangeCount) return null

    const range = selection.getRangeAt(0)
    const preCaretRange = range.cloneRange()
    preCaretRange.selectNodeContents(containerEl)
    preCaretRange.setEnd(range.startContainer, range.startOffset)

    return preCaretRange.toString().length
}

function restoreCaretPosition(containerEl, caretPosition) {
    if (caretPosition == null) return

    let charIndex = 0
    const range = document.createRange()
    range.setStart(containerEl, 0)
    range.collapse(true)

    const nodeStack = [containerEl]
    let node, stop = false

    while (!stop && (node = nodeStack.pop())) {
        if (node.nodeType === 3) {
            const nextCharIndex = charIndex + node.length
            if (caretPosition >= charIndex && caretPosition <= nextCharIndex) {
                range.setStart(node, caretPosition - charIndex)
                range.setEnd(node, caretPosition - charIndex)
                stop = true
            }
            charIndex = nextCharIndex
        } 
        else {
            let i = node.childNodes.length
            while (i--) nodeStack.push(node.childNodes[i])
        }
    }

    const sel = window.getSelection()
    sel.removeAllRanges()
    sel.addRange(range)
}

function undoQueryChanges() {
    if (queryUndoStack.length > 1) {
        const snapshot = queryUndoStack.pop() // pop() removes last item
        queryRedoStack.push(snapshot)
        restoreQuerySnapshot(queryUndoStack[queryUndoStack.length - 1])
    }
}

function redoQueryChanges() {
    if (queryRedoStack.length > 0) {
        const snapshot = queryRedoStack.pop()
        restoreQuerySnapshot(snapshot)
        queryUndoStack.push(snapshot)
    }
}

saveQuerySnapshot()


// ================================================================================ SEND (EXECUTE) QUERY AND FETCH BOKEH


document.getElementById("executeQueryButton").addEventListener("click", sendQueryAndFetchBokeh)

function sendQueryAndFetchBokeh() {
    // const queryEditor = document.getElementById('queryEditor')
    executeQueryOutput.style = 'color: var(--color-text-primary);' // normal color
    executeQueryOutput.innerHTML ='loading...'

    function getCleanTextFromContentEditable() {
        // clone to avoid messing with original
        let queryEditorClone = document.getElementById('queryEditor').cloneNode(true)
        queryEditorClone.querySelectorAll('br').forEach(br => {
            br.replaceWith("\n") // replace <br> elements with "\n" for python
        })
        // queryEditorClone = queryEditorClone.textContent.trim() // queryEditorClone = queryEditorClone.innerText.trim()
        queryEditorClone = queryEditorClone.innerText.trim()
        // split into lines, remove excessive whitespaces and join again
        const queryCleaned = queryEditorClone
        .split('\n') // Step 1: divide into lines
        .map(line => line.replace(/\s+/g, ' ')) // Step 2: replace every whitespace character with a regular space 
        .join('\n'); // Step 3: rejoin lines
        queryEditorClone = queryCleaned
        // console.log(queryEditorClone)
        return queryEditorClone
    }
    const queryText = getCleanTextFromContentEditable()
    const queryJson = JSON.stringify(queryText)

    fetch(window.origin.toString() + '/executeQuery', {
        method: "POST",
        credentials: "include", // cookies etc
        body: queryJson, // form results
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
            // console.log(items)
            console.log('======QUERY EXECUTION DONE======\n'+items.message+'\n\n' + queryText.toString())
            executeQueryOutput.innerHTML = items.message
            if (items.error === true){
                executeQueryOutput.style = 'color: var(--color-text-warning);'
                executeQueryOutput.innerHTML += '<br>' + items.errorMessage
            }
            if (items.resultsAmount === 0) {
                document.getElementById('plotDiv').innerHTML = ''
                document.getElementById('tableDiv').innerHTML = ''
                document.getElementById('downloadCsvContainer').style.display = 'none'
                document.getElementById('downloadCsvIcon').innerHTML = ''
                document.getElementById('downloadCsvText').innerHTML = ''
                document.getElementById('resultsAmount').innerHTML = '' //'no results ¯\\_(ツ)_/¯'
                if (items.error != true) {
                    executeQueryOutput.innerHTML += '<br>' + 'no results ¯\\_(ツ)_/¯'
                }
                return
            }
            // if all went good and results are not empty replace the divs with bokeh stuff
            else if (items.resultsAmount >= 1) {
                document.getElementById('plotDiv').innerHTML = '' //make div empty first
                document.getElementById('tableDiv').innerHTML = ''
                if (items.plot !== null) {Bokeh.embed.embed_item(items.plot, 'plotDiv')} // not every table has a plot
                Bokeh.embed.embed_item(items.table, 'tableDiv')
                document.getElementById('downloadCsvContainer').style.display = 'flex'
                document.getElementById('downloadCsvIcon').innerHTML = '<i class="fa fa-download" aria-hidden="true"></i>'
                document.getElementById('downloadCsvText').innerHTML = 'DOWNLOAD CSV'

                if (items.resultsAmount === 1) { //if 1 result
                    document.getElementById('resultsAmount').innerHTML = '1 result'
                    executeQueryOutput.innerHTML += '<br>' + '1 result'
                }
                else if (items.resultsAmount > 1) { // if >1 results
                    document.getElementById('resultsAmount').innerHTML = items.resultsAmount + ' results'
                    executeQueryOutput.innerHTML += '<br>' + items.resultsAmount + ' results'
                }
            }
        })
}


// ================================================================================ FETCH PROCESSES


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


// ================================================================================ TEST BROWSER STUFF


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


// ================================================================================ CREATE NEW FULL SCRAPING DIV


function createNewFullScrapingDiv (url, index, lastMessage) {
    const fullScrapingDivsContainer = document.getElementById('fullScrapingDivsContainer')
    const existingFullScrapingDivs = document.querySelectorAll('.fullScrapingDiv div')

    // HANDLING UNDEFINED ARGUMENTS
    if (url === undefined) { // IF URL ARGUMENT NOT PROVIDED
        // url = "https://justjoin.it/job-offers/bialystok?experience-level=mid&remote=yes&orderBy=DESC&sortBy=published"
        // url = "https://theprotocol.it/filtry/python;t/junior;p/zdalna;rw"
        let urlsList = [
            "https://theprotocol.it/praca", 
            //"https://theprotocol.it/filtry/python;t/zdalna;rw",
            //"https://theprotocol.it/filtry/trainee,assistant,junior,mid;p",
            // "https://theprotocol.it/filtry/trainee,assistant,junior,mid;p/hybrydowa,zdalna;rw",
            "https://theprotocol.it/filtry/trainee,assistant,junior,mid;p/",
            "https://justjoin.it",
            //"https://justjoin.it/job-offers/all-locations/python",
            //"https://justjoin.it/job-offers/all-locations/javascript",
            "https://justjoin.it/job-offers/all-locations?experience-level=junior,mid"
        ]
        // urlsList = ["https://theprotocol.it/filtry/python;t/trainee,assistant;p",] 
        url = urlsList[Math.floor(Math.random() * urlsList.length)] // random choice from the list
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


// ================================================================================ CHECK BUTTON STATE AND FETCH FULL SCRAPING ENDPOINT RECURSIVELY


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


// ================================================================================ SEND FORM AND FETCH BOKEH


document.getElementById("sendFormAndFetchBokehButton").addEventListener("click", sendFormAndFetchBokeh)

function sendFormAndFetchBokeh(e) {
    const sendFormAndFetchBokehOutput =  document.getElementById('sendFormAndFetchBokehOutput')
    sendFormAndFetchBokehOutput.innerHTML = 'loading...' //reset output
    saveFormValuesOnSearchClick()
    e.preventDefault() //prevent sending form default request

    if (atLeastOneCheckboxChecked() === false) {
        sendFormAndFetchBokehOutput.innerHTML = 'select at least one parameter to show'
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

    fetch(window.origin.toString() + '/', {
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
            // const queryEditor = document.getElementById('queryEditor')
            // const executeQueryOutput = document.getElementById('executeQueryOutput')
            executeQueryOutput.style = 'color: var(--color-text-primary);' // normal color
            queryEditor.innerHTML = items.query.replace(/\n/g, "<br>") // replace python newline with html <br>
            queryEditor.innerHTML = highlightQuerySyntax(queryEditor.innerText)
            if (items.error === true){
                executeQueryOutput.style = 'color: var(--color-text-warning);'
                executeQueryOutput.innerHTML = items.errorMessage
                sendFormAndFetchBokehOutput.innerHTML = 'query error - check description'
            }
            if (items.resultsAmount === 0) {
                document.getElementById('plotDiv').innerHTML = ''
                document.getElementById('tableDiv').innerHTML = ''
                document.getElementById('downloadCsvContainer').style.display = 'none'
                document.getElementById('downloadCsvIcon').innerHTML = ''
                document.getElementById('downloadCsvText').innerHTML = ''
                document.getElementById('resultsAmount').innerHTML = '' // empty to hide download div
                if (items.error != true) {
                    sendFormAndFetchBokehOutput.innerHTML = 'no results ¯\\_(ツ)_/¯'
                    executeQueryOutput.innerHTML = 'no results ¯\\_(ツ)_/¯'
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
                    sendFormAndFetchBokehOutput.innerHTML = '1 result'
                    executeQueryOutput.innerHTML = '1 result'
                }
                else if (items.resultsAmount > 1) { // if >1 results
                    document.getElementById('resultsAmount').innerHTML = items.resultsAmount + ' results'
                    sendFormAndFetchBokehOutput.innerHTML = items.resultsAmount + ' results'
                    executeQueryOutput.innerHTML = items.resultsAmount + ' results'
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

// ================================================================================ CHANGING CHECKBOXES STATE - CHECK/UNCHECK
document.getElementById('checkUncheckAll').addEventListener('click', () => {
    const checkUncheckAll = document.getElementById('checkUncheckAll')
    // The HTML entity &check; is converted into the Unicode character ✓ by the browser when the page is rendered
    if (checkUncheckAll.textContent == uncheckAllText) {
        document.querySelectorAll('.checkBox').forEach(checkbox => { checkbox.checked = false })
        checkUncheckAll.textContent = checkAllText
        checkUncheckAll.style = 'color: var(--color-primary);' // root variable
    }
    else if (checkUncheckAll.textContent == checkAllText) {
        document.querySelectorAll('.checkBox').forEach(checkbox => { checkbox.checked = true })
        checkUncheckAll.textContent = uncheckAllText
        checkUncheckAll.style = 'color: var(--color-secondary);'
    }
})

// ================================================================================ SAVE FORM INPUTS STATE IN BROWSER MEMORY AND LOAD IT ON REFRESH

// save form values on 'SEARCH' click
function saveFormValuesOnSearchClick(){
    document.querySelectorAll('input').forEach(input => {
        if (!input.name) {
            return // save only named ones
        }
        const key = input.name
        // console.log(key)
        if (input.type === 'text') {
            localStorage.setItem(key, input.value)
        }
        if (input.type === 'checkbox') {
            localStorage.setItem(key, input.checked)
        }
    })
}

// load form values on refresh (uncomment to save on input)
document.querySelectorAll('input').forEach(input => {
    const key = input.name
    if (input.type === 'text') {
        // Load saved text input
        const saved = localStorage.getItem(key)
        if (saved !== null) input.value = saved
        // // Save on input
        // input.addEventListener('input', () => {
        //     localStorage.setItem(key, input.value)
        // })
    }
    if (input.type === 'checkbox') {
        // Load saved checkbox state
        const saved = localStorage.getItem(key)
        if (saved !== null) input.checked = saved === 'true'
        // // Save on change
        // input.addEventListener('change', () => {
        //     localStorage.setItem(key, input.checked)
        // })
    }
})

// ================================================================================ HIDE / SHOW CATEGORIES
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

// MAKE WHOLE DOWNLOAD CSV CONTAINER CLICKABLE
document.getElementById('downloadCsvContainer').addEventListener('click', function() {
    let url = window.origin.toString() + "/downloadCsv"
    window.location.href = url
})

// ================================================================================ CHANGE HEADER TEXT CONTENT ON MOUSEOVER
headerContainer = document.getElementById("headerContainer")

headerContainer.addEventListener("mouseover", function() {
    headerText2.textContent = "so much crap"
    headerText2.style = 'color: var(--color-secondary);'
})
headerContainer.addEventListener("mouseout", function() {
    headerText2.textContent = "so much scrap";
    headerText2.style = 'color: var(--color-tertiary);'
})

// ================================================================================ CALENDAR TOOL FLATPICKR - styling in CSS file
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