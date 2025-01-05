import json, random, re, datetime
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy

from flask import Flask, render_template, request, send_file, make_response, jsonify
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource, WheelZoomTool, HTMLTemplateFormatter, HoverTool, TapTool, Range1d, LinearAxis
from bokeh.embed import json_item
from bokeh.io import curdoc #for dark theme
import multiprocessing, io, time
import numpy as np

from seleniumFunctions import queueManager, openBrowserIfNeeded, saveCookiesToJson, fullScraping
from databaseFunctions import Database, columnsAll, tableName

########################################################################## FLASK SERVER FUNCITONS ###########################################################################

def makeBokehPlot(dataframe): #Only offers with specified salary?
    # len(dataframe) >=1 at this point 
    # dataframe already ordered by (salaryMin+SalaryMax)/2 ASC

    pd.options.mode.copy_on_write = True #recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    pd.set_option('future.no_silent_downcasting', True)

    nonNanRowsDf = dataframe[dataframe['salaryMin'].notna()]
    nanRowsDf = dataframe[dataframe['salaryMin'].isna()]

    # SPECIFY UNSPECIFIED BARS HEIGHT
    if len(nonNanRowsDf) > 0: #otherwise division by 0 possible
        lookUpToValues = int(len(nonNanRowsDf)/6) #how many values to count average
        if lookUpToValues == 0: # avoid /0
            lookUpToValues = 1
        avgOfNLowestMinSalaries = nonNanRowsDf['salaryMin'].head(lookUpToValues).tolist() #select up to lookUpToValues
        avgOfNLowestMinSalaries = sum(avgOfNLowestMinSalaries) / len(avgOfNLowestMinSalaries) #avg
        avgOfNLowestMaxSalaries = nonNanRowsDf['salaryMax'].head(lookUpToValues).tolist() #select up to lookUpToValues
        avgOfNLowestMaxSalaries = sum(avgOfNLowestMaxSalaries) / len(avgOfNLowestMaxSalaries) #avg
        nanRowsDf['salaryMin'] = nanRowsDf['salaryMin'].fillna(avgOfNLowestMinSalaries) #replace nulls with values
        nanRowsDf['salaryMax'] = nanRowsDf['salaryMax'].fillna(avgOfNLowestMaxSalaries)
    else: #if only unspecified salaries foud
        avgOfNLowestMinSalaries = 4200 #some value to plot
        avgOfNLowestMaxSalaries = 4200
        nanRowsDf['salaryMin'] = nanRowsDf['salaryMin'].fillna(avgOfNLowestMinSalaries) #replace nulls with values
        nanRowsDf['salaryMax'] = nanRowsDf['salaryMax'].fillna(avgOfNLowestMaxSalaries)
        
    dataSalaryUnspecified = {
        'x': nanRowsDf.index.tolist(),
        'title': nanRowsDf['title'].values.tolist(),
        'activeFor': [(dtstr.days) for dtstr in (pd.to_datetime(nanRowsDf["datetimeLast"])-pd.to_datetime(nanRowsDf["datetimeFirst"])).tolist()], #.days shows only days
        'salaryAvg': [((avgOfNLowestMinSalaries+avgOfNLowestMaxSalaries)/2) for i in range (len(nanRowsDf))]
    }
    dataSalarySpecified = {
        'x': nonNanRowsDf.index.tolist(),
        'title': nonNanRowsDf['title'].values.tolist(),
        'activeFor': [(dtstr.days) for dtstr in (pd.to_datetime(nonNanRowsDf["datetimeLast"])-pd.to_datetime(nonNanRowsDf["datetimeFirst"])).tolist()], #.days shows only days
        'salaryMin': nonNanRowsDf['salaryMin'].values.tolist(),
        'salaryMax': nonNanRowsDf['salaryMax'].values.tolist(),
        'salaryAvg': [(a + b) / 2 for a, b in zip(nonNanRowsDf['salaryMin'].values.tolist(), nonNanRowsDf['salaryMax'].values.tolist())],
    }

    #Calculate ranges - SAFE MAX by declaring default values used if empty list
    maxActiveFor = int(max(max(dataSalaryUnspecified['activeFor'], default=0) , max(dataSalarySpecified['activeFor'], default=0))) +1 #
    maxSalary = max(max(dataSalaryUnspecified['salaryAvg'], default=0) , max(dataSalarySpecified['salaryMax'], default=0)) * 1.05

    sourceSalaryUnspecified = ColumnDataSource(dataSalaryUnspecified) #2 data sources
    sourceSalarySpecified = ColumnDataSource(dataSalarySpecified) #2 data sources
    plot = figure(title="", x_axis_label='Offer index', y_axis_label='Salary', height = 400, sizing_mode='stretch_width')
    plot.y_range = Range1d(start=0 - 1, end=maxSalary) # * 1.2 to fit the bars
    plot.x_range = Range1d(start=0 - 1, end=int(len(dataframe))) #too much empty space by default
    plot.extra_y_ranges = {"y2": Range1d(start=0, end=maxActiveFor)} #add 1 day
    #COLORS
    salaryUnspecifiedColor = 'rgb(60,60,160)'
    salarySpecifiedColor = 'rgb(80,80,220)'
    # daysActiveColor = 'rgb(30,150,30)'
    daysActiveColor = 'rgb(60,100,40)'
    # SALARY UNSPECIFIED BARS
    plot.vbar('x', top = 'salaryAvg', width = 0.70, source = sourceSalaryUnspecified, color=salaryUnspecifiedColor, alpha = 1) # MAIN BAR
    plot.vbar('x', top = 'activeFor', y_range_name="y2", source = sourceSalaryUnspecified, color=daysActiveColor, alpha = 0.15, width=0.90) # Active for
    # plot.segment(x0='x', y0='salaryMin', x1='x', y1='salaryMax', source=sourceSalaryUnspecified, line_width=2, color='black', alpha = 0.5) #Error bar
    # SALARY SPECIFIED BARS
    plot.vbar('x', top = 'salaryAvg', width = 0.70, source = sourceSalarySpecified, color=salarySpecifiedColor, alpha = 1) # MAIN BAR
    plot.vbar('x', top = 'activeFor', y_range_name="y2", source = sourceSalarySpecified, color=daysActiveColor, alpha = 0.15, width=0.90) # Active for
    plot.segment(x0='x', y0='salaryMin', x1='x', y1='salaryMax', source=sourceSalarySpecified, line_width=1.5, color='black', alpha=0.75) #Error bar
    
    plot.add_layout(LinearAxis(y_range_name="y2", axis_label="Days adtive"), 'right') # Add the second y-axis to the right
    
    # Configure minor gridlines
    plot.xgrid.minor_grid_line_color = 'rgb(80,80,80)'
    plot.ygrid.minor_grid_line_color = 'rgb(80,80,80)'
    plot.xgrid.minor_grid_line_alpha = 0.5 # Opacity
    plot.ygrid.minor_grid_line_alpha = 0.5

    taptool = TapTool() #highlight on tap
    wheel_zoom = WheelZoomTool()
    plot.toolbar.active_scroll = wheel_zoom
    hoverSalaryUnpecified = HoverTool(tooltips=[("Offer index:", "@x"), ("Job title:", "@title"), ("Salary:", "Unspecified"), ("Active for:", "@activeFor days")])
    hoverSalaryUnpecified.renderers = [plot.renderers[0]]# hover tool only on the salary bars
    hoverSalarySpecified = HoverTool(tooltips=[("Offer index:", "@x"), ("Job title:", "@title"), ("Min/Avg/Max:", "@salaryMin{0.}/@salaryAvg{0.}/@salaryMax{0.}"), ("Active for:", "@activeFor days")]) #{0} = no decimals
    hoverSalarySpecified.renderers = [plot.renderers[2]]# hover tool only on the salary bars
    plot.add_tools(hoverSalarySpecified, hoverSalaryUnpecified, taptool) #wheel_zoom removed for now
    #DARK THEME
    curdoc().theme = 'dark_minimal'
    curdoc().add_root(plot) #to apply the theme
    return plot

def makeBokehTable(dataframe):
    source = ColumnDataSource(dataframe)
    columns = []
    for column in dataframe.columns:
        if column == 'url': # to make a hyperlink
            columns.append(TableColumn(field=column, title=column, formatter=HTMLTemplateFormatter(template="""<a href="<%= value %>" target="_blank"><%= value %></a>""")))
        else:
            columns.append(TableColumn(field=column, title=column))     
    table = DataTable(source=source, columns=columns, height = 800, editable=True, sizing_mode="stretch_width")
    return table

#DECLARE FLASK APP
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
    TASK_QUEUE.put((openBrowserIfNeeded, (), {}))
    # time.sleep(300) #still shows in JS
    res = RESULT_QUEUE.get()
    return json.dumps(res)

@app.route('/saveCookiesToJson', methods=['GET'])
def saveCookiesToJsonEndpoint():
    print('\t\tsaveCookiesToJsonEndpoint')
    TASK_QUEUE.put((saveCookiesToJson, (), {}))
    res = RESULT_QUEUE.get()
    return json.dumps(res)

@app.route('/fullScraping', methods=['GET'])
def fullScrapingEndpoint():
    # print('\t\\fullScrapingEndpoint')
    TASK_QUEUE.put((fullScraping, (), {}))
    # time.sleep(random.uniform(1,2))
    res = RESULT_QUEUE.get()
    return json.dumps(res)

if __name__ == "__main__":
    # Database.createTableIfNotExists()
    TASK_QUEUE = multiprocessing.Queue()  # Queue for sending tasks to the worker
    RESULT_QUEUE = multiprocessing.Queue()  # Queue for receiving results from the worker

    # Start the worker process
    process = multiprocessing.Process(target=queueManager, args=(TASK_QUEUE, RESULT_QUEUE))
    process.start()
    app.run(debug=False) #runs (3?) additional python processes. IF TRUE USED TO RUN TWO SELENIUM BROWSERS ¯\_(ツ)_/¯

    # TASK_QUEUE.put((fetchUrlsFromAllThePages, (), {}))
    # # TASK_QUEUE.put((scrapToDatabase, (), {})) 
    # print(RESULT_QUEUE.get())
    # TASK_QUEUE.put("exit")
    # process.join() #could wait forever if process not terminated
    print('DAS ENDE')



##TODO
# paramsy do ustawienia - #vat, window size?, table name, url
# link table-plot?
# execute query?
# bokeh console errors in brave
# setCookiesFromJson inny msg jak cookies for domain not found
# na justjoin nie scrapuje dodatkowych location przy zminimalizowanym oknie
# dodac do DB 'oferujemy/benefity'

# NEED TO FIND 'OFFER NOT FOUND MSG AND CHECK WHICH DIVS DOES IT HAVE

# napisać o nested query w readme
