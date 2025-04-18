from selenium.webdriver.common.by import By
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
import time, random, re, datetime
from modules.Database import Database
import settings
import importlib

# theprotocol is being scraped well even when browser is minimized

########################################################################### Scrap offer URLs from all the pages ###########################################################################

# def foundOffersListOnThePage(SeleniumBrowser): # SITE UPDATED 27.01
#     try:
#         SeleniumBrowser.DRIVER.find_element("xpath", '//*[@id="main-offers-listing"]/div[1]/div')
#         return True #if offer specific div found
#     except:
#         return False

def foundOffersListOnThePage(SeleniumBrowser):
    try:
        SeleniumBrowser.DRIVER.find_element("xpath", "//div[@data-test='text-emptyList']")
        return False # empty list div found
    except:
        try:
            SeleniumBrowser.DRIVER.find_element("xpath", "//*[@id='main-offers-listing']")
            return True # empty list div not found and offers list found
        except Exception as exception:
            # print(exception)
            return False

def scrapOffersUrlsFromSinglePage(SeleniumBrowser):
    try:
        offersContainer = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@id="main-offers-listing"]/div[1]/div')
        offers = offersContainer.find_elements(By.CLASS_NAME, 'a4pzt2q ')
        # offers = offersContainer.find_elements(By.CSS_SELECTOR, '#offer-title') #also works
        # print('\t'+ str(len(offers)) + ' offers:')
        for offer in offers:
            SeleniumBrowser.OFFERS_URLS.append({'url':offer.get_property("href"), 'index':len(SeleniumBrowser.OFFERS_URLS)}) # just some index as theprotocol doesn't use that
        return {'success':True, 'functionDone':True, 'message': 'page ' + str(SeleniumBrowser.currentlyScrapedPageIndex) + ' offers scraped'}
    except:
        return {'success':False, 'functionDone':False, 'message': 'probably too high request frequency triggered bot check'}

def scrapUrlsFromAllThePages(SeleniumBrowser):
    try:
        SeleniumBrowser.DRIVER.get(SeleniumBrowser.BASE_URL + "?pageNumber=" + str(SeleniumBrowser.currentlyScrapedPageIndex))
        if not foundOffersListOnThePage(SeleniumBrowser) and len(SeleniumBrowser.OFFERS_URLS) == 0:
            return {'success':False, 'functionDone':True, 'message': 'no offers found on ' + SeleniumBrowser.BASE_URL, 'killProcess': True} # terminate the process if no offers found
        elif not foundOffersListOnThePage(SeleniumBrowser):
            return {'success':True, 'functionDone':True, 'message': 'URLs scraping done. Scraped ' + str(len(SeleniumBrowser.OFFERS_URLS))+' offer urls in total'}
        elif foundOffersListOnThePage(SeleniumBrowser):
            importlib.reload(settings) # necessary for reloading lists and other complex data types
            time.sleep(random.uniform(settings.WAIT_URLS_THEPROTOCOL[0], settings.WAIT_URLS_THEPROTOCOL[1])) # humanize request frequency
            if scrapOffersUrlsFromSinglePage(SeleniumBrowser)['success'] == True:
                SeleniumBrowser.currentlyScrapedPageIndex += 1
                return {'success':True, 'functionDone':False, 'message': 'page ' + str(SeleniumBrowser.currentlyScrapedPageIndex -1) + ' urls fetched'} # -1 because starting from 1 and incremented just above
    except Exception as exception:
        return {'success':False, 'functionDone':False, 'message':str(exception)}
        

########################################################################### Analyse offer functions ###########################################################################

def offerNotFound(SeleniumBrowser):
    try:
    # NEW HTML ELEMENTS (04.2025)
    # better look for offer list as it always appears when offer not found/achieved (since 04.2025)
    # DRIVER.find_element("xpath", '//*[@data-test="text-offerNotFound"]') 
    # DRIVER.find_element("xpath", '//*[@data-test="text-offerArchived"]') # new element, but logic changed to searching offer list
        if foundOffersListOnThePage(SeleniumBrowser):
            return True
    except:
        return False

def getOfferDetails(SeleniumBrowser):
    #JOB TITLE
    try:
        jobTitle = SeleniumBrowser.DRIVER.find_element(By.XPATH, '//*[@data-test="text-offerTitle"]') # this element should always exist
        jobTitle = jobTitle.text
    except:
        jobTitle = None
    
    #SALARY
    try:
        salaryContainer = SeleniumBrowser.DRIVER.find_element(By.XPATH, '//*[@data-test="section-contract"]') # this element should always exist
        salaryAndContract = salaryContainer.text
        # print(salaryAndContract)
        # print(salaryAndContract  + '\n')
    except:
        salaryAndContract = None
    
    salaryMinAndMax = [None, None] # Nones as these are INTs in DB
    if salaryAndContract != None:
        try: #to recalculate salary to [PLN/month net] #PLN=only unit on protocol?
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
                    salaryMinAndMax = [(float(elmnt) * settings.GROSS_TO_NET_MULTIPLIER) for elmnt in salaryMinAndMax]
                    # print(salaryMinAndMax)
                if re.findall("godz", lines[1]) or re.findall("hr.", lines[1]): # hr -> month
                    salaryMinAndMax = [(float(elmnt) * hoursPerMonthInFullTimeJob) for elmnt in salaryMinAndMax] #possible input float/str

                if salaryMinAndMax[1] == None: # some offers provide just 1 extremum
                    salaryMinAndMax[1] = salaryMinAndMax[0]
                salaryMinAndMax = [int(elmnt) for elmnt in salaryMinAndMax] # to ints
        except:
            pass    # salaryMinAndMax = [None, None]

    # EMPLOYER
    try:
        employerElement = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="anchor-company-link"]') # this element should always exist
        employer = employerElement.text # + ' ' + employerElement.get_property("href")
        employer = re.sub('company: |firma: ', '', employer, flags=re.IGNORECASE).strip()

    except:
        employer= None
    # print(employer  + '\n')
    
    # WORKFROM, EXP, VALIDTO, LOCATION - "PARAMETERS"
    workModes, positionLevels, location = None, None, None
    try:
        parametersContainer = SeleniumBrowser.DRIVER.find_element(By.CLASS_NAME, "c21kfgf")
        parameters = parametersContainer.find_elements(By.CLASS_NAME, "s1bu9jax")
        for param in parameters:
            paramType = param.get_attribute("data-test") #element description
            match paramType:
                case "section-workModes":
                    workModes = param.text
                case "section-positionLevels":
                    positionLevels = param.text
                # case "section-offerValidTo":
                #     offerValidTo = param.text
                case "section-workplace":
                    location = param.text
                    try: #to find and click 'more locations' button then fetch what's inside
                        moreLocations = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="button-locationPicker"]')
                        moreLocations.click()
                        locations = moreLocations.find_element("xpath", '//*[@data-test="modal-locations"]')
                        location = locations.text
                    except:
                        pass #leave location as it was
        # print(workModes + '\n\n' + positionLevels + '\n\n' + '\n\n' +  location + '\n')
    except:
        pass # leave Nones
    
    # IF STILL NOT FOUND, TRY SEARCHING NEW HTML ELEMENTS (04.2025)
    if location == None: # checking location, as it's the toughest one to gather
        parametersContainer = SeleniumBrowser.DRIVER.find_element(By.CLASS_NAME, "m1vgkec8")
        parameters = parametersContainer.find_elements(By.CLASS_NAME, "b12rofz")
        # print(parameters)
        for param in parameters:
            paramType = param.text #element description
            match paramType:
                case thisCase if any(keyword in thisCase.lower() for keyword in ("mode", "tryb")):
                    lines = param.text.splitlines()
                    workModes = "".join(lines[1:])  # Join all lines except the first one (param description)
                case thisCase if any(keyword in thisCase.lower() for keyword in ("level", "poziom")):
                    lines = param.text.splitlines()
                    positionLevels = "".join(lines[1:])
                case _: # IF IT'S NOT MODE OR LEVEL, IT MUST BE LOCATION DIV
                    location = param.text # fine for a single location
                    # remove description keyword
                    location = re.sub('location:|lokalizacja:', '', location, flags=re.IGNORECASE).strip()
                    # TRY CLICKING 'MORE' BUTTON
                    try: #to find and click 'more locations' button then fetch what's inside
                        moreLocations = param.find_element("xpath", '//button[@class="m8ercsp"]')
                        moreLocations.click()
                        locations = moreLocations.find_element("xpath", '//*[@class="mtlwq3f"]')
                        location = locations.text # overwrites a single one
                        location = re.sub('view on map', '', location, flags=re.IGNORECASE).strip()
                    except:
                        pass # leave location as it was


    #TECHSTACK
    techstackExpected, techstackOptional = None, None
    try:
        descriptionsContainer = SeleniumBrowser.DRIVER.find_element(By.CSS_SELECTOR, '#TECHNOLOGY_AND_POSITION')
        techstack = descriptionsContainer.find_elements(By.CLASS_NAME, "c1fj2x2p")
        for group in techstack:
            if re.search('expected|wymagane', group.text.lower()):
                lines = group.text.splitlines()
                techstackExpected = "\n".join(lines[1:]) # join lines except first one
            if re.search('optional|mile widziane', group.text.lower()):
                lines = group.text.splitlines()
                techstackOptional = "\n".join(lines[1:])
        # print(str(techstackExpected) + '\n\n' + str(techstackOptional) + '\n')
    except:
        pass # leave Nones
    # IF STILL NOT FOUND, TRY SEARCHING NEW HTML ELEMENTS (04.2025)
    if techstackExpected == None:
        try:
            technologiesContainer = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="section-technologies"]')
            techstack = technologiesContainer.find_elements("xpath", './div') # divs 1 level down
            for group in techstack:
                if re.search('expected|wymagane', group.text.lower()):
                    lines = group.text.splitlines()
                    techstackExpected = "\n".join(lines[1:]) # join lines except first one
                if re.search('optional|mile widziane', group.text.lower()):
                    lines = group.text.splitlines()
                    techstackOptional = "\n".join(lines[1:])
            # print(str(techstackExpected) + '\n\n' + str(techstackOptional) + '\n')
        except:
            pass # leave Nones


    #RESPONSIBILITIES
    try:
        try:
            responsibilities = descriptionsContainer.find_element("xpath", '//*[@data-test="section-responsibilities"]/ul').text #/only ul elements
        except:
            responsibilities = descriptionsContainer.find_element("xpath", '//*[@data-test="section-responsibilities"]').text #/if it's a single entry
    except:
        responsibilities= None
        # print('RESPONSIBILITIES:\n' + str(responsibilities) + '\n' + driver.current_url)
    # IF STILL NOT FOUND, TRY SEARCHING NEW HTML ELEMENTS (04.2025)
    if responsibilities == None:
        try:
            responsibilities = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="section-responsibilities"]').text
            # responsibilities = "\n".join(responsibilities.split('\n')[1:]) # remove 1st line
        except:
            responsibilities= None
            # print('RESPONSIBILITIES:\n' + str(responsibilities))

    #REQUIREMENTS
    try:
        try:
            requirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements"]/ul').text
        except:
            requirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements"]').text #/if it's a single entry
    except:
        requirements= None
        # print('REQUIREMENTS:\n' + str(requirements) + '\n' + driver.current_url)
    # IF STILL NOT FOUND, TRY SEARCHING NEW HTML ELEMENTS (04.2025)
    if requirements == None:
        try:
            requirements = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="section-requirements-expected"]').text
            # requirements = "\n".join(requirements.split('\n')[1:]) # remove 1st line
        except:
            requirements= None
            # print('REQUIREMENTS:\n' + str(requirements))


    #OPTIONAL REQUIREMENTS
    try:
        optionalRequirementsContainer = descriptionsContainer.find_elements("xpath", '//*[@data-test="section-requirements-optional"]/li')
        if len(optionalRequirementsContainer) > 0:
            optionalRequirements = ''
            for optionalRequirement in optionalRequirementsContainer:
                optionalRequirements += optionalRequirement.text + '\n'
        elif len(optionalRequirementsContainer) == 0:
            try:
                optionalRequirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements-optional"]').text
            except:
                optionalRequirements= None
                # print('OPTIONAL:\n' + str(optionalRequirements) + '\n' + driver.current_url)        
    except:
        optionalRequirements= None
    # IF STILL NOT FOUND, TRY SEARCHING NEW HTML ELEMENTS (04.2025)
    if optionalRequirements == None:
        try:
            optionalRequirements = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="section-requirements-optional"]').text
        except:
            optionalRequirements = None
    # print('OPTIONAL:\n' + str(optionalRequirements) + '\n' + driver.current_url)

    datetimeNow = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # FULL DESCRIPTION
    fullDescription = None
    try:
        fullDescription = SeleniumBrowser.DRIVER.find_element(By.CSS_SELECTOR, '#TECHNOLOGY_AND_POSITION').text
    except:
        fullDescription = None
    # IF STILL NOT FOUND, TRY SEARCHING NEW HTML ELEMENTS (04.2025)
    if fullDescription == None:   
        try:
            fullDescription = SeleniumBrowser.DRIVER.find_element(By.CSS_SELECTOR, '#REQUIREMENTS').text
        except:
            fullDescription = None    

    return {'datetimeLast':datetimeNow, 'datetimeFirst':datetimeNow, 'url':SeleniumBrowser.DRIVER.current_url, 'title':jobTitle, 'salaryAndContract':salaryAndContract, 'salaryMin':salaryMinAndMax[0], 'salaryMax':salaryMinAndMax[1], 'employer':employer, 'workModes':workModes, 'positionLevels':positionLevels, 'location':location, 'techstackExpected':techstackExpected, 'techstackOptional':techstackOptional, 'responsibilities':responsibilities, 'requirements':requirements, 'optionalRequirements':optionalRequirements, 'fullDescription':fullDescription}


########################################################################### Scraping to Database ###########################################################################

def scrapToDatabase(SeleniumBrowser):
    try:
        # FINISH CONDITIONS
        if len(SeleniumBrowser.OFFERS_URLS) == 0:
            return {'success':True, 'functionDone':True, 'message':'no offers to analyse', 'killProcess': True}
        elif int(SeleniumBrowser.currentlyScrapedOfferIndex +1) > int(len(SeleniumBrowser.OFFERS_URLS)):
            print(str(SeleniumBrowser.databaseInserts) + ' inserts | ' + str(SeleniumBrowser.databaseUpdates) + ' updates')
            return {'success':True, 'functionDone':True, 'message': 'scraping done. ' + str(SeleniumBrowser.databaseInserts) + ' inserts | ' + str(SeleniumBrowser.databaseUpdates) + ' updates', 'killProcess': True}
        # IF NOT FINISHED
        else:
            SeleniumBrowser.DRIVER.get(SeleniumBrowser.OFFERS_URLS[SeleniumBrowser.currentlyScrapedOfferIndex]['url'])
            # 'offer not found' div not found - it's offer / botcheck / invalid url by some chance
            if not offerNotFound(SeleniumBrowser):
                # LOOK FOR COMMON KEYS AS getOfferDetails() can return more keys than custom shortened DB has columns
                offerDetailsDict = getOfferDetails(SeleniumBrowser)
                # a dictionary containing only the keys appearing in both dictionaries
                commonKeysDict = {key: offerDetailsDict[key] for key in [item["dbColumnName"] for item in settings.DATABASE_COLUMNS] if key in offerDetailsDict}
                
                # AMOUNT OF NONES CHECK (if too many fields not scraped - bot check, site update, etc)
                alwaysNotNonesAmount = sum(1 for key in commonKeysDict.keys() if key in settings.doNotCountTheseColumnsOnNonesCheck)
                nonesCount = sum(1 for value in commonKeysDict.values() if value is None)
                if nonesCount >= int(len(commonKeysDict)-alwaysNotNonesAmount):
                    # PAUSE on too many nones (allColumns - alwaysNotNonesAmount) at the moment
                    print('PAUSING ' + str(SeleniumBrowser.BASE_URL))
                    return {'success':False, 'functionDone':False, 'message': 'too many fields unrecognized on scraping attempt. See if bot check triggered. If not, the site probably has been updated. Press START if no issues spotted.', 'pauseProcess':True}

                if Database.recordFound(SeleniumBrowser.DRIVER.current_url):
                    Database.updateDatetimeLast(SeleniumBrowser.DRIVER.current_url)
                    SeleniumBrowser.databaseUpdates += 1
                else:
                    Database.insertRecord(commonKeysDict) # insert into database
                    SeleniumBrowser.databaseInserts += 1
                SeleniumBrowser.currentlyScrapedOfferIndex += 1 # increment if successfully analysed

                importlib.reload(settings) # necessary for reloading lists and other complex data types

                time.sleep(random.uniform(settings.WAIT_OFFER_PARAMS_THEPROTOCOL[0], settings.WAIT_OFFER_PARAMS_THEPROTOCOL[1])) # move to settings
                return {'success':True, 'functionDone':False, 'message': str(SeleniumBrowser.currentlyScrapedOfferIndex) + '/' + str(len(SeleniumBrowser.OFFERS_URLS)) + ' offers scraped'}
            elif offerNotFound(SeleniumBrowser):
                # print('OFFER NOT FOUND: ' +  SeleniumBrowser.DRIVER.current_url)
                SeleniumBrowser.currentlyScrapedOfferIndex += 1 # increment even if offer not found not to get stuck
                time.sleep(random.uniform(settings.WAIT_OFFER_PARAMS_THEPROTOCOL[0], settings.WAIT_OFFER_PARAMS_THEPROTOCOL[1])) # move to settings
                return {'success':False, 'functionDone':False, 'message': 'OFFER NOT FOUND: ' +  SeleniumBrowser.DRIVER.current_url}
    except Exception as exception:
        return {'success':False, 'functionDone':False, 'message':str(exception)}