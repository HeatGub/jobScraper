from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn
from bokeh.models import ColumnDataSource, WheelZoomTool, HTMLTemplateFormatter, HoverTool, TapTool, Range1d, LinearAxis
from bokeh.io import curdoc #for dark theme
from settings import BOKEH_TABLE_HEIGHT, BOKEH_TABLE_ROW_HEIGHT

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
    table = DataTable(source=source, columns=columns, editable=True, sizing_mode="stretch_width")

    # Customize the theme for dark mode
    table.background = "black"  # Dark background
    table.height = BOKEH_TABLE_HEIGHT
    table.row_height = BOKEH_TABLE_ROW_HEIGHT

    return table