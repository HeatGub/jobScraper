from bokeh.plotting import figure
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource, WheelZoomTool, HTMLTemplateFormatter, HoverTool, TapTool, Range1d, LinearAxis, InlineStyleSheet
import settings
import pandas as pd

############################################################################# BOKEH FUNCITONS ###############################################################################
def makeBokehPlot(dataframe): #Only offers with specified salary?
    # len(dataframe) >=1 at this point 
    # dataframe already ordered by (salaryMin+SalaryMax)/2 ASC

    pd.options.mode.copy_on_write = True #recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    pd.set_option('future.no_silent_downcasting', True)

    nonNanRowsDf = dataframe[dataframe['salaryMin'].notna() & dataframe['salaryMax'].notna()] # must be numbers or the plot will be screwed
    nanRowsDf = dataframe[dataframe['salaryMax'].isna()]

    # SPECIFY UNSPECIFIED BARS HEIGHT
    if len(nonNanRowsDf) > 0: #otherwise division by 0 possible
        lookUpToValues = int(len(nonNanRowsDf)/4) # HOW MANY VALUES TO COUNT FOR AVERAGE
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
    tools = "pan,box_select,reset" # otherwise used to add 2 zoom tools
    plot = figure(title="", x_axis_label='offer index', y_axis_label='salary [pln net/month]', height = settings.BOKEH_PLOT_HEIGHT, sizing_mode='stretch_width', tools=tools)
    plot.add_layout(LinearAxis(y_range_name="y2", axis_label="days active"), 'right') # Add the second y-axis to the right. DONT MOVE IT - MAY BREAK CSS
    plot.y_range = Range1d(start=0 - 1, end=maxSalary) # * 1.2 to fit the bars
    plot.x_range = Range1d(start=0 - 1, end=int(len(dataframe))) #too much empty space by default
    plot.extra_y_ranges = {"y2": Range1d(start=0, end=maxActiveFor)} #add 1 day
      
    # COLOR SETTINGS
    plot.border_fill_color = settings.CSS_VARIABLES['color-background-secondary'] # outside the plot area
    plot.background_fill_color = settings.CSS_VARIABLES['color-background-tertiary'] # plot area
    # plot.background_fill_color = CSS_VARIABLES['primary-color'] # plot area

    plot.xaxis.axis_line_color = settings.CSS_VARIABLES['color-plot-grid-line']
    plot.xaxis.major_tick_line_color = settings.CSS_VARIABLES['color-plot-grid-line']
    plot.xaxis.minor_tick_line_color = settings.CSS_VARIABLES['color-plot-grid-line']
    plot.yaxis.axis_line_color = settings.CSS_VARIABLES['color-plot-grid-line']
    plot.yaxis.major_tick_line_color = settings.CSS_VARIABLES['color-plot-grid-line']
    plot.yaxis.minor_tick_line_color = settings.CSS_VARIABLES['color-plot-grid-line']

    plot.xgrid.grid_line_color = settings.CSS_VARIABLES['color-plot-grid-line']
    plot.ygrid.grid_line_color = settings.CSS_VARIABLES['color-plot-grid-line']
    plot.xgrid.minor_grid_line_color = settings.CSS_VARIABLES['color-plot-minor-grid-line']
    plot.ygrid.minor_grid_line_color = settings.CSS_VARIABLES['color-plot-minor-grid-line']

    plot.xaxis.axis_label_text_color = settings.CSS_VARIABLES['color-text-primary']
    plot.yaxis.axis_label_text_color = settings.CSS_VARIABLES['color-text-primary']
    plot.xaxis.major_label_text_color = settings.CSS_VARIABLES['color-text-secondary']
    plot.yaxis.major_label_text_color = settings.CSS_VARIABLES['color-text-secondary']
        
    # FONT SETTINGS
    plot.xaxis.axis_label_text_font = "Anta"
    plot.yaxis.axis_label_text_font = "Anta"
    plot.xaxis.major_label_text_font = "Anonymous Pro" # font imported in html
    plot.yaxis.major_label_text_font = "Anonymous Pro"
    plot.xaxis.axis_label_text_font_style = "normal" # italic by default
    plot.yaxis.axis_label_text_font_style = "normal"
    plot.xaxis.axis_label_text_font_size = "0.8rem"
    plot.yaxis.axis_label_text_font_size = "0.8rem"
    plot.xaxis.major_label_text_font_size = "0.7rem"
    plot.yaxis.major_label_text_font_size = "0.7rem"

    # SALARY UNSPECIFIED BARS
    plot.vbar('x', top = 'salaryAvg', width = 0.70, source = sourceSalaryUnspecified, color=settings.CSS_VARIABLES["color-secondary"], alpha=0.4) # MAIN BAR
    plot.vbar('x', top = 'activeFor', y_range_name="y2", source = sourceSalaryUnspecified, width=0.90, color=settings.CSS_VARIABLES["color-tertiary"], alpha=0.05) # Active for
    # plot.segment(x0='x', y0='salaryMin', x1='x', y1='salaryMax', source=sourceSalaryUnspecified, line_width=2, color='black') #Error bar
    # SALARY SPECIFIED BARS
    plot.vbar('x', top = 'salaryAvg', width = 0.70, source = sourceSalarySpecified, color=settings.CSS_VARIABLES["color-primary"], alpha=0.8) # MAIN BAR
    plot.vbar('x', top = 'activeFor', y_range_name="y2", source = sourceSalarySpecified, width=0.90, color=settings.CSS_VARIABLES["color-tertiary"], alpha=0.05) # Active for
    plot.segment(x0='x', y0='salaryMin', x1='x', y1='salaryMax', source=sourceSalarySpecified, line_width=1.5, color=settings.CSS_VARIABLES["color-plot-error-bars"], alpha=0.9) #Error bar
    
    # @parameter = accessing ColumnDataSource parameter
    # {0.} = no decimals
    hoverTooltipSalarySpecified = """
    <strong> @title </strong>
    <style type="text/css">:host { 
        padding: 0.3rem; 
        border: none; 
        text-align: center; 
        background-color: var(--color-background-secondary);
        color: var(--color-text-primary);
    }</style> 

    <div style="
        margin: 0 !important;
        padding: 0.4rem;
        outline: none;
        background-color: var(--color-background-tertiary);
        color: var(--color-text-secondary); 
        font-family: Anta;
        font-size: 0.7rem;
    ">
        <strong>min/avg/max:</strong> @salaryMin{0.}/@salaryAvg{0.}/@salaryMax{0.} <br>
        <strong>active for:</strong> @activeFor days <br>
        <strong>offer index:</strong> @x <br>
    </div>"""

    hoverTooltipSalaryUnpecified = """
    <strong> @title </strong>
    <style type="text/css">:host { 
        padding: 0.3rem; 
        border: none; 
        text-align: center; 
        background-color: var(--color-background-secondary);
        color: var(--color-text-primary);
    }</style> 

    <div style="
        margin: 0 !important;
        padding: 0.4rem;
        border: none; 
        outline: none; 
        background-color: var(--color-background-secondary);
        color: var(--color-text-secondary); 
        font-family: Anta;
        font-size: 0.7rem;
    ">
        <strong>salary:</strong> unspecified <br>
        <strong>active for:</strong> @activeFor days <br>
        <strong>offer index:</strong> @x <br>
    </div>"""
    
    # this approach has no colors customization
    # hoverSalarySpecified = HoverTool(tooltips=[("Offer index:", "@x"), ("Job title:", "@title"), ("Min/Avg/Max:", "@salaryMin{0.}/@salaryAvg{0.}/@salaryMax{0.}"), ("Active for:", "@activeFor days")]) #{0} = no decimals
    
    hoverSalarySpecified = HoverTool(tooltips=hoverTooltipSalarySpecified)
    hoverSalaryUnpecified = HoverTool(tooltips=hoverTooltipSalaryUnpecified)
    hoverSalaryUnpecified.renderers = [plot.renderers[0]]# hover tool only on the salary bars
    hoverSalarySpecified.renderers = [plot.renderers[2]]# hover tool only on the salary bars

    taptool = TapTool() #highlight on tap
    wheelZoom = WheelZoomTool()
    plot.add_tools(hoverSalarySpecified, hoverSalaryUnpecified, taptool, wheelZoom) #wheelZoom removed for now
    plot.toolbar.active_scroll = wheelZoom
    
    return plot

def makeBokehTable(dataframe):

    dataframe = dataframe.replace({'^\s+': '', '\n': '<br>', '\t': '<br>'}, regex=True) # replace for HTML displaying. ^\s* matches zero or more whitespace characters at the beginning of a string
    dataframe = dataframe.fillna("") # Nones to empty strs - cleaner table

    # FORMAT SOME COLUMNS (change \n and \t to <br> as it wouldn't display a new line in the table cell div otherwise)
    columnsToFormatNewlines = ["salaryAndContract", "workModes", "positionLevels", "location", "techstackExpected", "techstackOptional", "responsibilities", "requirements", "optionalRequirements", "fullDescription"]

    for col in columnsToFormatNewlines:
        if col in dataframe.columns:
            dataframe[col] = dataframe[col].apply(lambda cellContent: f"<div style='overflow: auto; max-height: {settings.BOKEH_TABLE_ROW_HEIGHT}px;'>{cellContent}</div>")

    # dataframe = dataframe.map(lambda cellContent: f"<div style='overflow: auto; max-height: {BOKEH_TABLE_ROW_HEIGHT}px;'>{cellContent}</div>") # surround every cell content with div element to customize it (ENABLE SCROLLING)

    source = ColumnDataSource(dataframe)
    columns = []
    for column in dataframe.columns:
        if column == 'url': # to make a hyperlink
            columns.append(TableColumn(field=column, title=column, formatter=HTMLTemplateFormatter(template="""<a style='overflow: auto;' href="<%= value %>" target="_blank"><%= value %></a>""")))
        # elif column == 'requirements':
        else:
            # columns.append(TableColumn(field=column, title=column, formatter=HTMLTemplateFormatter(template="""<div style="background-color: rgb(29, 29, 29);" """)))
            columns.append(TableColumn(field=column, title=column, formatter=HTMLTemplateFormatter())) # HTMLTemplateFormatter to render <div> elements
    table = DataTable(source=source, columns=columns, sizing_mode="stretch_width", fit_columns=True) # editable=True. fit_columns=True = Ensure columns fit within the width

    # calculate table height
    height = settings.BOKEH_TABLE_ROW_HEIGHT * (len(dataframe)) # would display all without scrolling but it could get too long fast
    if height > settings.BOKEH_TABLE_MAX_HEIGHT:
        height = settings.BOKEH_TABLE_MAX_HEIGHT
    table.height = height
    table.row_height = settings.BOKEH_TABLE_ROW_HEIGHT
    # table.index_position = None # turns off indexes

    # A LOT OF INLINE STYLING BECAUSE TABLES DON'T SUPPORT PYTHON STYLING LIKE PLOTS DO
    BOKEH_TABLE_CSS = """
    /* GENERAL DIV */

    .bk-data-table * {
        font-size: 0.7rem;
        font-family: "Anonymous Pro", serif;
        font-weight: 100;
        background-color: var(--color-background-secondary);
        color: var(--color-text-secondary);
    }

    /* HEADER */
    
    /*center column name*/
    .slick-header-column {
        text-align: center !important;
    }
    .slick-header-column .slick-column-name {
        display: block;
        width: 100%;
        text-align: center;
    }

    .slick-header * {
        color: var(--color-text-primary);
        font-size: 0.8rem;
        font-weight: 600;
        background-color: var(--color-background-secondary) !important; /* header color */
    }
    .slick-column-name {
        background-color: rgba(0,0,0,0) !important; /* transparent for nicer higlighting*/
    }
    .slick-resizable-handle {
        background-color: rgba(0,0,0,0) !important; /* transparent for nicer higlighting*/
    }

    /* INDEX CELLS */
    .bk-cell-index {
        background-color: var(--color-background-secondary) !important;
        font-size: 0.8rem;
    }

    /* SPACES BETWEEN ROWS*/
    .ui-widget-content {
        background-color: var(--color-background-quaternary) !important;
    }

    /* HIGHLIGHT HEADER COLOR */
    .ui-state-hover {
        background-color: var(--color-primary) !important;
    }
                                
    /* EVEN/ODD ROWS COLORS */
    .even * {
        background-color: var(--color-background-secondary);
    }
    .odd * {
        background-color: var(--color-background-tertiary);
    }
                                
    /* SELECTION COLOR PARAMS*/
    .active, .selected {
        background-color: var(--color-table-selection) !important;
    }
                                
    /* CENTER TEXT INSIDE NORMAL CELLS */
    .slick-cell * { /* OK - centering normal cells text */
        text-align: center !important;
        background-color: rgba(0,0,0,0) !important;
    }

    /* HREF URL COLOR BEFORE VISIT */
    .slick-cell > a {
        color: var(--color-table-url-unvisited) !important;
    }

    /* VISITED URL COLOR */
    .slick-cell > a:visited {
        color: var(--color-table-url-visited) !important;
    }

    .slick-cell { /* CENTER CONTENT INSIDE CELL */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /****************************** SCROLLBAR STYLING ******************************/

    /* WEBKIT SCROLLBAR STYLING */
    ::-webkit-scrollbar {
        width: 0.95rem;
    }

    ::-webkit-scrollbar-thumb {
        background: var(--color-primary);
        /*border-radius: 20%;*/
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-secondary);
    }
    ::-webkit-scrollbar-track {
        background: var(--color-background-secondary);
    }

    /* Firefox Scrollbar Styling */
    html {
        scrollbar-color: var(--color-primary) var(--color-background-secondary);
        scrollbar-width: thin;
    }


    /* DISABLE CELLS SCROLLBARS VISIBILITY (overflow: auto set in bokeh python file) */
    .slick-cell::-webkit-scrollbar {
        display: none !important; /* For Chrome/Safari */
    }
    .slick-cell * {
        -ms-overflow-style: none !important; /* For Internet Explorer (IE) */
        scrollbar-width: none !important;    /* For Firefox */
    }

    /* SORTING INDICATOR - remove background */
    .slick-sort-indicator {
        background-color: rgba(0, 0, 0, 0) !important;
    }
    """

    # /* DISABLE MAIN TABLE SCROLLBARS VISIBILITY*/
    # .slick-viewport::-webkit-scrollbar {
    #     display: none !important; /* For Chrome/Safari */
    # }
    # .slick-viewport {
    #     background-color: rgba(0, 0, 0, 0.7); /* colors vertical lines on both sides */
    #     overflow: scroll !important;        /* Enable scrolling, but no visible scrollbar */
    #     -ms-overflow-style: none !important; /* For Internet Explorer (IE) */
    #     scrollbar-width: none !important;    /* For Firefox */
    # }

    tableStyle = InlineStyleSheet(css=BOKEH_TABLE_CSS)
    table.stylesheets = [tableStyle]

    return table