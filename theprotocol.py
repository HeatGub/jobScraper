from selenium.webdriver.common.by import By
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
import time, json, random, re, datetime
from databaseFunctions import Database
from settings import GROSS_TO_NET_MULTIPLIER, DATABASE_COLUMNS

########################################################################### Scrap offer URLs from all the pages ###########################################################################

def foundOffersListOnThePage(SeleniumBrowser):
    try:
        SeleniumBrowser.DRIVER.find_element("xpath", '//*[@id="main-offers-listing"]/div[1]/div')
        return True #if offer specific div found
    except:
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
            time.sleep(random.uniform(0.5, 1)) #humanize
            if scrapOffersUrlsFromSinglePage(SeleniumBrowser)['success'] == True:
                SeleniumBrowser.currentlyScrapedPageIndex += 1
                return {'success':True, 'functionDone':False, 'message': 'page ' + str(SeleniumBrowser.currentlyScrapedPageIndex -1) + ' urls fetched'} # -1 because starting from 1 and incremented just above
    except Exception as exception:
        return {'success':False, 'functionDone':False, 'message':str(exception)}
        

########################################################################### Analyse offer functions ###########################################################################

def offerNotFound(SeleniumBrowser):
    try:
        SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="text-offerNotFound"]')
        return True
    except:
        return False

def getOfferDetails(SeleniumBrowser):
    #JOB TITLE
    try:
        jobTitle = SeleniumBrowser.DRIVER.find_element(By.XPATH, '//*[@data-test="text-offerTitle"]') # this element should always exist
        jobTitle = jobTitle.text
    except:
        jobTitle= ''
    
    #SALARY
    try:
        salaryContainer = SeleniumBrowser.DRIVER.find_element(By.XPATH, '//*[@data-test="section-contract"]') # this element should always exist
        salaryAndContract = salaryContainer.text
        # print(salaryAndContract  + '\n')
    except:
        salaryAndContract= ''
    
    salaryMinAndMax = [None, None] # Nones as these are INTs in DB
    if salaryAndContract != '':
        try: #to recalculate salary to [PLN/month net] #PLN=only unit on protocol?
            GROSS_TO_NET_MULTIPLIER = 0.7
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
                    salaryMinAndMax = [(float(elmnt) * GROSS_TO_NET_MULTIPLIER) for elmnt in salaryMinAndMax]
                    # print(salaryMinAndMax)
                if re.findall("godz", lines[1]) or re.findall("hr.", lines[1]): # hr -> month
                    salaryMinAndMax = [(float(elmnt) * hoursPerMonthInFullTimeJob) for elmnt in salaryMinAndMax] #possible input float/str

                salaryMinAndMax = [int(elmnt) for elmnt in salaryMinAndMax] # to ints
        except:
            pass    # salaryMinAndMax = [None, None]

    # EMPLOYER
    try:
        employerElement = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="anchor-company-link"]') # this element should always exist
        employer = employerElement.text + ' ' + employerElement.get_property("href")
    except:
        employer= ''
    # print(employer  + '\n')
    
    #WORKFROM, EXP, VALIDTO, LOCATION - "PARAMETERS"
    workModes, positionLevels, offerValidTo, location = '', '', '', ''
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
                case "section-offerValidTo":
                    offerValidTo = param.text
                case "section-workplace":
                    location = param.text
                    try: #to find and click 'more locations' button then fetch what's inside
                        moreLocations = SeleniumBrowser.DRIVER.find_element("xpath", '//*[@data-test="button-locationPicker"]')
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
        descriptionsContainer = SeleniumBrowser.DRIVER.find_element(By.CSS_SELECTOR, '#TECHNOLOGY_AND_POSITION')
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

    # FULL DESCRIPTION
    fullDescription = ''
    try:
        fullDescription = SeleniumBrowser.DRIVER.find_element(By.CSS_SELECTOR, '#TECHNOLOGY_AND_POSITION').text
    except:
        pass # fullDescription = ''

    return {'datetimeLast':datetimeNow, 'datetimeFirst':datetimeNow, 'url':SeleniumBrowser.DRIVER.current_url, 'title':jobTitle, 'salaryAndContract':salaryAndContract, 'salaryMin':salaryMinAndMax[0], 'salaryMax':salaryMinAndMax[1], 'employer':employer, 'workModes':workModes, 'positionLevels':positionLevels, 'location':location, 'techstackExpected':techstackExpected, 'techstackOptional':techstackOptional, 'responsibilities':responsibilities, 'requirements':requirements, 'optionalRequirements':optionalRequirements, 'fullDescription':fullDescription}

########################################################################### Scraping to Database ###########################################################################

def scrapToDatabase(SeleniumBrowser):
    try:
        # FINISH CONDITIONS
        if len(SeleniumBrowser.OFFERS_URLS) == 0:
            return {'success':True, 'functionDone':True, 'message':'no offers to analyse'}
        elif int(SeleniumBrowser.currentlyScrapedOfferIndex +1) > int(len(SeleniumBrowser.OFFERS_URLS)):
                print(str(SeleniumBrowser.databaseInserts) + ' inserts | ' + str(SeleniumBrowser.databaseUpdates) + ' updates')
                return {'success':True, 'functionDone':True, 'message': 'SCRAPING DONE. ' + str(SeleniumBrowser.databaseInserts) + ' inserts | ' + str(SeleniumBrowser.databaseUpdates) + ' updates'}
        # IF NOT FINISHED
        else:
            SeleniumBrowser.DRIVER.get(SeleniumBrowser.OFFERS_URLS[SeleniumBrowser.currentlyScrapedOfferIndex]['url'])
            if not offerNotFound(SeleniumBrowser):
                # LOOK FOR COMMON KEYS AS getOfferDetails() can return more keys than custom shortened DB has columns
                offerDetailsDict = getOfferDetails(SeleniumBrowser)
                # a dictionary containing only the keys appearing in both dictionaries
                commonKeysDict = {key: offerDetailsDict[key] for key in DATABASE_COLUMNS if key in offerDetailsDict}

                # # before = time.time()
                if Database.recordFound(SeleniumBrowser.DRIVER.current_url):
                    Database.updateDatetimeLast(SeleniumBrowser.DRIVER.current_url)
                    SeleniumBrowser.databaseUpdates += 1
                else:
                    Database.insertRecord(commonKeysDict) # insert into database
                    SeleniumBrowser.databaseInserts += 1
                SeleniumBrowser.currentlyScrapedOfferIndex += 1 # increment if successfully analysed
                return {'success':True, 'functionDone':False, 'message': str(SeleniumBrowser.currentlyScrapedOfferIndex) + '/' + str(len(SeleniumBrowser.OFFERS_URLS)) + ' offers analysed'}
            elif offerNotFound(SeleniumBrowser):
                # print('OFFER NOT FOUND: ' +  SeleniumBrowser.DRIVER.current_url)
                SeleniumBrowser.currentlyScrapedOfferIndex += 1 # increment even if offer not found not to get stuck
                return {'success':False, 'functionDone':False, 'message': 'OFFER NOT FOUND: ' +  SeleniumBrowser.DRIVER.current_url}
    except Exception as exception:
        return {'success':False, 'functionDone':False, 'message':str(exception)}