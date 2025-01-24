from bokeh.plotting import figure
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource, WheelZoomTool, HTMLTemplateFormatter, HoverTool, TapTool, Range1d, LinearAxis, InlineStyleSheet
from settings import BOKEH_PLOT_HEIGHT, BOKEH_TABLE_MAX_HEIGHT, BOKEH_TABLE_ROW_HEIGHT, BOKEH_TABLE_CSS, CSS_VARIABLES
from bokeh.themes import Theme
import pandas as pd

############################################################################# BOKEH FUNCITONS ###############################################################################
def makeBokehPlot(dataframe): #Only offers with specified salary?
    # len(dataframe) >=1 at this point 
    # dataframe already ordered by (salaryMin+SalaryMax)/2 ASC

    pd.options.mode.copy_on_write = True #recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
    pd.set_option('future.no_silent_downcasting', True)

    nonNanRowsDf = dataframe[dataframe['salaryMin'].notna()]
    nanRowsDf = dataframe[dataframe['salaryMin'].isna()]

    # SPECIFY UNSPECIFIED BARS HEIGHT
    if len(nonNanRowsDf) > 0: #otherwise division by 0 possible
        lookUpToValues = int(len(nonNanRowsDf)/4) #how many values to count average
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
    plot = figure(title="", x_axis_label='offer index', y_axis_label='salary [pln net/month]', height = BOKEH_PLOT_HEIGHT, sizing_mode='stretch_width')
    plot.add_layout(LinearAxis(y_range_name="y2", axis_label="days active"), 'right') # Add the second y-axis to the right. DONT MOVE IT - MAY BREAK CSS
    plot.y_range = Range1d(start=0 - 1, end=maxSalary) # * 1.2 to fit the bars
    plot.x_range = Range1d(start=0 - 1, end=int(len(dataframe))) #too much empty space by default
    plot.extra_y_ranges = {"y2": Range1d(start=0, end=maxActiveFor)} #add 1 day
      
    # COLOR SETTINGS
    plot.border_fill_color = CSS_VARIABLES['color-background-secondary'] # outside the plot area
    plot.background_fill_color = CSS_VARIABLES['color-background-tertiary'] # plot area
    # plot.background_fill_color = CSS_VARIABLES['primary-color'] # plot area

    plot.xaxis.axis_line_color = CSS_VARIABLES['color-plot-grid-line']
    plot.xaxis.major_tick_line_color = CSS_VARIABLES['color-plot-grid-line']
    plot.xaxis.minor_tick_line_color = CSS_VARIABLES['color-plot-grid-line']
    plot.yaxis.axis_line_color = CSS_VARIABLES['color-plot-grid-line']
    plot.yaxis.major_tick_line_color = CSS_VARIABLES['color-plot-grid-line']
    plot.yaxis.minor_tick_line_color = CSS_VARIABLES['color-plot-grid-line']

    plot.xgrid.grid_line_color = CSS_VARIABLES['color-plot-grid-line']
    plot.ygrid.grid_line_color = CSS_VARIABLES['color-plot-grid-line']
    plot.xgrid.minor_grid_line_color = CSS_VARIABLES['color-plot-minor-grid-line']
    plot.ygrid.minor_grid_line_color = CSS_VARIABLES['color-plot-minor-grid-line']

    plot.xaxis.axis_label_text_color = CSS_VARIABLES['color-text-primary']
    plot.yaxis.axis_label_text_color = CSS_VARIABLES['color-text-primary']
    plot.xaxis.major_label_text_color = CSS_VARIABLES['color-text-secondary']
    plot.yaxis.major_label_text_color = CSS_VARIABLES['color-text-secondary']
        
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
    plot.vbar('x', top = 'salaryAvg', width = 0.70, source = sourceSalaryUnspecified, color=CSS_VARIABLES["color-plot-salary-unspecified"]) # MAIN BAR
    plot.vbar('x', top = 'activeFor', y_range_name="y2", source = sourceSalaryUnspecified, color=CSS_VARIABLES["color-plot-salary-days-active"], width=0.90) # Active for
    # plot.segment(x0='x', y0='salaryMin', x1='x', y1='salaryMax', source=sourceSalaryUnspecified, line_width=2, color='black') #Error bar
    # SALARY SPECIFIED BARS
    plot.vbar('x', top = 'salaryAvg', width = 0.70, source = sourceSalarySpecified, color=CSS_VARIABLES["color-plot-salary-specified"]) # MAIN BAR
    plot.vbar('x', top = 'activeFor', y_range_name="y2", source = sourceSalarySpecified, color=CSS_VARIABLES["color-plot-salary-days-active"],  width=0.90) # Active for
    plot.segment(x0='x', y0='salaryMin', x1='x', y1='salaryMax', source=sourceSalarySpecified, line_width=1.5, color=CSS_VARIABLES["color-plot-error-bars"]) #Error bar
    
    taptool = TapTool() #highlight on tap
    wheel_zoom = WheelZoomTool()
    plot.toolbar.active_scroll = wheel_zoom
    hoverSalaryUnpecified = HoverTool(tooltips=[("Offer index:", "@x"), ("Job title:", "@title"), ("Salary:", "Unspecified"), ("Active for:", "@activeFor days")])
    hoverSalaryUnpecified.renderers = [plot.renderers[0]]# hover tool only on the salary bars
    hoverSalarySpecified = HoverTool(tooltips=[("Offer index:", "@x"), ("Job title:", "@title"), ("Min/Avg/Max:", "@salaryMin{0.}/@salaryAvg{0.}/@salaryMax{0.}"), ("Active for:", "@activeFor days")]) #{0} = no decimals
    hoverSalarySpecified.renderers = [plot.renderers[2]]# hover tool only on the salary bars
    plot.add_tools(hoverSalarySpecified, hoverSalaryUnpecified, taptool, wheel_zoom) #wheel_zoom removed for now
    
    return plot

def makeBokehTable(dataframe):

    dataframe = dataframe.replace({'^\s+': '', '\n': '<br>', '\t': '<br>'}, regex=True) # replace for HTML displaying. ^\s* matches zero or more whitespace characters at the beginning of a string
    dataframe = dataframe.fillna("") # Nones to empty strs - cleaner table

    # FORMAT SOME COLUMNS (change \n and \t to <br> as it wouldn't display a new line in the table cell div otherwise)
    columnsToFormatNewlines = ["salaryAndContract", "workModes", "positionLevels", "location", "techstackExpected", "techstackOptional", "responsibilities", "requirements", "optionalRequirements", "fullDescription"]

    for col in columnsToFormatNewlines:
        if col in dataframe.columns:
            dataframe[col] = dataframe[col].apply(lambda cellContent: f"<div style='overflow: auto; max-height: {BOKEH_TABLE_ROW_HEIGHT}px;'>{cellContent}</div>")

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
    table = DataTable(source=source, columns=columns, sizing_mode="stretch_width") #editable=True

    # calculate table height
    height = BOKEH_TABLE_ROW_HEIGHT * (len(dataframe)) # would display all without scrolling but it could get too long fast
    if height > BOKEH_TABLE_MAX_HEIGHT:
        height = BOKEH_TABLE_MAX_HEIGHT
    table.height = height
    table.row_height = BOKEH_TABLE_ROW_HEIGHT
    # table.index_position = None # turns off indexes

    tableStyle = InlineStyleSheet(css=BOKEH_TABLE_CSS)
    table.stylesheets = [tableStyle]

    return table