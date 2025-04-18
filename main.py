import json, re, datetime
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
from flask import Flask, render_template, request, send_file #, make_response, jsonify
from bokeh.resources import CDN
from bokeh.embed import json_item
import multiprocessing, io
from modules.Database import Database
from modules.SeleniumBrowser import SeleniumBrowser
from modules.makeBokehFigures import makeBokehPlot, makeBokehTable
import importlib, os, sys, time, threading # settings autoreload
import settings # 'from settings import variable' doesn't work with importlib autoreloading


########################################################################## FLASK ENDPOINTS ###########################################################################

app = Flask(__name__)

# root's GET is for CSS vars and POST is for query tool
@app.route('/', methods=['GET', 'POST'])
def root():
    # PREPARE TEMPLATE FOR CSS ROOT VARIABLES
    if request.method == 'GET':
        variablesString = ''
        for key, value in settings.CSS_VARIABLES.items():
            variablesString += f"--{key}:{value};" # no new line needed as it has ; instead
        cssRootTemplate = "<style>:root{"+variablesString+"}</style>"
        # print(cssRootTemplate)
        return render_template("app.html", cssRoot=cssRootTemplate, databaseColumns=settings.DATABASE_COLUMNS, resources=CDN.render()) # columnsAll=list(DATABASE_COLUMNS_OLD.keys())
    
    # QUERY TOOL
    elif request.method == 'POST':
        def makeFormOutputDictionary():
            formDictFromJson = request.get_json() #get form values from a request
            outputDict = {}
            for column in [column["dbColumnName"] for column in settings.DATABASE_COLUMNS]:
                rowDictionary = {'show': False, 'necessary': None, 'forbidden': None, 'above': None, 'below': None}
                #show column
                if formDictFromJson.get(column+'Show', False): #if not found assign False. Found only if form field not empty
                    rowDictionary['show'] = True
                #necessary phrase
                if formDictFromJson.get(column+'Necessary', False):
                    phraseNecessary = formDictFromJson.get(column+'Necessary')
                    # phraseNecessary = phraseNecessary.split(", ") #delete
                    rowDictionary['necessary'] = phraseNecessary
                #forbidden phrase
                if formDictFromJson.get(column+'Forbidden', False):
                    phraseForbidden = formDictFromJson.get(column+'Forbidden')
                    # phraseForbidden = phraseForbidden.split(", ") #delete
                    rowDictionary['forbidden'] = phraseForbidden
                #above
                if formDictFromJson.get(column+'Above', False):
                    rowDictionary['above'] = formDictFromJson.get(column+'Above')
                    # print('found ' + column+'Above') #
                #below
                if formDictFromJson.get(column+'Below', False):
                    rowDictionary['below'] = formDictFromJson.get(column+'Below')
                    # print('found ' + column+'Below') #
                outputDict[column] = rowDictionary #append row with column name as a key
            # print(outputDict)
            return outputDict
        
        def queryBuilder(formDictionary):
            
            def handleBracketsAndLogicalOperators(input, param, like):
                # print('handleBracketsAndLogicalOperators')
                if like:
                    likePart = ' LIKE '
                elif not like:
                    likePart = ' NOT LIKE '
                splittedResults = re.split(r" OR | AND ", input) # split on logic operator
                phrases = []
                for res in splittedResults:
                    res = re.sub(r'\(|\)', '', res) # remove brackets
                    res = re.sub(r'^ +| +$', '', res) # remove spaces at both ends
                    # print(res)
                    # print()
                    phrases.append(res)
                # BY NOW ALL PHRASES ARE IN THE LIST SO IT CAN PUT THE PHRASES INTO THE BRACKETS
                for phrase in phrases: # MAKE PLACEHOLDERS ONE BY ONE
                    input = re.sub(phrase, '<<<>>>', input, count=1) # count=1 to only replace the first match. This is needed because phrases content can overlap
                    # print(input)
                    # print()
                for phrase in phrases: # FILL PLACEHOLDERS ONE BY ONE
                    if phrase != 'NULL':# and phrase != 'NaN':
                        input = re.sub('<<<>>>', param + likePart + "('%" +phrase+"%')", input, count=1) # only first match
                    elif phrase == 'NULL':# or phrase == 'NaN':
                        isIsNotPart = re.sub(r' LIKE ', '', likePart) # just remove ' LIKE ' to fit
                        # print(likePart, isIsNotPart)
                        input = re.sub('<<<>>>', param + " IS " + isIsNotPart + " NULL", input, count=1) # only first match
                    # print(input)
                    # print()
                return input

            querySelectPart = "SELECT "
            queryMainPart = "\nWHERE 1=1" #removing this later
            for columnName in formDictionary.keys():
                currentColumnDictionary = formDictionary[columnName].items()
                for key, value in currentColumnDictionary:
                    # SELECT STATEMENT APPENDING
                    if key == 'show' and value:
                        querySelectPart += columnName + ', '
                    # ABOVE & BELOW 
                    elif key == 'above' and value:
                        queryMainPart += "\nAND ("+columnName+" > '"+value+"')"
                    elif key == 'below' and value:
                        queryMainPart += "\nAND ("+columnName+" < '"+value+"')"
                    # NECESSARY PHRASE
                    elif key == 'necessary' and value: # if list not empty
                        queryMainPart += "\nAND ("+ handleBracketsAndLogicalOperators(value, columnName, like=True) + ")"
                    # FORBIDDEN PHRASE
                    elif key == "forbidden" and value:
                        queryMainPart += "\nAND ("+ handleBracketsAndLogicalOperators(value, columnName, like=False) + ")"
            queryMainPart += '\nORDER BY (salaryMin+SalaryMax)/2 ASC, (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 * 60 DESC;' #order by

            querySelectPart = re.sub(r", $", '', querySelectPart) #remove ", " from the end
            querySelectPart += " FROM "+settings.DATABASE_TABLE_NAME # 1=1 to append only ANDs
            queryMainPart = re.sub(r" 1=1\nAND", '', queryMainPart) #remove "1=1\nAND" if at least 1 filter specified
            queryMainPart = re.sub(r"\nWHERE 1=1", '', queryMainPart)# or remove WHERE 1=1 if no filters specified. If specified shouldn't match this regexp
            query = querySelectPart + queryMainPart
            queryPlot = "SELECT datetimeFirst, datetimeLast, title, salaryMin, salaryMax FROM "+ settings.DATABASE_TABLE_NAME + queryMainPart #2nd query - always select datetimes and salaries for plotting, order by time active and avg salary
            # print('\n'+query+'\n'+queryPlot)
            return query, queryPlot
        
        global dataframeTable # to make it accessible to download at all times
        dataframeTable, dataframePlot = queryBuilder(makeFormOutputDictionary())
        queryToDisplay = queryBuilder(makeFormOutputDictionary())[0]
        try:
            dataframeTable = Database.queryToDataframe(dataframeTable)
            dataframePlot = Database.queryToDataframe(dataframePlot)
        except Exception as exception:
            # WRONG QUERY ERROR
            return json.dumps({'resultsAmount':0, 'query': queryToDisplay, 'error':True, 'errorMessage':str(exception)}), 200, {'Content-Type': 'application/json'} # return 200 even tho its error (JS check)
        # print(queryToDisplay)

        if len(dataframePlot) > 0 and len(dataframeTable) > 0: #tho their lengths should be equal
            plot = makeBokehPlot(dataframePlot)
            table = makeBokehTable(dataframeTable)
            # return json.dumps([json_item(plot), json_item(table), int(len(dataframeTable))])
            # ALL FINE - SEND PLOT AND TABLE
            return json.dumps({'resultsAmount':int(len(dataframeTable)), 'plot': json_item(plot), 'table':json_item(table), 'query': queryToDisplay}), 200, {'Content-Type': 'application/json'}
        # QUERY OK BUT NO RESULTS
        return json.dumps({'resultsAmount':0, 'query': queryToDisplay}), 200, {'Content-Type': 'application/json'} # when no results


@app.route('/executeQuery', methods=['POST'])
def executeQueryEndpoint():
    query = request.get_json()
    # print('\texecuteQueryEndpoint')
    # print(query)
    def removeComments(text): # splitting into lines, removing what's after -- and joining again
        lines = text.splitlines()
        cleaned = [line.split('--')[0].rstrip() for line in lines] # split on first occurrence of -- and remove what's to the right side of that
        return '\n'.join(cleaned)
    query = removeComments(query)
    # print(query)

    # FIRST TRY EXECUTING THE QUERY AS NOT EVERY QUERY RETURNS TABLE OUTPUT
    queryResults = Database.executeQuery(query)
    if queryResults['executed'] == False:
        # BAD QUERY CASE
        return json.dumps({'resultsAmount':0, 'error':True, 'errorMessage':str(queryResults['message']), 'message':"query execution error"}), 200, {'Content-Type': 'application/json'} # return 200 even tho its error (JS check)

    # QUERY EXECUTED AT THIS POINT
    # TRY MAKING PLOT QUERY, ALTHOUGH NOT ALWAYS POSSIBLE (no SELECT...FROM part, no columns etc.)
    try:       
        dividedQuery = re.search(r'SELECT.*\s+FROM\s+(?:["\[\']?)([\w-]+)(?:["\]\']?)\s*(.*)$', query, flags=re.IGNORECASE|re.DOTALL) # pick a word after the last 'SELECT...FROM ' ($ at the end of regex) and the rest after table name (which can be in [] "" or ''). re.DOTALL to match newline
        tableName = dividedQuery.group(1) # None if not found
        queryAfterTableName = dividedQuery.group(2)
        queryPlot = "SELECT datetimeFirst, datetimeLast, title, salaryMin, salaryMax FROM " + tableName + " " + queryAfterTableName
        # print(queryPlot)
    except Exception as exception:
        # print(exception)
        queryPlot = None
            
    # TRY MAKING TABLE > PLOT (as without the table there's no plot)
    try:
        dataframeTable = Database.queryToDataframe(query)
        table = makeBokehTable(dataframeTable) # table ready
    except Exception as exception:
        # NO TABLE AND PLOT, BUT QUERY VALID
        return json.dumps({'resultsAmount':0, 'message':"query executed - table and plot unavailable"}), 200, {'Content-Type': 'application/json'}
    
    if len(dataframeTable) == 0:
        # QUERY OK BUT NO RESULTS
        return json.dumps({'resultsAmount':0, 'message':"query executed - no results"}), 200, {'Content-Type': 'application/json'}
    
    # TRY MAKING A PLOT
    try:
        dataframePlot = Database.queryToDataframe(queryPlot)
    except Exception as exception:
        # SEND TABLE ONLY - ERROR ON PLOT GENERATION ('plot': None)
        return json.dumps({'resultsAmount':int(len(dataframeTable)), 'plot': None, 'table':json_item(table), 'message':"query executed - plot unavailable"}), 200, {'Content-Type': 'application/json'}             
    
    # ALL FINE - TRY SENDING PLOT AND TABLE
    try:
        plot = makeBokehPlot(dataframePlot) # plot ready
        return json.dumps({'resultsAmount':int(len(dataframeTable)), 'plot': json_item(plot), 'table':json_item(table), 'message':"query executed"}), 200, {'Content-Type': 'application/json'}
    except Exception as exception:
        # plot generating exception - rare or never
        return json.dumps({'resultsAmount':0, 'error':True, 'errorMessage':str(exception), 'message':"query executed"}), 200, {'Content-Type': 'application/json'}

@app.route('/downloadCsv')
def downloadCsvEndpoint():
    # Save the DataFrame to a CSV file
    csvName = "jobScrappingResults " + str(datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + ".csv"
    # Save the DataFrame to a CSV in memory
    buffer = io.BytesIO() #buffer for a csv file to avoid saving csv on a disk
    dataframeTable.to_csv(buffer, sep=',', encoding='utf-8-sig', index=True, header=True)
    buffer.seek(0)  # Reset buffer position to the beginning
    # Send the CSV file as a downloadable response
    return send_file(buffer, as_attachment=True, download_name=csvName, mimetype='text/csv')

@app.route('/openBrowser', methods=['GET'])
def openTestBrowserEndpoint():
    print('\t\topenTestBrowserEndpoint')
    process = getOrCreateProcess(settings.testBrowserUrlPlaceholder, -1) # JUST SOME STRING AND NEGATIVE INDEX AS IT'S NOT A SCRAPING BROWSER
    process['taskQueue'].put((SeleniumBrowser.openBrowserIfNeeded, (), {})) # pass tuple to seleniumFunctions
    # time.sleep(300) # still shows in JS
    res = process['resultQueue'].get()
    return json.dumps(res)

@app.route('/saveCookiesToJson', methods=['GET'])
def saveCookiesToJsonEndpoint():
    print('\t\tsaveCookiesToJsonEndpoint')
    process = getOrCreateProcess(settings.testBrowserUrlPlaceholder, -1) # JUST SOME STRING AND NEGATIVE INDEX AS IT'S NOT A SCRAPING BROWSER
    process['taskQueue'].put((SeleniumBrowser.saveCookiesToJson, (), {})) # pass tuple to seleniumFunctions
    # time.sleep(random.uniform(1,2))
    res = process['resultQueue'].get()
    return json.dumps(res)

@app.route('/fullScraping', methods=['POST'])
def fullScrapingEndpoint():
    # print('\t\\fullScrapingEndpoint')
    requestData = request.get_json('url')
    url = requestData.get('url')
    divIndex = requestData.get('divIndex')
    # print('\t\t\t\t', url, divIndex)
    # listProcessesExceptTestBrowser()

    processDict = getOrCreateProcess(url, divIndex)

    # WHEN PROCESS ALREADY EXISTS AT DIFFERENT DIVINDEX
    if 'process' not in processDict:
        return json.dumps(processDict) # {'message':...}

    processDict['taskQueue'].put((SeleniumBrowser.fullScraping, (), {})) # pass tuple to seleniumFunctions
    # time.sleep(random.uniform(1,2))
    res = processDict['resultQueue'].get()
    processDict['lastMessage'] = res['message'] # overwrite last message

    if 'killProcess' in res and res['killProcess'] == True: # if killProcess key found in dictionary and == True
        killProcessAndCloseBrowser(url) # KILL PROCESS
    return json.dumps(res)

@app.route('/killProcessIfExists', methods=['POST'])
def killProcessIfExistsEndpoint():
    try:
        # print('\t\tkillProcessIfExistsEndpoint')
        requestData = request.get_json('url') # arguments
        url = requestData.get('url')
        divIndex = requestData.get('divIndex')

        if returnProcessIfBothMatchOrNone(url, divIndex) == None:
            # print('NO PROCESS TO KILL')
            return json.dumps({'success':True, 'message':'no process to kill'})

        killProcessAndCloseBrowser(url) # PRINTS
        # print(url, divIndex)
        return json.dumps({'success':True, 'message':'process killed'})
    except Exception as exception:
        return json.dumps({'success':False, 'message':str(exception)})

@app.route('/getProcesses', methods=['GET'])
def getProcessesEndpoint():
    return json.dumps (listProcessesExceptTestBrowser())


########################################################################### PROCESSES MANAGEMENT ########################################################################### 

def workerBrowser(url, task_queue, result_queue):
    browserInstance = SeleniumBrowser(url) # EACH PROCESS (WORKER) HAS ITS OWN BROWSER INSTANCE
    print('INITIALIZED workerBrowser for url ' + url)
    while True:
        task = task_queue.get()
        # if 'killProcess' in task and task['killProcess'] == True: # if killProcess key found in dictionary and == True
        #     killProcessIfExistsEndpoint(url)
        #     print('KILLED workerBrowser for url ' + url)
        #     break
        func, args, kwargs = task
        try:
            result = func(browserInstance, *args, **kwargs) # USE THE BROWSER INSTANCE
            result_queue.put(result)
        except Exception as exception:
            result_queue.put({'success':False, 'message':'workerBrowser exception: ' + str(exception)})

def listProcessesExceptTestBrowser():
    processes = [{'divIndex':process['divIndex'], 'url':process['url'], 'lastMessage':process['lastMessage'] }
                  for process in PROCESSES_LIST
                  if process['url'] != settings.testBrowserUrlPlaceholder]
    # print('\n')
    # print('\t\tactive_processes len = ' + str(len(processes)))
    # print(processes)
    # print('\n')
    # print(processes)
    return processes

# check typeof(process) and if it already did start() - check is_alive() / exitcode 
def getOrCreateProcess(url, divIndex):
    # no running process case
    if len(PROCESSES_LIST) == 0:
        return startProcess(url, divIndex) # startProcess() appends to empty PROCESSES_LIST
    # look for URL
    for processDict in PROCESSES_LIST:
        # IF URL CHANGED FOR THAT DIVINDEX
        if processDict['divIndex'] == divIndex and processDict['url'] != url:
            killProcessAndCloseBrowser(processDict['url'])
            print('\t\tCHANGING PROCESS URL FOR DIVINDEX ' + str(divIndex))
            return startProcess(url, divIndex)
        # IF URL FOUND
        if processDict['url'] == url:
            if type(processDict['process']) == multiprocessing.context.Process:
                
                if processDict['divIndex'] == divIndex: # URL and divIndex match
                    return processDict # FOUND RUNNING PROCESS FOR THIS divIndex
                
                elif processDict['divIndex'] != divIndex: # just URL match
                    ########################## THE ONLY PATH WHICH DOES NOT RETURN A PROCESS ##########################
                    # print('\tprocess for url '+url+' already exists at divIndex '+str(processDict['divIndex']))
                    return {'message':'a process for that URL already exists', 'killProcess': True}

            else: # type(processDict['process']) != multiprocessing.context.Process - just for safety
                return startProcess(url, divIndex)
    # if URL not found start new process
    return startProcess(url, divIndex) # appends to PROCESSES_LIST

def returnProcessIfBothMatchOrNone(url, divIndex):
    # no running process case
    if len(PROCESSES_LIST) == 0:
        return None
    # look for URL
    for processDict in PROCESSES_LIST:
        if processDict['url'] == url and int(processDict['divIndex']) == int(divIndex):
            return processDict # FOUND PROCESS FOR THAT ARGUMENTS
    # if URL not found return None
    return None

def startProcess(url, divIndex):
    taskQueue = multiprocessing.Queue()  # Queue for sending tasks to the worker
    resultQueue = multiprocessing.Queue()  # Queue for receiving results from the worker
    # Create a new process
    process = multiprocessing.Process(target=workerBrowser, args=(url, taskQueue, resultQueue))
    process.daemon = True # end this process when main process dies
    processDict = {'url': url, 'divIndex': divIndex, 'lastMessage':'', 'process': process, 'taskQueue':taskQueue, 'resultQueue':resultQueue}
    # Append to the global list
    PROCESSES_LIST.append(processDict)
    # Start the process
    process.start()
    return processDict

def killProcessAndCloseBrowser(url):
    # listProcessesExceptTestBrowser()
    for processDict in PROCESSES_LIST:
        if processDict["url"] == url: # DELETES ALL FOR THAT URL (should be just 1 tho)
            processDict['taskQueue'].put((SeleniumBrowser.closeBrowser, (), {})) # CLOSE A BROWSER FIRST
            processDict['resultQueue'].get() # wait till it closes a browser
            processDict["process"].terminate()  # Stop the process
            processDict["process"].join()  # Ensure the process finishes cleanup
            PROCESSES_LIST.remove(processDict)  # remove from the PROCESSES_LIST
            print(f"TERMINATED PROCESS FOR '{url}'")
            # listProcessesExceptTestBrowser()
            return
            # return jsonify({"message": f"Process for '{url}' terminated successfully!"})
    print('no process to terminate for ' + url)

PROCESSES_LIST = [] #[ {'url': url, 'divIndex': divIndex, 'lastMessage':'', 'process': process, 'taskQueue':taskQueue, 'resultQueue':resultQueue}, {}, ... ]


########################################################################### SETTINGS AUTORELOAD ########################################################################### 

# Since python caches imports, when settings.py is reloaded, all modules using 'import settings' will get the updated values automatically
def reloadSettingsOnChange():
    settingsPath = settings.__file__
    modifiedTimeLast = os.path.getmtime(settingsPath)
    while True:
        time.sleep(1)  # the thread will look for changes once per second
        modifiedTimeCurrent = os.path.getmtime(settingsPath)
        if modifiedTimeCurrent != modifiedTimeLast:
            modifiedTimeLast = modifiedTimeCurrent
            
            importlib.reload(settings) # all modules using 'import settings' will get these reloaded values
            print("⚡ Settings reloaded ⚡")


########################################################################### APP INITIALIZATION ########################################################################### 

if __name__ == "__main__":
    Database.createTableIfNotExists()

    threading.Thread(target=reloadSettingsOnChange, daemon=True).start() # start a thread to detect settings.py changes

    if settings.DOCKERIZE_MODE_ACTIVE == True:
        host = '0.0.0.0' # host = 0.0.0.0 allows docker app to accept connections from outside the container, like via localhost:5000
    else:
        host = 'localhost'
    port=5000

    print(f"\n\tStarting job scraper. Visit http://{host}:{port} and begin.\n")
    app.run(host=host, port=port, debug=False) # if debug=True it auto-reloads after detecting code change, but runs additional process
    print("\n\tJob scraper closed.\n")


###########################################  TODO
# terminate test browser instance at some point (check ifBrowserOpen on any add/delete process click?)
# always natural scale on plot y-axis?