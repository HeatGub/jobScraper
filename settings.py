BROWSER_WINDOW_WIDTH = 700
BROWSER_WINDOW_HEIGHT = 500
GROSS_TO_NET_MULTIPLIER = 0.77 # values like 0.77 which is equal to 23% tax

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
    {"dbColumnName": "salaryMin", "dataType": "INT", "default":DATABASE_DEFAULT_INT, "displayName": "salary min", "description":"'salaryMin' - minimal salary"},
    {"dbColumnName": "salaryMax", "dataType": "INT", "default":DATABASE_DEFAULT_INT, "displayName": "salary max", "description":"'salaryMax' - maximum salary"},
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

makeBrowserInvisible = False # justjoin HAS TO HAVE INVISIBLE (headless) OR ACTIVE (not minimized) window to work

testBrowserUrlPlaceholder = 'testBrowserUrlPlaceholder'