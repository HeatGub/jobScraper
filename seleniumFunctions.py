from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
pd.options.mode.copy_on_write = True # recommended - https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html#returning-a-view-versus-a-copy
import time,json, random, re, datetime, sqlite3
from databaseFunctions import database, columnsAll

# # ChromeDriver should match browser version. If outdated download from:
# # https://googlechromelabs.github.io/chrome-for-testing/


OFFERS_URLS = [] #GLOBAL, appended in fetchUrlsFromAllThePages()
# base_url = "https://theprotocol.it/filtry/ai-ml;sp/bialystok;wp/stacjonarna;rw"
base_url = "https://theprotocol.it/filtry/ai-ml;sp/bialystok;wp/"
# currentSession = str(DRIVER.session_id)

def openBrowser():
    try:
        # SELENIUM CHROME DRIVER SETTINGS
        service = Service(executable_path="chromedriver.exe")
        chrome_options = Options()
        chrome_options.add_argument("--disable-search-engine-choice-screen")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) #disable error logging
        # chrome_options.add_experimental_option("detach", True) #to keep browser open after python script execution ended
        global DRIVER
        DRIVER = webdriver.Chrome(service=service, options=chrome_options) #Selenium opens a new browser window whenever it initializes a WebDriver instance
        DRIVER.get("https://google.com")
        return {'success':True, 'responseCode': 200, 'message':'browser opened'}
    except Exception as exception:
        return {'success':False, 'responseCode': 500, 'message':str(exception)}
    
def saveCookiesToJson():
    try:
        cookies = DRIVER.get_cookies() # get cookies
        json_object = json.dumps(cookies, indent=4) # Serializing json
        with open("cookies.json", "w") as outfile: # OVERWRITES cookies.json
            outfile.write(json_object)
        return {'success':True, 'responseCode': 200, 'message':'cookies saved to cookies.json'}
    except Exception as exception:
        return {'success':False, 'responseCode': 500, 'message':str(exception)}

def setCookiesFromJson():
    try:
        DRIVER.get(base_url) #RUN BROWSER
        with open('cookies.json', 'r', newline='') as inputdata:
            cookies = json.load(inputdata)
        for cookie in cookies: #works only after driver.get
            DRIVER.add_cookie(cookie)
        DRIVER.refresh() # to load cookies
        return {'success':True, 'responseCode': 200, 'message':'cookies successfully set'}
    except Exception as exception:
        return {'success':False, 'responseCode': 500, 'message':str(exception)}


# ########################################################################### Fetch the URLs from all the pages ###########################################################################

def fetchUrlsFromAllThePages():
    global OFFERS_URLS
    OFFERS_URLS = [] #reset on retry
    def anyOffersOnTheList():
        try:
            DRIVER.find_element(By.CSS_SELECTOR, '#main-offers-listing > div.hfenof > div.t2re51w > div')
            return False
        except:
            return True
        
    def fetchOffersUrlsFromSinglePage():
        try:
            offersContainer = DRIVER.find_element("xpath", '//*[@id="main-offers-listing"]/div[1]/div')
            offers = offersContainer.find_elements(By.CLASS_NAME, 'a4pzt2q ')
            # offers = offersContainer.find_elements(By.CSS_SELECTOR, '#offer-title') #also works
            # print('\t'+ str(len(offers)) + ' offers:')
            for offer in offers:
                OFFERS_URLS.append(offer.get_property("href"))
        except:
            print ('probably too high request frequency triggered robot check')

    page = 1 #theprotocol enumerates pages starting from 1
    while True: # because not sure how many pages are there
        site = DRIVER.get(base_url + "?pageNumber=" + str(page))
        if not anyOffersOnTheList():
            print('fetched ' + str(len(OFFERS_URLS)) + ' offer urls in total')
            break # break if no results
        else:
            time.sleep(random.uniform(0.5, 1)) #humanize
            fetchOffersUrlsFromSinglePage()
            print('page ' + str(page) + ' urls fetched')
            page += 1
    return str(len(OFFERS_URLS)) + ' urls fetched'


# ########################################################################### Analyse offer functions ###########################################################################


def offerNotFound():
    try:
        DRIVER.find_element("xpath", '//*[@data-test="text-offerNotFound"]')
        return True
    except:
        return False

def getOfferDetails():
    #JOB TITLE
    try:
        jobTitle = DRIVER.find_element(By.XPATH, '//*[@data-test="text-offerTitle"]') # this element should always exist
        jobTitle = jobTitle.text
    except:
        jobTitle = None
    
    #SALARY
    try:
        salaryContainer = DRIVER.find_element(By.XPATH, '//*[@data-test="section-contract"]') # this element should always exist
        salaryAndContract = salaryContainer.text
        # print(salaryAndContract  + '\n')
    except:
        salaryAndContract = None
    
    salaryMinAndMax = [None, None] # set as zeros to have some values for plotting
    if salaryAndContract:
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
        employerElement = DRIVER.find_element("xpath", '//*[@data-test="anchor-company-link"]') # this element should always exist
        employer = employerElement.text + ' ' + employerElement.get_property("href")
    except:
        employer = None
    # print(employer  + '\n')
    
    #WORKFROM, EXP, VALIDTO, LOCATION - "PARAMETERS"
    workModes, positionLevels, offerValidTo, location = '', '', '', ''
    parametersContainer = DRIVER.find_element(By.CLASS_NAME, "c21kfgf")
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
                    moreLocations = DRIVER.find_element("xpath", '//*[@data-test="button-locationPicker"]')
                    moreLocations.click()
                    # time.sleep(0.05) #probably necessary
                    locations = moreLocations.find_element("xpath", '//*[@data-test="modal-locations"]')
                    location = locations.text
                except:
                    pass #leave location as it was
    # print(workModes + '\n\n' + positionLevels + '\n\n' +  offerValidTo + '\n\n' +  location + '\n')

    #TECHSTACK
    descriptionsContainer = DRIVER.find_element(By.CSS_SELECTOR, '#TECHNOLOGY_AND_POSITION')

    techstack = descriptionsContainer.find_elements(By.CLASS_NAME, "c1fj2x2p")
    techstackExpected = None
    techstackOptional = None
    for group in techstack:
        if group.text[0:8] == 'EXPECTED' or group.text[0:8] == 'WYMAGANE': # eng/pl same word length
            techstackExpected = group.text[9:]
        elif group.text[0:8] == 'OPTIONAL':
            techstackOptional = group.text[9:]
        elif group.text[0:13] == 'MILE WIDZIANE': # polish version
            techstackOptional = group.text[14:]
    # print(str(techstackExpected) + '\n\n' + str(techstackOptional) + '\n')

    #RESPONSIBILITIES
    try:
        try:
            responsibilities = descriptionsContainer.find_element("xpath", '//*[@data-test="section-responsibilities"]/ul').text #/only ul elements
        except:
            responsibilities = descriptionsContainer.find_element("xpath", '//*[@data-test="section-responsibilities"]').text #/if it's a single entry
    except:
        responsibilities = None
        # print('RESPONSIBILITIES:\n' + str(responsibilities) + '\n' + driver.current_url)

    #REQUIREMENTS
    try:
        try:
            requirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements"]/ul').text
        except:
            requirements = descriptionsContainer.find_element("xpath", '//*[@data-test="section-requirements"]').text #/if it's a single entry
    except:
        requirements = None
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
                optionalRequirements = None
                # print('OPTIONAL:\n' + str(optionalRequirements) + '\n' + driver.current_url)        
    except:
        optionalRequirements = None
    # print('OPTIONAL:\n' + str(optionalRequirements) + '\n' + driver.current_url)
    datetimeNow = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return [datetimeNow, datetimeNow, DRIVER.current_url, jobTitle, salaryAndContract, salaryMinAndMax[0], salaryMinAndMax[1], employer, workModes, positionLevels, offerValidTo, location, techstackExpected, techstackOptional, responsibilities, requirements, optionalRequirements]

########################################################################### Scrapping to database ###########################################################################

def scrapToDatabase():
    #PRIMITIVE FLOW FOR TESTS
    openBrowser()
    setCookiesFromJson()
    fetchUrlsFromAllThePages()
    
    # timeDeltas = []
    inserts = 0
    updates = 0
    print(database.countAllRecords() + ' records before run')
    for i in range (5):
    # for i in range (len(OFFERS_URLS)):
        DRIVER.get(OFFERS_URLS[i])
        if not offerNotFound():
            resultsList = getOfferDetails()
            outputDictionary = {}
            for column, offerDetail in zip(columnsAll, resultsList):
                outputDictionary[column] = offerDetail #combine 2 lists into 1 dictionary
            # before = time.time()
            if database.recordFound(DRIVER.current_url):
                database.updateDatetimeLast(DRIVER.current_url)
                updates += 1
            else:
                database.insertRecord(outputDictionary) # insert into database
                inserts += 1
            # timeDeltas.append(time.time() - before)
            #ending here and starting in an above for/zip loop it takes ~(1/100)s - good enough
            print (str(i+1) + '/' + str(len(OFFERS_URLS)) + ' done')
        else:
            print('OFFER NOT FOUND: ' +  DRIVER.current_url)
        time.sleep(random.uniform(0.35,0.85)) #Humanize requests frequency
    # print(np.mean(timeDeltas))
    # print(str(inserts) + ' inserts | ' + str(updates) + ' updates')
    return (str(inserts) + ' inserts | ' + str(updates) + ' updates')


# Process queue management
def queueManager(taskQueue, resultQueue):
    while True:
        print('\t\t\t\t\t QUEUE MANAGER LOOP')
        # if len(task_queue.get()) == 0:
        #     print('len 0')
        #     break #break
        task = taskQueue.get()  # Get a task from the queue
        if task == "exit":  # Exit signal
            print("Worker exiting...")
            break
        func, args, kwargs = task  # Unpack the function, args, and kwargs
        result = func(*args, **kwargs)  # Call the function
        # if not resultQueue.empty():
        resultQueue.put(result)  # Send the result back