BROWSER_WINDOW_WIDTH = 700
BROWSER_WINDOW_HEIGHT = 500
GROSS_TO_NET_MULTIPLIER = 0.77 # values like 0.77 which is equal to 23% tax

DATABASE_TABLE_NAME = 'test5' # values like 'table1'. Creates new table if it doesn't exist already
DATABASE_DEFAULT_TEXT = '""'# '""' represents an empty string. Used when value not provided
DATABASE_DEFAULT_INT = 'NULL'# it's displayed as NULL in DB

# adjust DATABASE_COLUMNS if you'd like different table structure. 
# CAUTION: it could cause problem on existing tables (running select query on columns which does not exist)
DATABASE_COLUMNS = {
    "datetimeLast": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT}, # don't remove this one tho as it's updated if offer url found in DB
    "datetimeFirst": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "url": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "title": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "salaryAndContract": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "salaryMin": {"dataType": "INT", "default":DATABASE_DEFAULT_INT},
    "salaryMax": {"dataType": "INT", "default":DATABASE_DEFAULT_INT},
    "employer": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "workModes": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "positionLevels": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "location": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "techstackExpected": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "techstackOptional": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "responsibilities": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "requirements": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "optionalRequirements": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
    "fullDescription": {"dataType": "TEXT", "default":DATABASE_DEFAULT_TEXT},
}

makeBrowserInvisible = True # justjoin HAS TO HAVE INVISIBLE (headless) OR active (not minimized) window to work

testBrowserUrlPlaceholder = 'testBrowserUrlPlaceholder'