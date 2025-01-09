from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
import time,json, random, re, datetime, inspect
from databaseFunctions import Database, columnsAll

##############################################################################
#                                                                            #
#    CHROMEDRIVER SHOULD MATCH BROWSER VERSION. IF OUTDATED DOWNLOAD FROM:   #
#    https://googlechromelabs.github.io/chrome-for-testing/                  #
#                                                                            #
##############################################################################

class SeleniumBrowser:
    def __init__(self):
        print('\tSeleniumBrowser __init__')
        self.DRIVER = None
        # self.BASE_URL = url
        self.BASE_URL = "https://theprotocol.it/filtry/ai-ml;sp/"
        # self.BASE_URL = "https://theprotocol.it/filtry/ai-ml;sp/bialystok;wp/stacjonarna;rw"

        #all of the below functions must return dictionary like          {'success':True, 'functionDone':False, 'message':'working'}
        self.scrapingFunctionsInOrder = [self.openBrowserIfNeeded, self.setCookiesFromJson, self.scrapUrlsFromAllThePages, self.scrapToDatabase]
        self.currentFunctionIndex = 0

        self.currentlyScrapedPageIndex = 1 #theprotocol starts page enumeration with 1
        self.OFFERS_URLS = [] # appended in scrapUrlsFromAllThePages()

        self.currentlyScrapedOfferIndex = 0
        self.databaseInserts = 0
        self.databaseUpdates = 0

    def isBrowserOpen(self):
        # print('\tisBrowserOpen')
        if self.DRIVER:
            try:
                self.DRIVER.current_url
                # print(self.DRIVER.current_url)
                return True
            except WebDriverException as e:
                print(e)
                return False
        else:
            return False
        
    def openBrowserIfNeeded(self):
        if not self.isBrowserOpen():
            return self.openBrowser() #opens browser and returns object like {'success':True, 'functionDone':False, 'message':'msg''}
        elif self.isBrowserOpen():
            return {'success':True, 'functionDone':True, 'message':'browser is already running'}

    def saveCookiesToJson(self):
        if self.isBrowserOpen():
            return self.saveCookiesToJson()
        else:
            return {'success':False, 'functionDone':True, 'message':'open selenium browser first'}
    
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
        try:
            seleniumCookies = self.DRIVER.get_cookies() # get cookies for a currently open domain
            seleniumCookiesDomain = seleniumCookies[0]['domain'] # single one is enough, domain is the same for all of them
            seleniumCookiesDomain = re.sub(r'^www\.', '', seleniumCookiesDomain)
            seleniumCookiesDomain = re.sub(r'^\.', '', seleniumCookiesDomain)
            # print(seleniumCookiesDomain)
            updatedCookiesList = []

            with open("cookies.json", "r") as cookiesFile:
                try:
                    cookiesFileData = json.load(cookiesFile) # will load if JSON is valid
                except:
                    with open("cookies.json", "w") as outputFile: # OVERWRITES cookies.json as it's not valid JSON
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

            print(len(cookiesFileData))
            print(len(updatedCookiesList))

            with open("cookies.json", "w") as outputFile: # OVERWRITES cookies.json, but updatedCookiesList contains cookies from the file
                outputFile.write(json.dumps(updatedCookiesList, indent=4))
            return {'success':True, 'functionDone':True, 'message':'cookies.json for '+ seleniumCookiesDomain +' updated'}
        
        except Exception as exception:
            return {'success':False, 'functionDone':False, 'message':str(exception)}

    def openBrowser(self):
        self.currentFunctionIndex = 0
        try:
            # SELENIUM CHROME DRIVER SETTINGS
            service = Service(executable_path="chromedriver.exe")
            chrome_options = Options()
            chrome_options.add_argument("--disable-search-engine-choice-screen")
            chrome_options.add_argument("window-size=700,900")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) #disable error logging
            # chrome_options.add_experimental_option("detach", True) # to keep browser open after python script execution ended. Not needed anymore?
            self.DRIVER = webdriver.Chrome(service=service, options=chrome_options) #Selenium opens a new browser window whenever it initializes a WebDriver instance
            self.DRIVER.get("https://google.com")
            return {'success':True, 'functionDone':True, 'message':'opened a selenium browser'}
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
            with open('cookies.json', 'r', newline='') as inputdata:
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
            return {'success':False, 'functionDone':True, 'message':str(exception)} # 'functionDone':True because it's not necessary


    ########################################################################### Scrap offer URLs from all the pages ###########################################################################
    def foundOfferOnThePage(self):
        try:
            self.DRIVER.find_element(By.CSS_SELECTOR, '#main-offers-listing > div.hfenof > div.t2re51w > div')
            return False #if no offer specific div found
        except:
            return True
    
    def scrapOffersUrlsFromSinglePage(self):
        try:
            offersContainer = self.DRIVER.find_element("xpath", '//*[@id="main-offers-listing"]/div[1]/div')
            offers = offersContainer.find_elements(By.CLASS_NAME, 'a4pzt2q ')
            # offers = offersContainer.find_elements(By.CSS_SELECTOR, '#offer-title') #also works
            # print('\t'+ str(len(offers)) + ' offers:')
            for offer in offers:
                self.OFFERS_URLS.append(offer.get_property("href"))
            return {'success':True, 'functionDone':True, 'message': 'page ' + str(self.currentlyScrapedPageIndex) + ' offers scraped'}
        except:
            return {'success':False, 'functionDone':False, 'message': 'probably too high request frequency triggered bot check'}
   
    def scrapUrlsFromAllThePages(self):
        try:
            self.DRIVER.get(self.BASE_URL + "?pageNumber=" + str(self.currentlyScrapedPageIndex))
            if not self.foundOfferOnThePage():
                return {'success':True, 'functionDone':True, 'message': 'URLs scraping done. Scraped ' + str(len(self.OFFERS_URLS))+' offer urls in total'}
            elif self.foundOfferOnThePage():
                time.sleep(random.uniform(0.5, 1)) #humanize
                if self.scrapOffersUrlsFromSinglePage()['success'] == True:
                    self.currentlyScrapedPageIndex += 1
                    return {'success':True, 'functionDone':False, 'message': 'page ' + str(self.currentlyScrapedPageIndex -1) + ' urls fetched'} # -1 because starting from 1 and incremented just above
        except Exception as exception:
            return {'success':False, 'functionDone':False, 'message':str(exception)}
            
    ########################################################################### Analyse offer functions ###########################################################################
    def offerNotFound(self):
        try:
            self.DRIVER.find_element("xpath", '//*[@data-test="text-offerNotFound"]')
            return True
        except:
            return False

    def getOfferDetails(self):
        #JOB TITLE
        try:
            jobTitle = self.DRIVER.find_element(By.XPATH, '//*[@data-test="text-offerTitle"]') # this element should always exist
            jobTitle = jobTitle.text
        except:
            jobTitle= ''
        
        #SALARY
        try:
            salaryContainer = self.DRIVER.find_element(By.XPATH, '//*[@data-test="section-contract"]') # this element should always exist
            salaryAndContract = salaryContainer.text
            # print(salaryAndContract  + '\n')
        except:
            salaryAndContract= ''
        
        salaryMinAndMax = [None, None] # Nones as these are INTs in DB
        if salaryAndContract != '':
            try: #to recalculate salary to [PLN/month net] #PLN=only unit on protocol?
                grossToNetMultiplier = 0.7
                hoursPerMonthInFullTimeJob = 168
                lines = salaryAndContract.splitlines()
                if len(lines) >= 3: #should be 2-3 tho
                    lines[0] = lines[0].replace(" ", "") #remove spaces
                    lines[0] = re.sub(r",\d{1,2}", '', lines[0]) #removes dash and /d x(1-2)  (needed when salary as 123,45)
                    salaryMinAndMax = re.findall(r"\d+", lines[0]) #r = raw
                    # print(salaryMinAndMax.split(',', 1)[0])
                    # salaryUnit = re.findall(r"[^\d–-]", lines[0]) #[exclude digits and –/-]
                    # salaryUnit = ''.join(salaryUnit) #join list elements
                    if re.findall("brutto", lines[1]) or re.findall("gross", lines[1]): # gross -> net
                        salaryMinAndMax = [(float(elmnt) * grossToNetMultiplier) for elmnt in salaryMinAndMax]
                        # print(salaryMinAndMax)
                    if re.findall("godz", lines[1]) or re.findall("hr.", lines[1]): # hr -> month
                        salaryMinAndMax = [(float(elmnt) * hoursPerMonthInFullTimeJob) for elmnt in salaryMinAndMax] #possible input float/str

                    salaryMinAndMax = [int(elmnt) for elmnt in salaryMinAndMax] # to ints
            except:
                pass    # salaryMinAndMax = [None, None]

        # EMPLOYER
        try:
            employerElement = self.DRIVER.find_element("xpath", '//*[@data-test="anchor-company-link"]') # this element should always exist
            employer = employerElement.text + ' ' + employerElement.get_property("href")
        except:
            employer= ''
        # print(employer  + '\n')
        
        #WORKFROM, EXP, VALIDTO, LOCATION - "PARAMETERS"
        workModes, positionLevels, offerValidTo, location = '', '', '', ''
        try:
            parametersContainer = self.DRIVER.find_element(By.CLASS_NAME, "c21kfgf")
            parameters = parametersContainer.find_elements(By.CLASS_NAME, "s1bu9jax")
            for param in parameters:
                paramType = param.get_attribute("data-test") #element description
                match paramType:
                    case "section-workModes":
                        workModes = param.text
                    case "section-positionLevels":
                        positionLevels = param.text
                    case "section-offerValidTo":
                        offerValidTo = param.text
                    case "section-workplace":
                        location = param.text
                        try: #to find and click 'more locations' button then fetch what's inside
                            moreLocations = self.DRIVER.find_element("xpath", '//*[@data-test="button-locationPicker"]')
                            moreLocations.click()
                            # time.sleep(0.05) #probably necessary
                            locations = moreLocations.find_element("xpath", '//*[@data-test="modal-locations"]')
                            location = locations.text
                        except:
                            pass #leave location as it was
            # print(workModes + '\n\n' + positionLevels + '\n\n' +  offerValidTo + '\n\n' +  location + '\n')
        except:
            pass # leave ''s

        #TECHSTACK
        techstackExpected, techstackOptional = '', ''
        try:
            descriptionsContainer = self.DRIVER.find_element(By.CSS_SELECTOR, '#TECHNOLOGY_AND_POSITION')
            techstack = descriptionsContainer.find_elements(By.CLASS_NAME, "c1fj2x2p")
            for group in techstack:
                if group.text[0:8] == 'EXPECTED' or group.text[0:8] == 'WYMAGANE': # eng/pl same word length
                    techstackExpected = group.text[9:]
                elif group.text[0:8] == 'OPTIONAL':
                    techstackOptional = group.text[9:]
                elif group.text[0:13] == 'MILE WIDZIANE': # polish version
                    techstackOptional = group.text[14:]
            # print(str(techstackExpected) + '\n\n' + str(techstackOptional) + '\n')
        except:
            pass # leave ''s

        #RESPONSIBILITIES
        try:
            try:
                responsibilities = descriptionsContainer.find_element("xpath", '//*[@data-test="section-responsibilities"]/ul').text #/only ul elements
            except:
                responsibilities = descriptionsContainer.find_element("xpath", '//*[@data-test="section-responsibilities"]').text #/if it's a single entry
        except:
            responsibilities= ''
            # print('RESPONSIBILITIES:\n' + str(responsibilities) + '\n' + driver.current_url)

        #REQUIREMENTS
        try:
            try:
                requirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements"]/ul').text
            except:
                requirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements"]').text #/if it's a single entry
        except:
            requirements= ''
            # print('REQUIREMENTS:\n' + str(requirements) + '\n' + driver.current_url)


        #OPTIONAL REQUIREMENTS
        try:
            optionalRequirementsContainer = descriptionsContainer.find_elements("xpath", '//*[@data-test="section-requirements-optional"]/li')
            if len(optionalRequirementsContainer) > 0:
                optionalRequirements = ''
                for optionalRequirement in optionalRequirementsContainer:
                    optionalRequirements += optionalRequirement.text + '\n'
            elif len(optionalRequirementsContainer) <= 0:
                try:
                    optionalRequirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements-optional"]').text
                except:
                    optionalRequirements= ''
                    # print('OPTIONAL:\n' + str(optionalRequirements) + '\n' + driver.current_url)        
        except:
            optionalRequirements= ''
        # print('OPTIONAL:\n' + str(optionalRequirements) + '\n' + driver.current_url)
        datetimeNow = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return [datetimeNow, datetimeNow, self.DRIVER.current_url, jobTitle, salaryAndContract, salaryMinAndMax[0], salaryMinAndMax[1], employer, workModes, positionLevels, offerValidTo, location, techstackExpected, techstackOptional, responsibilities, requirements, optionalRequirements]

    ########################################################################### Scraping to Database ###########################################################################

    def scrapToDatabase(self):
        try:
            # FINISH CONDITIONS
            if len(self.OFFERS_URLS) == 0:
                return {'success':True, 'functionDone':True, 'message':'no offers to analyse'}
            elif int(self.currentlyScrapedOfferIndex +1) > int(len(self.OFFERS_URLS)):
                    print(str(self.databaseInserts) + ' inserts | ' + str(self.databaseUpdates) + ' updates')
                    return {'success':True, 'functionDone':True, 'message': 'SCRAPING DONE. ' + str(self.databaseInserts) + ' inserts | ' + str(self.databaseUpdates) + ' updates'}
            # IF NOT FINISHED
            else:
                self.DRIVER.get(self.OFFERS_URLS[self.currentlyScrapedOfferIndex])
                if not self.offerNotFound():
                    resultsList = self.getOfferDetails()
                    outputDictionary = {}
                    for column, offerDetail in zip(columnsAll, resultsList):
                        outputDictionary[column] = offerDetail #combine 2 lists into 1 dictionary
                    # before = time.time()
                    if Database.recordFound(self.DRIVER.current_url):
                        Database.updateDatetimeLast(self.DRIVER.current_url)
                        self.databaseUpdates += 1
                    else:
                        Database.insertRecord(outputDictionary) # insert into database
                        self.databaseInserts += 1
                    self.currentlyScrapedOfferIndex += 1 # increment if successfully analysed
                    return {'success':True, 'functionDone':False, 'message': str(self.currentlyScrapedOfferIndex) + '/' + str(len(self.OFFERS_URLS)) + ' offers analysed'}
                elif self.offerNotFound():
                    # print('OFFER NOT FOUND: ' +  self.DRIVER.current_url)
                    self.currentlyScrapedOfferIndex += 1 # increment even if offer not found not to get stuck
                    return {'success':False, 'functionDone':False, 'message': 'OFFER NOT FOUND: ' +  self.DRIVER.current_url}
        except Exception as exception:
            return {'success':False, 'functionDone':False, 'message':str(exception)}
    
    def fullScraping(self):
        print('FULL SCRAPING SELENIUM')
        # getScrapingStatus()

        if self.currentFunctionIndex != 0:
            self.openBrowserIfNeeded() # it's for currentFunctionIndex == 0

        # SCRAPING FUNCTIONS IN ORDER: [openBrowserIfNeeded, self.setCookiesFromJson, self.scrapUrlsFromAllThePages, self.scrapToDatabase]
        functionResultDict = self.scrapingFunctionsInOrder[self.currentFunctionIndex]() # RUN CURRENT FUNCTION AND GET RESULTS

        if   (functionResultDict['functionDone'] == True) and ((self.currentFunctionIndex +1) <  len(self.scrapingFunctionsInOrder)):
            self.currentFunctionIndex +=1            # SINGLE FUNCTION DONE
        elif (functionResultDict['functionDone'] == True) and ((self.currentFunctionIndex +1) >= len(self.scrapingFunctionsInOrder)):
            self.resetScrapingFunctionsProgress()    # ALL FUNCTIONS DONE
            # functionResultDict = {'success':True, 'functionDone':True, 'message':'EXIT SIGNAL'} # signal to JS to stop fetching

        print('\t\t\t' + str(functionResultDict))
        # getScrapingStatus()
        return functionResultDict