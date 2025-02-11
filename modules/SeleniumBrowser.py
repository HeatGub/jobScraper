from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
import json, re
from pathlib import Path
import modules.theprotocol as theprotocol
import modules.justjoin as justjoin
from settings import MAKE_BROWSER_INVISIBLE, BROWSER_WINDOW_WIDTH_THEPROTOCOL, BROWSER_WINDOW_HEIGHT_THEPROTOCOL, BROWSER_WINDOW_WIDTH_JUSTJOIN, BROWSER_WINDOW_HEIGHT_JUSTJOIN, DOCKERIZE_MODE_ACTIVE, testBrowserUrlPlaceholder

##############################################################################
#                                                                            #
#    CHROMEDRIVER SHOULD MATCH BROWSER VERSION. IF OUTDATED DOWNLOAD FROM:   #
#    https://googlechromelabs.github.io/chrome-for-testing/                  #
#                                                                            #
##############################################################################

class SeleniumBrowser:
    def __init__(self, baseUrl):
        # print('\tSeleniumBrowser __init__')
        self.DRIVER = None
        self.BASE_URL = baseUrl # passed to worker # self.BASE_URL = "https://theprotocol.it/filtry/ai-ml;sp/"
        
        # CHECK DOMAIN TO ASSIGN PROPER FUNCTIONS AND VARIABLES
        # all of the below functions must return dictionary like          {'success':True, 'functionDone':False, 'message':'working'}
        if "theprotocol.it" in str(self.BASE_URL):
            self.scrapingFunctionsInOrder = [self.openBrowserIfNeeded, self.setCookiesFromJson, theprotocol.scrapUrlsFromAllThePages, theprotocol.scrapToDatabase]
            self.BROWSER_WINDOW_WIDTH = BROWSER_WINDOW_WIDTH_THEPROTOCOL
            self.BROWSER_WINDOW_HEIGHT = BROWSER_WINDOW_HEIGHT_THEPROTOCOL
        elif "justjoin.it" in str(self.BASE_URL): 
            self.scrapingFunctionsInOrder = [self.openBrowserIfNeeded, self.setCookiesFromJson, justjoin.scrapAllOffersUrls, justjoin.scrapToDatabase]
            self.BROWSER_WINDOW_WIDTH = BROWSER_WINDOW_WIDTH_JUSTJOIN
            self.BROWSER_WINDOW_HEIGHT = BROWSER_WINDOW_HEIGHT_JUSTJOIN
        elif testBrowserUrlPlaceholder in str(self.BASE_URL):
            self.BROWSER_WINDOW_WIDTH = BROWSER_WINDOW_WIDTH_JUSTJOIN # this one for example
            self.BROWSER_WINDOW_HEIGHT = BROWSER_WINDOW_HEIGHT_JUSTJOIN
        else:
            self.scrapingFunctionsInOrder = [self.returnIncorrectDomainDictionary] # looks strange but __init__ can only return None

        self.currentFunctionIndex = 0
        
        self.OFFERS_URLS = [] # appended in scrapUrlsFromAllThePages() #[{'index':'3', 'url':'https...'}, {}, ...] 

        self.currentlyScrapedPageIndex = 1 # theprotocol starts page enumeration with 1
        self.currentlyScrapedOfferIndex = 0 # THEPROTOCOL

        self.noNewResultsCounter = 0 # JUSTJOIN
        self.lastSeenIndex = 0 # JUSTJOIN

        self.databaseInserts = 0
        self.databaseUpdates = 0
        # print(self.BASE_URL)
    
    def returnIncorrectDomainDictionary(self):
        return {'success':False, 'functionDone':True, 'message':'only scraping theprotocol.it and justjoin.it for now', 'killProcess':True} # killProcess - incorrect URL provided

    def isBrowserOpen(self):
        # print('\tisBrowserOpen')
        if self.DRIVER:
            try:
                self.DRIVER.current_url
                # print(self.DRIVER.current_url)
                return True
            except WebDriverException as exception:
                # print(exception)
                return False
        else:
            return False
        
    def openBrowserIfNeeded(self):
        if not self.isBrowserOpen():
            return self.openBrowser() #opens browser and returns object like {'success':True, 'functionDone':False, 'message':'msg''}
        elif self.isBrowserOpen():
            return {'success':True, 'functionDone':True, 'message':'browser open'}
    
    def openBrowser(self):
        self.currentFunctionIndex = 0 # doesn't reset each function's progress
        try:
            # SELENIUM CHROME DRIVER SETTINGS
            chromeOptions = Options()
            chromeOptions.add_argument("--disable-search-engine-choice-screen")
            chromeOptions.add_argument("window-size="+str(self.BROWSER_WINDOW_WIDTH)+","+str(self.BROWSER_WINDOW_HEIGHT))
            chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging']) # disable error logging
            # MAKE BROWSER INVISIBLE (HEADLESS)
            if self.BASE_URL != testBrowserUrlPlaceholder and MAKE_BROWSER_INVISIBLE == True:
                chromeOptions.add_argument('--headless')

            # DOCKER (UBUNTU) REQUIREMENTS
            if DOCKERIZE_MODE_ACTIVE == True:
                chromeOptions.add_argument("--headless")  # Run Chrome in headless mode (remove if you need UI)
                chromeOptions.add_argument("--no-sandbox")  # Required in Docker
                chromeOptions.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
                chromeOptions.add_argument("--disable-gpu")  # Disable GPU acceleration
                chromeOptions.binary_location = "/usr/bin/google-chrome" # linux command: which google-chrome
                service = Service("/usr/local/bin/chromedriver-linux64/chromedriver") # specified in dockerfile (linux)
            # WINDOWS REQUIREMENTS
            else:
                service = Service(executable_path="chromedriver.exe") 

            self.DRIVER = webdriver.Chrome(service=service, options=chromeOptions) # Selenium opens a new browser window whenever it initializes a WebDriver instance
            self.DRIVER.get("https://theprotocol.it")
            return {'success':True, 'functionDone':True, 'message':'opened a selenium browser'}
        except Exception as exception:
            # usually triggered when driver and browser versions don't match 
            return {'success':False, 'functionDone':False, 'message':str(exception), 'pauseProcess':True}
    
    def closeBrowser(self):
        try:
            self.DRIVER.quit()
            return {'success':True, 'functionDone':True, 'message':'closed a broswer'}
        except Exception as exception: # if exception it is closed already anyway
            return {'success':False, 'functionDone':True, 'message':str(exception)}
    
    def getScrapingStatus(self):
        if ((self.currentFunctionIndex +1) <= len(self.scrapingFunctionsInOrder)):
            print()
            # print('currentFunctionIndex: ' + str(self.currentFunctionIndex))
            print('currentFunctionName: ' + str(self.scrapingFunctionsInOrder[self.currentFunctionIndex]))
            print()
    
    def resetScrapingFunctionsProgress(self):
        self.currentFunctionIndex = 0
        self.currentlyScrapedPageIndex = 1
        self.OFFERS_URLS = []
        self.currentlyScrapedOfferIndex = 0
        self.databaseInserts = 0
        self.databaseUpdates = 0
                
    def saveCookiesToJson(self):
        if not self.isBrowserOpen():
            return {'success':False, 'functionDone':True, 'message':'open selenium browser first'}
        try:
            seleniumCookies = self.DRIVER.get_cookies() # get cookies for a currently open domain
            seleniumCookiesDomain = seleniumCookies[0]['domain'] # single one is enough, domain is the same for all of them
            seleniumCookiesDomain = re.sub(r'^www\.', '', seleniumCookiesDomain)
            seleniumCookiesDomain = re.sub(r'^\.', '', seleniumCookiesDomain)
            # print(seleniumCookiesDomain)
            updatedCookiesList = []

            # Create cookies.json file if it doesn't exist
            filePathStr = "other/cookies.json"
            filePath = Path(filePathStr)
            if not filePath.exists():
                filePath.write_text("{}")  # Writes an empty JSON object

            # Read the file
            with filePath.open("r") as cookiesFile:
                try:
                    cookiesFileData = json.load(cookiesFile) # will load if JSON is valid
                except:
                    with open(filePathStr, "w") as outputFile: # OVERWRITES cookies.json as it's not valid JSON
                        outputFile.write(json.dumps(seleniumCookies, indent=4))
                        return {'success':True, 'functionDone':True, 'message':'cleared file and saved cookies for '+ seleniumCookiesDomain}
                # if cookiesFileData ok
                for cookie in cookiesFileData:
                    domain = cookie['domain']
                    domain = re.sub(r'^www\.', '', domain)
                    domain = re.sub(r'^\.', '', domain)
                    if domain != seleniumCookiesDomain:
                        updatedCookiesList.append(cookie) # append only onther domains, this one will be appended in the end
                updatedCookiesList = updatedCookiesList + seleniumCookies # merge lists

            # print(len(cookiesFileData))
            # print(len(updatedCookiesList))

            with open(filePathStr, "w") as outputFile: # OVERWRITES cookies.json, but updatedCookiesList contains cookies from the file
                outputFile.write(json.dumps(updatedCookiesList, indent=4))
            return {'success':True, 'functionDone':True, 'message':'cookies.json for '+ seleniumCookiesDomain +' updated'}
        
        except Exception as exception:
            return {'success':False, 'functionDone':False, 'message':str(exception)}

    def setCookiesFromJson(self):  
        try:
            self.DRIVER.get(self.BASE_URL) #RUN BROWSER
            currentUrlDomain = self.DRIVER.current_url
            currentUrlDomain = re.search(r'^https?://([^/]+)', currentUrlDomain)
            currentUrlDomain = currentUrlDomain.group(1)  
            currentUrlDomain = re.sub(r'^www\.', '', currentUrlDomain)
            currentUrlDomain = re.sub(r'^\.', '', currentUrlDomain)
            # print(currentUrlDomain)
            with open('other/cookies.json', 'r', newline='') as inputdata:
                cookies = json.load(inputdata)
                cookiesAdded = 0
                for cookie in cookies: #works only after driver.get
                    if re.match(r".?"+currentUrlDomain, cookie['domain']): # can only add cookies for current domain
                        self.DRIVER.add_cookie(cookie)
                        cookiesAdded += 1
                if cookiesAdded > 0:
                    self.DRIVER.refresh() # to load cookies
                    return {'success':True, 'functionDone':True, 'message':'cookies for ' + currentUrlDomain + ' successfully set'}
                elif (cookiesAdded == 0):
                    return {'success':False, 'functionDone':True, 'message':'no cookies for ' + currentUrlDomain + ' found in cookies.json'}
        except Exception as exception:
            return {'success':False, 'functionDone':True, 'message':str(exception), 'killProcess':True} # killProcess on error as most likely wrong URL was provided 

    def fullScraping(self):
        # print('FULL SCRAPING SELENIUM')
        # self.getScrapingStatus()

        if self.currentFunctionIndex != 0:
            self.openBrowserIfNeeded() # it's for currentFunctionIndex == 0

        # SCRAPING FUNCTIONS IN ORDER: [self.openBrowserIfNeeded, self.setCookiesFromJson, theprotocol.scrapUrlsFromAllThePages, theprotocol.scrapToDatabase]
        if self.currentFunctionIndex < 2:
            functionResultDict = self.scrapingFunctionsInOrder[self.currentFunctionIndex]() # RUN CURRENT FUNCTION AND GET RESULTS
        elif self.currentFunctionIndex >= 2: # need to pass seleniumBrowser instance (self) to the last 2 funcitons
            functionResultDict = self.scrapingFunctionsInOrder[self.currentFunctionIndex](self) # RUN CURRENT FUNCTION AND GET RESULTS

        if   (functionResultDict['functionDone'] == True) and ((self.currentFunctionIndex +1) <  len(self.scrapingFunctionsInOrder)):
            self.currentFunctionIndex +=1              # SINGLE FUNCTION DONE
        elif (functionResultDict['functionDone'] == True) and ((self.currentFunctionIndex +1) >= len(self.scrapingFunctionsInOrder)):
            self.resetScrapingFunctionsProgress()      # ALL FUNCTIONS DONE
            # functionResultDict['killProcess'] = True   # KILL THE PROCESS SIGNAL

        # print('\t\t' + str(functionResultDict))
        # self.getScrapingStatus()
        return functionResultDict