# SAVE SETTINGS AND RUN THE APP AGAIN FOR CHANGES TO TAKE EFFECT

makeBrowserInvisible = False # justjoin HAS TO HAVE INVISIBLE (headless) OR ACTIVE (not minimized) window to work

BROWSER_WINDOW_WIDTH = 700 # integer [pixels]
BROWSER_WINDOW_HEIGHT = 800 # integer [pixels]
GROSS_TO_NET_MULTIPLIER = 0.77 # values like 0.77 which is equal to 23% tax. It converts gross -> net at the time of scraping, not on table display

BOKEH_PLOT_HEIGHT = 300 # integer [pixels]
BOKEH_TABLE_MAX_HEIGHT = 700 # integer [pixels]
BOKEH_TABLE_ROW_HEIGHT = 100 # integer [pixels]

# primary, secondary, tertiary, quaternary, quinary, senary, septenary, octonary, nonary, and denary.
CSS_VARIABLES = {
    "color-primary": "rgba(60,140,200,1)",
    "color-secondary": "rgba(140,60,170,1)",
    "color-tertiary": "rgba(60,100,200,0.8)",
    "color-quaternary": "rgba(60,100,200,0.6)",

    "color-background-primary": "rgba(10,10,10,1)",
    "color-background-secondary": "rgba(25,25,25,1)",
    "color-background-tertiary": "rgba(35,35,35,1)",
    "color-background-quaternary": "rgba(60,60,60,1)",

    "color-text-primary":"rgba(180,180,180,1)",
    "color-text-secondary":"rgba(200,200,200,1)",
    "color-text-tertiary":"rgba(220,220,220,1)",
    "color-text-warning":"rgba(200,0,40,1)",

    # "color-button-text":"rgba(120,200,40,1)",
    "color-button-text":"rgba(100,180,40,1)",
    "color-button-background":"rgba(100,100,100,1)",
    "color-button-border":"rgba(158,158,158,1)",

    "color-plot-salary-specified":"rgba(60,60,160,1)",
    "color-plot-salary-unspecified":"rgba(60,60,160, 0.6)",
    "color-plot-salary-days-active":"rgba(30,150,3, 0.5)",
    "color-plot-error-bars":"rgba(20,20,20, 0.4)",
    "color-plot-grid-line":"rgba(100,100,100,0.9)",
    "color-plot-minor-grid-line":"rgba(80,80,80,0.3)",

    "color-table-selection": "rgba(60,140,200,0.2)",
    "color-table-url-unvisited": "rgba(120, 120, 240, 1)",
    "color-table-url-visited": "rgba(80, 80, 180, 1)",
    
    "border-radius-primary":"0.4rem",
    "border-radius-secondary":"0.2rem",
    "border-radius-tertiary":"0.1rem",
}

BOKEH_TABLE_CSS = """
/* GENERAL DIV */
.bk-data-table * {
    font-size: 0.7rem;
    font-family: "Anonymous Pro", serif;
    font-weight: 100;
    background-color: var(--color-background-primary);
}

/* HEADER */
.slick-header * {
    font-size: 0.8rem;
    font-weight: 600;
    background-color: var(--color-background-secondary) !important; /* header color */
}
.slick-column-name {
    background-color: rgba(0,0,0,0) !important; /* transparent for nicer higlighting*/
}

/* INDEX CELLS */
.bk-cell-index {
    background-color: var(--color-background-secondary) !important;
    font-size: 0.7rem;
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

                    
/* DISABLE MAIN TABLE SCROLLBARS VISIBILITY*/
.slick-viewport::-webkit-scrollbar {
    display: none !important; /* For Chrome/Safari */
}
.slick-viewport {
    background-color: rgba(0, 0, 0, 0.7); /* colors vertical lines on both sides */
    overflow: scroll !important;        /* Enable scrolling, but no visible scrollbar */
    -ms-overflow-style: none !important; /* For Internet Explorer (IE) */
    scrollbar-width: none !important;    /* For Firefox */
}


/* DISABLE CELLS SCROLLBARS VISIBILITY (overflow: auto set in bokeh python file) */
.slick-cell::-webkit-scrollbar {
    display: none !important; /* For Chrome/Safari */
}
.slick-cell * {
    -ms-overflow-style: none !important; /* For Internet Explorer (IE) */
    scrollbar-width: none !important;    /* For Firefox */
}

"""

######################################################## DATABASE ########################################################

DATABASE_TABLE_NAME = 'test6' # values like 'table1'. Creates new table if it doesn't exist already

DATABASE_DEFAULT_INT = 'NULL' # '""' represents an empty string. Default value is used when value not provided
DATABASE_DEFAULT_TEXT = 'NULL' # Default value is used when value not provided

# adjust DATABASE_COLUMNS if you'd like different table structure. 
# CAUTION: it could cause problem on existing tables (running select query on columns which does not exist)
DATABASE_COLUMNS = [
    {"dbColumnName": "datetimeLast", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "last seen", "description":"'datetimeLast' - last time seen"}, # don't remove this one tho as it's updated if offer url found in DB
    {"dbColumnName": "datetimeFirst", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "first seen", "description":"'datetimeFirst' - first time seen"},
    {"dbColumnName": "url", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "URL", "description":"'url' - link to an offer"},
    {"dbColumnName": "title", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "job title", "description":"'title' - job title"},
    {"dbColumnName": "salaryAndContract", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "salary & contract", "description":"'salaryAndContract' - salary and contract type"},
    {"dbColumnName": "salaryMin", "dataType": "INT", "default":DATABASE_DEFAULT_INT, "displayName": "salary min", "description":"'salaryMin' - minimal salary converted to [net PLN/month]"},
    {"dbColumnName": "salaryMax", "dataType": "INT", "default":DATABASE_DEFAULT_INT, "displayName": "salary max", "description":"'salaryMax' - maximum salary converted to [net PLN/month]"},
    {"dbColumnName": "employer", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "employer", "description":"'employer' - employer or juker"},
    {"dbColumnName": "workModes", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "work modes", "description":"'workModes' - work modes"},
    {"dbColumnName": "positionLevels", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "position", "description":"'positionLevels' - position level(s), so called seniority"},
    {"dbColumnName": "location", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "location", "description":"'location' - location(s)"},
    {"dbColumnName": "techstackExpected", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "techstack expected", "description":"'techstackExpected' - expected techstack"},
    {"dbColumnName": "techstackOptional", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "techstack optional", "description":"'techstackOptional' - optional techstack"},
    {"dbColumnName": "responsibilities", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "responsibilities", "description":"'responsibilities' - what you're going to do, at least theoretically"},
    {"dbColumnName": "requirements", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "requirements", "description":"'requirements' - employer's requirements"},
    {"dbColumnName": "optionalRequirements", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "optional requirements", "description":"'optionalRequirements' - employer's optional requirements"},
    {"dbColumnName": "fullDescription", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "full description", "description":"'fullDescription' - full description of a job offer, useful when more specific fields couldn't be scraped"},
]

testBrowserUrlPlaceholder = 'testBrowserUrlPlaceholder' # no need to change it, just a process 'name'