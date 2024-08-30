from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json


service = Service(executable_path="chromedriver.exe")
chrome_options = Options()
chrome_options.add_argument("--disable-search-engine-choice-screen")
# chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) #disable error logging
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://theprotocol.it/filtry/python;t/trainee,assistant,junior;p/zdalna;rw/praca/data-scientist-deep-learning-warszawa,oferta,8e0c0000-a5a4-c69a-3164-08dcbb7766ef?s=-1499548823&searchId=20a1f390-66d0-11ef-8a60-57a9d1202edd")

timer = 5
for sec in range(timer+1):
    print(str(timer - sec) + ' seconds left') #not rly
    time.sleep(1)

cookies = driver.get_cookies() # get cookies

json_object = json.dumps(cookies, indent=4) # Serializing json
with open("cookies.json", "w") as outfile: #overwrites cookies.json
    outfile.write(json_object)