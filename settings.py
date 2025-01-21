BROWSER_WINDOW_WIDTH = 700
BROWSER_WINDOW_HEIGHT = 500
GROSS_TO_NET_MULTIPLIER = 0.77 # values like 0.77 which is equal to 23% tax



makeBrowserInvisible = False # justjoin HAS TO HAVE INVISIBLE (headless) OR ACTIVE (not minimized) window to work

testBrowserUrlPlaceholder = 'testBrowserUrlPlaceholder'

BOKEH_TABLE_HEIGHT = 800 # numeric values like 800. Changes Bokeh table height [pixels]
BOKEH_TABLE_ROW_HEIGHT = 25 # numeric values like 25. Changes row height [pixels]
BOKEH_TABLE_CSS = """
/* GENERAL DIV */
.bk-data-table * {
    font-size: 0.7rem;
    font-family: "Anonymous Pro", serif;
    font-weight: 100;
    background-color: rgba(200, 0, 0, 0); 
}

/* HEADER */
.slick-header * {
    font-size: 0.8rem;
    font-weight: 600;
    background-color: rgba(0, 0, 0, 0.7) !important; /* for nicer higlighting*/
}
.slick-column-name {
    background-color: rgba(200, 0, 0, 0) !important;
}

/* INDEX CELLS */
.bk-cell-index {
    background-color: rgba(0, 0, 0, 0.7) !important;
    font-size: 0.6rem;
}

/* SPACES BETWEEN ROWS*/
.ui-widget-content {
    background-color: rgba(60, 60, 140, 0.7) !important;
}

/* HIGHLIGHT HEADER COLOR */
.ui-state-hover {
    background-color: rgba(60, 60, 140, 0.7) !important;
}
                            
/* EVEN/ODD ROWS COLORS */
.even * {
    background-color: rgb(20, 20, 40);
}
.odd * {
    background-color: rgba(10, 10, 20);
}
                            
/* SELECTION COLOR PARAMS*/
.active, .selected {
    background-color: rgba(60, 60, 120, 0.6) !important;
}
                            
/* CENTER TEXT INSIDE NORMAL CELLS */
.slick-cell * { /* OK - centering normal cells text */
    text-align: center !important;
    background-color: rgba(10, 10, 20, 0) !important;
}

/* HREF URL COLOR BEFORE VISIT */
.slick-cell > a {
    color: rgba(120, 120, 240, 1) !important;
}

/* VISITED URL COLOR */
.slick-cell > a:visited {
    color: rgba(80, 80, 180, 1) !important;
}
                            
/* DISABLE SCROLLBARS */
.slick-viewport::-webkit-scrollbar {
    display: none; /* For Chrome/Safari */
}
.slick-viewport {
    width: 100%;
    height: 100%;
    overflow: scroll;        /* Enable scrolling, but no visible scrollbar */
    -ms-overflow-style: none; /* For Internet Explorer (IE) */
    scrollbar-width: none;    /* For Firefox */
}
"""




######################################################## DATABASE ########################################################

DATABASE_TABLE_NAME = 'test5' # values like 'table1'. Creates new table if it doesn't exist already
DATABASE_DEFAULT_TEXT = '""'# '""' represents an empty string. Used when value not provided
DATABASE_DEFAULT_INT = 'NULL'# it's displayed as NULL in DB

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