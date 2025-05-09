from selenium.webdriver.common.by import By
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
import time, random, re, datetime
from modules.Database import Database
import settings
import importlib

def anyOffersOnTheList(SeleniumBrowser):
    try:
        # offersList = DRIVER.find_element(By.ID, 'up-offers-list') # changed back to virtuoso ~15.01.2025 xD
        # offers = offersList.find_elements(By.XPATH, '//li[@data-index]') # changed back to virtuoso ~15.01.2025 xD
        offersList = SeleniumBrowser.DRIVER.find_element(By.XPATH, '//*[@data-test-id="virtuoso-item-list"]') # changed to up-offers-list ~25.12.2024
        offers = offersList.find_elements(By.XPATH, 'div[@data-index]') # virtuoso approach
        # print(len(offers))
        if len(offers) > 0:
            return True
        else:
            return False
    except Exception as exception:
        # print(exception)
        return False

def scrapCurrentlyVisibleOffersUrls(SeleniumBrowser): # just the ones currently rendered in browser
    try:
        offersList = SeleniumBrowser.DRIVER.find_element(By.XPATH, '//*[@data-test-id="virtuoso-item-list"]') # changed to up-offers-list ~25.12.2024
        offers = offersList.find_elements(By.XPATH, 'div[@data-index]') # amount depends on screen height 
        for offer in offers: # ever-loading div among them
            try:
                index = offer.get_attribute('data-index')
                # href = offer.find_element(By.XPATH, ".//div/div/a").get_property("href") # changed ~2025.04.20 
                # href = offer.find_element(By.XPATH, "./div/a").get_property("href") # changed on 30.04.2025
                href = offer.find_element(By.XPATH, ".//div/div/a").get_property("href") # changed back to .//div/div/a again on 30.04.2025

                def foundAmongSavedIndexes():
                    if len(SeleniumBrowser.OFFERS_URLS) == 0:
                        return False # no offers
                    for i in range (len(SeleniumBrowser.OFFERS_URLS[-30:])): # 30 last offers (or less if len < 30)
                        if index == SeleniumBrowser.OFFERS_URLS[-i - 1]['index']: # decrementing from the end
                            return True
                    return False # not found if reached this return
                
                if not foundAmongSavedIndexes():
                    SeleniumBrowser.OFFERS_URLS.append({'index':index, 'url':href})
            
            except:
                pass #if url not found
        # if len(OFFERS_URLS) >=1:
        #     print(int(OFFERS_URLS[-1]['index']) - int(OFFERS_URLS[0]['index']) + 1, len(OFFERS_URLS))
        #     print('first and last OFFERS_URLS: ', OFFERS_URLS[0]['index'], OFFERS_URLS[-1]['index'])
    except Exception as exception:
        # print('scrapCurrentlyVisibleOffersUrls ' + str(exception)) # StaleElementReferenceException
        return# {'success':False, 'functionDone':False, 'message':str(exception)}


def scrapAllOffersUrls(SeleniumBrowser):
    try:
        # print('scrapAllOffersUrls')
        # if not anyOffersOnTheList() and SeleniumBrowser.noNewResultsCounter >= 2:
        #     return {'success':False, 'functionDone':True, 'message': 'no offers found on ' + SeleniumBrowser.BASE_URL, 'killProcess': True} # terminate the process if no offers found

        # SeleniumBrowser.DRIVER.execute_script("window.scrollTo(0, 0);") # scroll to the very top

        importlib.reload(settings) # necessary for reloading lists and other complex data types
        # CHECK IF READY TO TERMINATE
        if SeleniumBrowser.noNewResultsCounter >= settings.NO_NEW_RESULTS_COUNTER_LIMIT_JUSTJOIN: # or int(SeleniumBrowser.lastSeenIndex) >= 10: # END IF NO NEW RESULTS FEW TIMES
            # print('first and last OFFERS_URLS: ', SeleniumBrowser.OFFERS_URLS[0]['index'], SeleniumBrowser.OFFERS_URLS[-1]['index'])
            return {'success':True, 'functionDone':True, 'message': 'URLs scraping done. Scraped ' + str(len(SeleniumBrowser.OFFERS_URLS))+' offer urls in total'}
        
        scrapCurrentlyVisibleOffersUrls(SeleniumBrowser) # updates OFFERS_URLS

        if len(SeleniumBrowser.OFFERS_URLS) == 0: # should have results already from the above function execution
            time.sleep(0.2) # give it some more time to load
            SeleniumBrowser.noNewResultsCounter += 1
            return {'success':True, 'functionDone':False, 'message': 'scraping in progress. ' + str(len(SeleniumBrowser.OFFERS_URLS)) + ' urls fetched'}
        elif len(SeleniumBrowser.OFFERS_URLS) > 0:
            # no new offer index found
            if (SeleniumBrowser.lastSeenIndex == SeleniumBrowser.OFFERS_URLS[-1]['index']):
                SeleniumBrowser.DRIVER.execute_script("window.scrollBy(0, -2*innerHeight);") # for some reason scrolling up helps this fucking site to load the bottom
                importlib.reload(settings) # necessary for reloading lists and other complex data types
                time.sleep(random.uniform(settings.WAIT_URLS_JUSTJOIN[0], settings.WAIT_URLS_JUSTJOIN[1]))
                SeleniumBrowser.DRIVER.execute_script("window.scrollBy(0, 3*innerHeight);") # scroll to the bottom
                SeleniumBrowser.noNewResultsCounter += 1
                # print(OFFERS_URLS[0]['index'], OFFERS_URLS[-1]['index'])
            # if new offer index found reset the counter
            else: 
                SeleniumBrowser.noNewResultsCounter = 0
            # ABOVE IF/ELSE RETURNS THE BELOW
            return {'success':True, 'functionDone':False, 'message': 'scraping in progress. ' + str(len(SeleniumBrowser.OFFERS_URLS)) + ' urls fetched'}
        
    except Exception as exception:
        SeleniumBrowser.noNewResultsCounter += 1
        return {'success':False, 'functionDone':False, 'message':str(exception)}

    finally: # UPDATE LAST INDEX ANYWAY (finally block is always executed)
        if(len(SeleniumBrowser.OFFERS_URLS)) > 0:
            # time.sleep(0.1)
            SeleniumBrowser.lastSeenIndex = SeleniumBrowser.OFFERS_URLS[-1]['index']
            SeleniumBrowser.DRIVER.execute_script("window.scrollBy(0, innerHeight);")  # scroll to the bottom

        # print(len(SeleniumBrowser.OFFERS_URLS), SeleniumBrowser.noNewResultsCounter)

########################################################################### Analyse offer functions ###########################################################################

def offerNotFound(SeleniumBrowser):
    try:  # try finding offer specific div (job description/techstack divs)
        specificDivs = SeleniumBrowser.DRIVER.find_elements(By.CLASS_NAME, 'MuiBox-root.css-16nvqld')
        if (len(specificDivs)) > 0:
            return False
        else:
            return True
    except:
        return True

def getOfferDetails(SeleniumBrowser):
    # BASIC PARAMETERS WHICH SHOULD ALWAYS BE NOT EMPTY ON THE SITE
    try:
        offerContent = SeleniumBrowser.DRIVER.find_element(By.CSS_SELECTOR, '.MuiBox-root.css-tnvghs')
        topContainer = offerContent.find_element(By.CSS_SELECTOR, 'div')
        topDiv = topContainer.find_element(By.XPATH, ".//*[contains(@class, 'css-10x887j')]") # .// = as deep as necessary
    except Exception as exception:
        # print(exception)
        # no point of continuing, but has to return a dictionary of nones
        return {'datetimeLast':None, 'datetimeFirst':None, 'url':None, 'title':None, 'salaryAndContract':None, 'salaryMin':None, 'salaryMax':None, 'employer':None, 'workModes':None, 'positionLevels':None, 'location':None, 'techstackExpected':None, 'techstackOptional':None, 'responsibilities':None, 'requirements':None, 'optionalRequirements':None, 'fullDescription':None}

    try:
        jobTitle = topDiv.find_element(By.CSS_SELECTOR, 'h1').text
    except:
        jobTitle = None
    try:
        employerAndLocationDiv = topDiv.find_element(By.CSS_SELECTOR, '.MuiBox-root.css-yd5zxy')
        # FOR SOME REASON JUST THIS ONE FIELD OCCASIONALLY HAS STALE ELEMENT ERROR, and it's not due to employerAndLocationDiv as its being used successfully in location scraping
        # The StaleElementReferenceException happens because the element is no longer attached to the DOM, which can occur if the page is updated, refreshed, or if JavaScript modifies the page
        employer = employerAndLocationDiv.find_element(By.XPATH, './/h2').text # look for h2 as deep as necessary

        # print('\n' +employer) # name="multilocation_button"
    except:
        employer = None
        # import traceback
        # traceback.print_exc()

    try:
        location = employerAndLocationDiv.find_elements(By.CSS_SELECTOR, '.MuiBox-root.css-mswf74')[1].text # first one is employer
        location = re.sub(r'\+[0-9]+$', '', location) #remove '+x' where x is int
    except:
        location = None
    #try clicking for more locations
    try:
        locationButton = employerAndLocationDiv.find_element("xpath", '//*[@name="multilocation_button"]')
        locationButton.click()
        locationsMenu = offerContent.find_element("xpath", '//ul[@role="menu"]')
        # locationsMenu = locationsMenu.find_elements(By.CSS_SELECTOR, 'li')
        if location == None:
            location = ''
        location += '\n' + locationsMenu.text # TEXT EMPTY WHEN MINIMIZED!
    except Exception as exception:
        pass
    # print(location)

    #SALARY
    try:
        # salaryAndContract = topContainer.find_element(By.CSS_SELECTOR, '.MuiBox-root.css-1km0bek').text # changed ~2025.04.20 due to nested span
        salaryAndContract = topContainer.find_element(By.CSS_SELECTOR, '.MuiBox-root.css-1km0bek').get_attribute("innerText")
        salaryAndContractElement = topContainer.find_element(By.CSS_SELECTOR, '.MuiBox-root.css-1km0bek')
    except:
        salaryAndContract = None

    # print(salaryAndContract)
    salaryMinAndMax = [None, None]
    if salaryAndContract != None:
        try: #to recalculate salary to [PLN/month net]
            hoursPerMonthInFullTimeJob = 168
            # minAndMaxLine = salaryAndContract.splitlines()[0] # There could be multiple salaries depending on contract type though. It will be in salaryAndContract anyway
            # secondLine = salaryAndContract.splitlines()[1] # changed ~2025.04.20
            salaryAndContractSpans = salaryAndContractElement.find_elements(By.CSS_SELECTOR, 'span')
            minAndMaxLine = salaryAndContractSpans[0].get_attribute("innerText")
            contractLine = salaryAndContractSpans[1].get_attribute("innerText") # could look in whole salaryAndContract but it can have multiple contract types
            firstContractParameters = minAndMaxLine + ' ' + contractLine
            splitValues = re.split(r'-', minAndMaxLine) # split on a first dash for min and max

            for i in range(len(splitValues)):
                splitValues[i] = splitValues[i].replace(" ", "") # remove spaces
                splitValues[i] = re.sub(r",\d{1,2}", '', splitValues[i]) # removes , and /d{1 to 2 occurrences}  (needed when salary as 123,45)
                salaryMinAndMax[i] = re.search(r"\d+", splitValues[i]).group() # r = raw, \d+ = at least 1 digit, group() contains results
            # gross -> net
            if re.findall("brutto", firstContractParameters) or re.findall("gross", firstContractParameters):
                salaryMinAndMax = [(float(elmnt) * settings.GROSS_TO_NET_MULTIPLIER) for elmnt in salaryMinAndMax]
            # year -> month
            if re.findall("year", firstContractParameters) or re.findall("rok", firstContractParameters): 
                salaryMinAndMax = [(float(elmnt)/12) for elmnt in salaryMinAndMax] #possible input float/str
            # day -> month
            if re.findall("day", firstContractParameters) or re.findall("dzień", firstContractParameters): 
                salaryMinAndMax = [(float(elmnt) * hoursPerMonthInFullTimeJob/8) for elmnt in salaryMinAndMax] #possible input float/str
            # hr -> month
            if re.findall("hour", firstContractParameters) or re.findall(r"/h", firstContractParameters) or re.findall("godz", contractLine): 
                salaryMinAndMax = [(float(elmnt) * hoursPerMonthInFullTimeJob) for elmnt in salaryMinAndMax] #possible input float/str

            salaryMinAndMax = [int(elmnt) for elmnt in salaryMinAndMax] # to ints
            # cancel conversion if employer can't properly set units
            if salaryMinAndMax[0] < 1000 or salaryMinAndMax[0] > 100000:
                salaryMinAndMax = [None, None]
        except Exception as exception:
            # print(exception)
            pass    # salaryMinAndMax = [None, None]
        
    workModes = None
    positionLevels = None

    try:
        # MuiBox-root css-ktfb40
        fourRectanglesContainer = offerContent.find_elements(By.XPATH, "./div")[1] # only child divs, not grandchild or further - 1 level down
        # print(fourRectanglesContainer.text)
        fourRectangles = fourRectanglesContainer.find_elements(By.XPATH, "./div")

        for i in range(len(fourRectangles)):
            fourRectangles[i] = fourRectangles[i].find_elements(By.XPATH, "./div")[1] # second child div (not grandchild or further)
            fourRectangles[i] = fourRectangles[i].find_elements(By.XPATH, "./div")[1].text
            # print(fourRectangles[i])
        if salaryAndContract == None:
            salaryAndContract = ''
        salaryAndContract += '\n' + fourRectangles[0] + ' | ' + fourRectangles[2]
        positionLevels = fourRectangles[1]
        workModes = fourRectangles[3]
    except Exception as exception:
        # print(exception)
        pass
    # print(salaryAndContract)
    # print(workModes, positionLevels + '\n')

    #TECHSTACK
    techstackExpected, techstackOptional = None, None
    try:
        # techstackDiv = offerContent.find_elements(By.CSS_SELECTOR, '.MuiBox-root.css-qal8sw')[0] # changed 04.2025
        # techstackDiv = techstackDiv.find_element(By.CSS_SELECTOR, 'div')
        techstackDiv = offerContent.find_elements(By.CSS_SELECTOR, '.MuiStack-root.css-6r2fzw')[0]

        technologies = techstackDiv.find_elements(By.XPATH, './/h4') # look for h4 in all children elements
        levels = techstackDiv.find_elements(By.XPATH, './/span') # look for h4 in all children elements
        for i in range(len(technologies)):
            techWithLvl = technologies[i].text + ' - ' + levels[i].text
            # print(techWithLvl)
            if levels[i].text == 'Nice To Have': # or levels[i].text == 'Junior'
                if techstackOptional == None:
                    techstackOptional = ''
                techstackOptional += '\n' + techWithLvl
            else: # -(nice to have)/junior/regular/advanced/master
                if techstackExpected == None:
                    techstackExpected = ''
                techstackExpected += '\n' + techWithLvl
        if techstackOptional != None:
            techstackOptional = re.sub(r"^\n", '', techstackOptional)
        if techstackExpected != None:
            techstackExpected = re.sub(r"^\n", '', techstackExpected)
    except Exception as exception:
        # print(exception)
        pass # leave empty strs
    # print(techstackExpected + '\n\n' + techstackOptional)

    fullDescription = None
    responsibilities, requirements, optionalRequirements = None, None, None

    optionalRequirementsKeywords = ['nice to', 'optional', 'ideal', 'preferr', 'asset', 'appreciat', 'atut', 'dodatk', 'mile widzi']
    requirementsKeywords = ['require', 'expect', 'skill', 'look', 'qualifications', 'must', 'competen', 'wymaga', 'oczek', 'umiejętn', 'aplikuj, jeśli', 'potrzeb', 'szukamy', 'kompeten']
    responsibilitiesKeywords = ['responsib', 'task', 'role', 'project', 'obowiązk', 'zadani', 'projek']
    whatTheyOfferKeywords = ['offer', 'benefit' 'oferuj', 'oferow']

    allKeywordsDict = {'optionalRequirementsKeywords':optionalRequirementsKeywords, 'requirementsKeywords':requirementsKeywords, 'responsibilitiesKeywords':responsibilitiesKeywords}

    try:
        # descriptionDiv = offerContent.find_elements(By.CSS_SELECTOR, '.MuiBox-root.css-qal8sw')[1] # changed 31.03.20205 (not sure when on jj.it)
        # descriptionDiv = descriptionDiv.find_elements(By.XPATH, "./div")[1] # second child div
        # descriptionDiv = offerContent.find_element(By.CSS_SELECTOR, '.MuiBox-root.css-rcazos') # changed 30.04.2025
        descriptionDiv = offerContent.find_element(By.CLASS_NAME, 'MuiBox-root.css-1vqiku9')
        
        # Remove empty lines (including those with spaces)
        fullDescription = re.sub(r'^\s*\n', '', descriptionDiv.text, flags=re.MULTILINE)
        # print(fullDescription)

        def splitTextByKeywords(text, keywords):
            lines = text.split("\n")  # Split text into lines
            keywordIndices = [i for i, line in enumerate(lines) if any(keyword.lower() in line.lower() for keyword in keywords)]
            # If no keywords found, return the original text as one paragraph
            if not keywordIndices:
                return [text]
            
            paragraphs = []
            startIndex = 0
            for keywordIndex in keywordIndices:
                # if startIndex != keywordIndex:
                paragraphs.append("\n".join(lines[startIndex:keywordIndex]).strip())  # Capture paragraph before keyword
                startIndex = keywordIndex  # Update start for next section
            paragraphs.append("\n".join(lines[startIndex:]).strip())  # Capture the last paragraph
            return paragraphs
        
        keywords = optionalRequirementsKeywords + requirementsKeywords + responsibilitiesKeywords + whatTheyOfferKeywords # just concat keywords lists as they will be assigned to a category later
        paragraphs = splitTextByKeywords(fullDescription, keywords)

        for paragraph in paragraphs:
            if not paragraph or re.search(r"^\s*$", paragraph): # \s matches Unicode whitespace characters. This includes [ \t\n\r\f\v] and more
                continue # don't try to analyze an empty sting, go with next loop iteration
            # look for keywords in the 1st line of text
            header = paragraph.splitlines()[0] # first line
            # print('=====================')
            # print(header)
            # print(paragraph)
            for keywordsCategory in allKeywordsDict.keys():
                # print(keywordsCategory)
                for keyword in allKeywordsDict[keywordsCategory]:
                    # if keyword found in header
                    # if re.search(rf'\b{re.escape(keyword)}\b', header, re.IGNORECASE): # \b = boundaries - matches whole words, regardless of punctuation or position in the string # escapes = escape regex reserved symbols
                    if re.search(rf'.*{re.escape(keyword)}.*', header, re.IGNORECASE): # .* = any symbol any number of times
                        # print('found ' + keyword)
                        if keywordsCategory =='optionalRequirementsKeywords': # check this first as it's more specific than requirements and contains similar keywords
                            if optionalRequirements == None:
                                optionalRequirements = ''
                            optionalRequirements += paragraph

                        elif keywordsCategory =='requirementsKeywords':
                            if requirements == None:
                                requirements = ''
                            requirements += paragraph

                        elif keywordsCategory =='responsibilitiesKeywords':
                            if responsibilities == None:
                                responsibilities = ''
                            responsibilities += paragraph

    except Exception as exception:
        # print(exception)
        pass

    # print('\n\n'+ responsibilities +'\n\n'+ requirements +'\n\n'+ optionalRequirements)
    datetimeNow = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return {'datetimeLast':datetimeNow, 'datetimeFirst':datetimeNow, 'url':SeleniumBrowser.DRIVER.current_url, 'title':jobTitle, 'salaryAndContract':salaryAndContract, 'salaryMin':salaryMinAndMax[0], 'salaryMax':salaryMinAndMax[1], 'employer':employer, 'workModes':workModes, 'positionLevels':positionLevels, 'location':location, 'techstackExpected':techstackExpected, 'techstackOptional':techstackOptional, 'responsibilities':responsibilities, 'requirements':requirements, 'optionalRequirements':optionalRequirements, 'fullDescription':fullDescription}

########################################################################### Scraping to Database ###########################################################################

def scrapToDatabase(SeleniumBrowser):
    try:
        # FINISH CONDITIONS
        if len(SeleniumBrowser.OFFERS_URLS) == 0:
            return {'success':True, 'functionDone':True, 'message':"no offers to analyse. justjoin might require active/headless browser window if that's the case (depends on justjoin update)", 'killProcess': True}
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

                time.sleep(random.uniform(settings.WAIT_OFFER_PARAMS_JUSTJOIN[0], settings.WAIT_OFFER_PARAMS_JUSTJOIN[1]))
                return {'success':True, 'functionDone':False, 'message': str(SeleniumBrowser.currentlyScrapedOfferIndex) + '/' + str(len(SeleniumBrowser.OFFERS_URLS)) + ' offers scraped'}
            else: # offer not found
                # print('OFFER NOT FOUND: ' +  SeleniumBrowser.DRIVER.current_url)
                SeleniumBrowser.currentlyScrapedOfferIndex += 1 # increment even if offer not found not to get stuck
                time.sleep(random.uniform(settings.WAIT_OFFER_PARAMS_JUSTJOIN[0], settings.WAIT_OFFER_PARAMS_JUSTJOIN[1]))
                return {'success':False, 'functionDone':False, 'message': 'OFFER NOT FOUND: ' +  SeleniumBrowser.DRIVER.current_url}
    except Exception as exception:
        print(exception)
        return {'success':False, 'functionDone':False, 'message':str(exception)}