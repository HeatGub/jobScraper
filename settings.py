#############################################################################################
#                                                                                           #
#       JUST SAVE SETTINGS.PY FOR CHANGES TO TAKE EFFECT. NO NEED TO STOP RUNNING APP       #
#                   IF CSS_VARIABLES HAVE BEEN CHANGED REFRESH THE PAGE                     #
#                                                                                           #
#############################################################################################


######################################################## SELENIUM SETTINGS ########################################################

MAKE_BROWSER_INVISIBLE = False # justjoin HAS TO HAVE INVISIBLE (headless) OR ACTIVE (not minimized) window to fetch URLs list and/or some params

# changing window size might affect scraping speed due to changing page loading time
BROWSER_WINDOW_WIDTH_THEPROTOCOL = 1400 # integer [pixels] - let it wide, as some elements can not display otherwise
BROWSER_WINDOW_HEIGHT_THEPROTOCOL = 900 # integer [pixels]
BROWSER_WINDOW_WIDTH_JUSTJOIN = 800 # integer [pixels]
BROWSER_WINDOW_HEIGHT_JUSTJOIN = 900 # integer [pixels]

NO_NEW_RESULTS_COUNTER_LIMIT_JUSTJOIN = 4 # integer. SUGGESTING AT LEAST 3. How many times to retry scrolling if offers list has the same length as after the last try

# AVOID BOT CHECK BY WAITING FOR SOME SECONDS - how long to wait before scraping next offer/URLs page
# [a,b] means wait between a and b SECONDS - sleep(random.uniform(a,b)). Integers/floats but always 2 values
WAIT_URLS_JUSTJOIN = [0, 0] # rather not [0,0] as this site usually loads offers list really slowly
WAIT_OFFER_PARAMS_JUSTJOIN = [0, 0] # [0,0] worked well for me as this site also loads offers slowly xD so even at max speed bot check was never triggered

WAIT_URLS_THEPROTOCOL = [0, 0] # [0,0] worked well
WAIT_OFFER_PARAMS_THEPROTOCOL = [0.3, 0.5] # [0,0] sometimes triggers bot check

######################################################## PLOT AND TABLE SIZING ########################################################

BOKEH_PLOT_HEIGHT = 300 # integer [pixels]
BOKEH_TABLE_MAX_HEIGHT = 800 # integer [pixels]
BOKEH_TABLE_ROW_HEIGHT = 300 # integer [pixels]

######################################################## COLOR SETTINGS ########################################################
# those variables are delared as CSS root variables on flask root endpoint render. And bohek plot uses them in the below python dictionary form
# primary, secondary, tertiary, quaternary, quinary...
CSS_VARIABLES = {
    # # DARK PURPLE THEME
    # "color-primary": "rgba(99, 40, 210, 0.85)",
    # "color-secondary": "rgba(192, 9, 140, 0.8)",
    # "color-tertiary": "rgba(177, 255, 0, 0.8)",
    # "color-quaternary": "rgba(0, 142, 66, 0.8)",
    # "color-table-selection": "rgba(60,140,200,0.2)",

    # AQUAMARINE THEME
    "color-primary": "rgba(0, 203, 182, 0.8)",
    "color-secondary": "rgba(174, 0, 242, 0.85)",
    "color-tertiary": "rgba(255, 199, 0, 0.7)",
    "color-quaternary": "rgba(0, 145, 134, 0.8)",
    "color-table-selection": "rgba(0, 203, 182,0.15)",

    # DARK BACKGROUNDS
    "color-background-primary": "rgba(15,15,15,1)",
    "color-background-secondary": "rgba(25,25,25,1)",
    "color-background-tertiary": "rgba(35,35,35,1)",
    "color-background-quaternary": "rgba(60,60,60,1)",
    "color-background-quinary": "rgba(90,90,90,1)",

    "color-text-primary": "rgba(180,180,180,1)",
    "color-text-secondary": "rgba(200,200,200,1)",
    "color-text-tertiary": "rgba(160,160,160,1)",
    "color-text-warning": "rgba(255, 40, 40, 0.8)",

    # plot bars transparency setting (alpha) in makeBokehFigures
    "color-plot-error-bars": "rgba(20,20,20, 0.4)",
    "color-plot-grid-line": "rgba(100,100,100,0.9)",
    "color-plot-minor-grid-line": "rgba(80,80,80,0.3)",

    # "color-table-selection": "rgba(60,140,200,0.2)",
    "color-table-url-unvisited": "rgba(120, 120, 240, 1)",
    "color-table-url-visited": "rgba(80, 80, 180, 1)",
    
    "border-width-primary": "0.2rem",
    "border-width-secondary": "0.1rem",
    "border-width-tertiary": "0.07rem",

    "outline-width-primary": "0.15rem",

    "border-radius-primary":"0.4rem",
    "border-radius-secondary":"0.2rem",
    "border-radius-tertiary":"0.1rem",
}

######################################################## DATABASE ########################################################

GROSS_TO_NET_MULTIPLIER = 0.77 # floating point number like 0.77, 0.6 etc. It converts with (salaryNet = salaryGross * GROSS_TO_NET_MULTIPLIER) at the time of scraping, not on table display

# DATABASE_TABLE_NAME = 'table1' # values like 'table1'. Creates new table if it doesn't exist already
DATABASE_TABLE_NAME = 'test1' # 'test1' = populated test table

DATABASE_DEFAULT_INT = 'NULL' # '""' represents an empty string. Default value is used when value not provided
DATABASE_DEFAULT_TEXT = 'NULL' # Default value is used when value not provided

# adjust DATABASE_COLUMNS if you'd like different table structure. The below variables REQUIRE APP RESTART TO APPLY (as it's rarely modified)
# ⛔ CAUTION: it can cause problems on existing tables (running select query on columns which does not exist)
DATABASE_COLUMNS = [
    {"dbColumnName": "datetimeLast", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "last seen", "description":"'datetimeLast' - date and time when an offer was scraped for the last time"}, # don't remove this one tho as it's updated if offer url found in DB
    {"dbColumnName": "datetimeFirst", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "first seen", "description":"'datetimeFirst' - date and time when an offer was scraped for the first time"},
    {"dbColumnName": "url", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "URL", "description":"'url' - link to an offer"},
    {"dbColumnName": "title", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "job title", "description":"'title' - job title provided by employer"},
    {"dbColumnName": "salaryAndContract", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "salary & contract", "description":"'salaryAndContract' - salary and contract type"},
    {"dbColumnName": "salaryMin", "dataType": "INT", "default":DATABASE_DEFAULT_INT, "displayName": "salary min", "description":"'salaryMin' - minimal salary converted to [net PLN/month]"},
    {"dbColumnName": "salaryMax", "dataType": "INT", "default":DATABASE_DEFAULT_INT, "displayName": "salary max", "description":"'salaryMax' - maximum salary converted to [net PLN/month]"},
    {"dbColumnName": "employer", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "employer", "description":"'employer' - employer (or personal information collector)"},
    {"dbColumnName": "workModes", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "work modes", "description":"'workModes' - work modes (remote, hybrid, home office)"},
    {"dbColumnName": "positionLevels", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "position", "description":"'positionLevels' - position level(s), so called seniority (junior, mid, senior etc.)"},
    {"dbColumnName": "location", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "location", "description":"'location' - location(s) provided by employer"},
    {"dbColumnName": "techstackExpected", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "techstack expected", "description":"'techstackExpected' - expected techstack"},
    {"dbColumnName": "techstackOptional", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "techstack optional", "description":"'techstackOptional' - optional techstack"},
    {"dbColumnName": "responsibilities", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "responsibilities", "description":"'responsibilities' - what you're going to do, at least theoretically"},
    {"dbColumnName": "requirements", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "requirements", "description":"'requirements' - employer's requirements"},
    {"dbColumnName": "optionalRequirements", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "optional requirements", "description":"'optionalRequirements' - employer's optional requirements"},
    {"dbColumnName": "fullDescription", "dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT, "displayName": "full description", "description":"'fullDescription' - full description of a job offer, useful when more specific fields couldn't be scraped"},
]

doNotCountTheseColumnsOnNonesCheck = ['datetimeLast', 'datetimeFirst', 'url'] # check scrapToDatabase() functions for flow - these columns are never Nones because they don't rely on page elements

######################################################## MISC ########################################################

testBrowserUrlPlaceholder = 'testBrowserUrlPlaceholder' # no need to change it, just a process 'name'

DOCKERIZE_MODE_ACTIVE = False # KEEP IT FALSE, unless building linux docker image. Changes settings in main.py and SeleniumBrowser.py to fit docker (ubuntu) requirements