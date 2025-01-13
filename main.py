import json, random, re, datetime
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
from flask import Flask, render_template, request, send_file, make_response, jsonify
from bokeh.resources import CDN
from bokeh.embed import json_item
import multiprocessing, io, time
# import numpy as np
from databaseFunctions import Database, columnsAll, tableName
from SeleniumBrowser import SeleniumBrowser
from makeBokehFigures import makeBokehPlot, makeBokehTable

########################################################################## FLASK SERVER FUNCTIONS ###########################################################################

app = Flask(__name__)

@app.route('/downloadCsv')
def downloadCsv():
    # Save the DataFrame to a CSV file
    csvName = "jobScrappingResults " + str(datetime.datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + ".csv"
    # Save the DataFrame to a CSV in memory
    buffer = io.BytesIO() #buffer for a csv file to avoid saving csv on a disk
    dataframeTable.to_csv(buffer, sep=',', encoding='utf-8-sig', index=True, header=True)
    buffer.seek(0)  # Reset buffer position to the beginning
    # Send the CSV file as a downloadable response
    return send_file(buffer, as_attachment=True, download_name=csvName, mimetype='text/csv')

@app.route('/', methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        # return render_template("form.html", columnsAll=columnsAll)
        return render_template("app.html", columnsAll=columnsAll, resources=CDN.render())
    
    elif request.method == 'POST':
        def makeFormOutputDictionary():
            formDictFromJson = request.get_json() #get form values from a request
            outputDict = {}
            for column in columnsAll:
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
                if like:
                    likePart = ' LIKE '
                elif not like:
                    likePart = ' NOT LIKE '
                splittedResults = re.split(r" OR | AND ", input) #split on logic operator
                phrases = []
                for res in splittedResults:
                    res = re.sub(r'\(|\)', '', res) #remove brackets
                    res = re.sub(r'^ +| +$', '', res) #remove spaces at both ends
                    phrases.append(res)
                for phrase in phrases: #make placeholders one by one
                    input = re.sub(phrase, '<<<>>>', input, count=1) #count=1 to only replace the first match. This is needed because phrases content can overlap
                for phrase in phrases: #fill placeholders one by one
                    input = re.sub('<<<>>>', param + likePart + "('%" +phrase+"%')", input, count=1) #only first match
                return input

            querySelectPart = "SELECT "
            queryMainPart = "\nWHERE 1=1" #removing this later
            for columnName in formDictionary.keys():
                currentColumnDictionary = formDictionary[columnName].items()
                for key, value in currentColumnDictionary:
                    # SELECT STATEMENT APPENDING
                    if key == 'show' and value:
                        querySelectPart += columnName + ', '
                    #ABOVE & BELOW 
                    elif key == 'above' and value:
                        queryMainPart += "\nAND ("+columnName+" > '"+value+"')"
                    elif key == 'below' and value:
                        queryMainPart += "\nAND ("+columnName+" < '"+value+"')"
                    #NECESSARY PHRASE
                    elif key == 'necessary' and value: # if list not empty
                        queryMainPart += "\nAND ("+ handleBracketsAndLogicalOperators(value, columnName, like=True) + ")"
                    #FORBIDDEN PHRASE
                    elif key == "forbidden" and value:
                        queryMainPart += "\nAND ("+ handleBracketsAndLogicalOperators(value, columnName, like=False) + ")"
            queryMainPart += '\nORDER BY (salaryMin+SalaryMax)/2 ASC, (JULIANDAY(datetimeLast) - JULIANDAY(datetimeFirst)) * 24 * 60 DESC;' #order by

            querySelectPart = re.sub(r", $", '', querySelectPart) #remove ", " from the end
            querySelectPart += " FROM "+tableName # 1=1 to append only ANDs
            queryMainPart = re.sub(r" 1=1\nAND", '', queryMainPart) #remove "1=1\nAND" if at least 1 filter specified
            queryMainPart = re.sub(r"\nWHERE 1=1", '', queryMainPart)# or remove WHERE 1=1 if no filters specified. If specified shouldn't match this regexp
            query = querySelectPart + queryMainPart
            queryPlot = "SELECT datetimeFirst, datetimeLast, title, salaryMin, salaryMax FROM "+ tableName + queryMainPart #2nd query - always select datetimes and salaries for plotting, order by time active and avg salary
            # print('\n'+query+'\n'+queryPlot)
            return query, queryPlot
        
        global dataframeTable #to make it accessible to download at all times
        dataframeTable, dataframePlot = queryBuilder(makeFormOutputDictionary())
        dataframeTable = Database.queryToDataframe(dataframeTable)
        dataframePlot = Database.queryToDataframe(dataframePlot)
        queryToDisplay = queryBuilder(makeFormOutputDictionary())[0]
        # print(queryToDisplay)

        if len(dataframePlot) > 0 and len(dataframeTable) > 0: #tho their lengths should be equal
            plot = makeBokehPlot(dataframePlot)
            table = makeBokehTable(dataframeTable)
            # return json.dumps([json_item(plot), json_item(table), int(len(dataframeTable))])
            return json.dumps({'resultsAmount':int(len(dataframeTable)), 'plot': json_item(plot), 'table':json_item(table), 'query': queryToDisplay}), 200, {'Content-Type': 'application/json'}

        return json.dumps({'resultsAmount':0, 'query': queryToDisplay}), 200, {'Content-Type': 'application/json'} #when no results

@app.route('/openBrowser', methods=['GET'])
def openBrowserEndpoint():
    print('\t\topenBrowserEndpoint')
    process = getOrCreateProcess('cookiesBrowser') # JUST SOME STRING AS IT'S NOT A SCRAPING BROWSER
    process['taskQueue'].put((SeleniumBrowser.openBrowserIfNeeded, (), {})) # pass tuple to seleniumFunctions
    # time.sleep(300) #still shows in JS
    res = process['resultQueue'].get()
    print(res)
    return json.dumps(res)

@app.route('/saveCookiesToJson', methods=['GET'])
def saveCookiesToJsonEndpoint():
    print('\t\tsaveCookiesToJsonEndpoint')
    process = getOrCreateProcess('cookiesBrowser') # JUST SOME STRING AS IT'S NOT A SCRAPING BROWSER
    process['taskQueue'].put((SeleniumBrowser.saveCookiesToJson, (), {})) # pass tuple to seleniumFunctions
    # time.sleep(random.uniform(1,2))
    res = process['resultQueue'].get()
    return json.dumps(res)

@app.route('/fullScraping', methods=['POST'])
def fullScrapingEndpoint():
    # print('\t\\fullScrapingEndpoint')
    url = request.get_json()
    listProcesses()
    process = getOrCreateProcess(url)
    process['taskQueue'].put((SeleniumBrowser.fullScraping, (), {})) # pass tuple to seleniumFunctions
    # time.sleep(random.uniform(1,2))
    res = process['resultQueue'].get()
    if 'killProcess' in res and res['killProcess'] == True: # if killProcess key found in dictionary
        killProcess(url)
    return json.dumps(res)


######################################################## PROCESSES MANAGEMENT


def workerBrowser(url, task_queue, result_queue):
    browserInstance = SeleniumBrowser(url) # EACH PROCESS (WORKER) HAS ITS OWN BROWSER INSTANCE
    print('INITIALIZED workerBrowser for url ' + url)
    while True:
        task = task_queue.get()
        if task == "KILL PROCESS":
            print('KILLED workerBrowser for url ' + url)
            break
        func, args, kwargs = task
        try:
            result = func(browserInstance, *args, **kwargs) # USE THE BROWSER INSTANCE
            result_queue.put(result)
        except Exception as exception:
            result_queue.put({'success':False, 'message':'workerBrowser exception: ' + str(exception)})

def listProcesses():
    active_processes = [ {"url": process["url"], "is_alive": process["process"].is_alive()} for process in PROCESSES_LIST ] # works for PROCESSES_LIST == [] as well
    print('\t\tlistProcesses')
    print('\t\tactive_processes len = ' + str(len(active_processes)))
    print(active_processes)
    # return jsonify(active_processes)

# check typeof(process) and if it already did start() - check is_alive() / exitcode 
def getOrCreateProcess(url):
    # no running process
    if len(PROCESSES_LIST) == 0:
        return startProcess(url) # appends to empty PROCESSES_LIST
    # look for URL
    for processDict in PROCESSES_LIST:
        if processDict['url'] == url: # if URL found - MAKE HTTPS NOT NECESSARY
            if processDict['process'] != None:       # lepiej typeof()
                print('process for url '+url+' already exists')
                return processDict # FOUND RUNNING PROCESS
    # if URL not found start new process
    return startProcess(url) # appends to PROCESSES_LIST

def startProcess(url):
    # Create a new process
    taskQueue = multiprocessing.Queue()  # Queue for sending tasks to the worker
    resultQueue = multiprocessing.Queue()  # Queue for receiving results from the worker
    process = multiprocessing.Process(target=workerBrowser, args=(url, taskQueue, resultQueue))
    process.daemon = True # end this process when main process dies
    processDict = {"url": url, "process": process, 'taskQueue':taskQueue, 'resultQueue':resultQueue}
    # Add to the global list
    PROCESSES_LIST.append(processDict)
    # Start the process
    process.start()
    return processDict

def killProcess(url):
    for process in PROCESSES_LIST:
        if process["url"] == url:
            process["process"].terminate()  # Stop the process
            process["process"].join()  # Ensure the process finishes cleanup
            del process # remove from the PROCESSES_LIST
            print(f"Process for '{url}' terminated successfully!")
            listProcesses()
            return
            # return jsonify({"message": f"Process for '{url}' terminated successfully!"})
    print('no process to terminate for ' + url)

# {"url": url, "process": process, 'taskQueue':taskQueue, 'resultQueue':resultQueue}
PROCESSES_LIST = []

if __name__ == "__main__":
    listProcesses()
    app.run(debug=False)
    print("""if __name__ == "__main__": ends here""")




##TODO
# paramsy do ustawienia - #vat, window size?, table name, url - część w pliku settings?
# use grossToNetMultiplier just to recalculate before displaying?
# link table-plot??
# execute query endpoint?
# console errors in brave
# na justjoin nie scrapuje dodatkowych location przy zminimalizowanym oknie - force active window?
# dodac do DB 'oferujemy/benefity?
# napisać o nested query w readme
# KILL PROCESS ON URL CHANGE

# NEED TO FIND 'OFFER NOT FOUND MSG AND CHECK WHICH DIVS DOES IT HAVE (jj.it)















#  KOD PRZED GLOBAL PROCESS LISTA

# ####################################

# @app.route('/openBrowser', methods=['GET'])
# def openBrowserEndpoint():
#     print('\t\topenBrowserEndpoint')
#     TASK_QUEUE.put((SeleniumBrowser.openBrowserIfNeeded, (), {}))
#     # time.sleep(300) #still shows in JS
#     res = RESULT_QUEUE.get()
#     print(res)
#     return json.dumps(res)

# @app.route('/saveCookiesToJson', methods=['GET'])
# def saveCookiesToJsonEndpoint():
#     print('\t\tsaveCookiesToJsonEndpoint')
#     TASK_QUEUE.put((SeleniumBrowser.saveCookiesToJson, (), {}))
#     res = RESULT_QUEUE.get()
#     return json.dumps(res)

# @app.route('/fullScraping', methods=['POST'])
# def fullScrapingEndpoint():
#     # print('\t\\fullScrapingEndpoint')
#     url = request.get_json()
#     # print(url)
#     TASK_QUEUE.put((SeleniumBrowser.fullScraping, (), {})) # pass tuple to seleniumFunctions
#     # time.sleep(random.uniform(1,2))
#     res = RESULT_QUEUE.get()
#     if 'killProcess' in res: # if killProcess key found in dictionary
#         if res['killProcess'] == True:
#             TASK_QUEUE.put("KILL PROCESS") # STOP THE PROCESS
#     return json.dumps(res)

# ## PROCESS QUEUE MANAGEMENT
# def workerBrowser(url, task_queue, result_queue):
#     browserInstance = SeleniumBrowser(url) # EACH PROCESS (WORKER) HAS ITS OWN BROWSER INSTANCE
#     print('INITIALIZED workerBrowser for url ' + url)
#     while True:
#         task = task_queue.get()
#         if task == "KILL PROCESS":
#             print('KILLED workerBrowser for url ' + url)
#             break
#         func, args, kwargs = task
#         try:
#             result = func(browserInstance, *args, **kwargs) # USE THE BROWSER INSTANCE
#             result_queue.put(result)
#         except Exception as exception:
#             result_queue.put({'success':False, 'message':'workerBrowser exception: ' + str(exception)})



# # check typeof(process) and if it already did start() - check is_alive() / exitcode 
# # def getOrCreateProcess(url):
# #     if len(PROCESSES_LIST) <= 1:
# #         return 
# #     for PROCESS in PROCESSES_LIST:
# #         if PROCESS['url'] == url: # if URL found
# #             if PROCESS['instance'] != None:       # lepiej typeof()
# #                 return PROCESS
# #             else


# PROCESSES_LIST = [{'url':None, 'process':None, 'taskQueue':None, 'resultQueue':None}]
# TASK_QUEUE = multiprocessing.Queue()  # Queue for sending tasks to the worker
# RESULT_QUEUE = multiprocessing.Queue()  # Queue for receiving results from the worker

# if __name__ == "__main__":
#     # Start the worker process
#     process = multiprocessing.Process(target=workerBrowser, args=('https://theprotocol.it/filtry/ai-ml;sp', TASK_QUEUE, RESULT_QUEUE))
#     process.daemon = True # exit with main process
#     process.start()

#     app.run(debug=False)
#     print("""if __name__ == "__main__": ends here""")