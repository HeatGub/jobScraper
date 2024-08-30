from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(executable_path="chromedriver.exe")
chrome_options = Options()
chrome_options.add_argument("--disable-search-engine-choice-screen")
# chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) #disable error logging
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://theprotocol.it/filtry/python;t/trainee,assistant,junior;p/zdalna;rw/praca/data-scientist-deep-learning-warszawa,oferta,8e0c0000-a5a4-c69a-3164-08dcbb7766ef?s=-1499548823&searchId=20a1f390-66d0-11ef-8a60-57a9d1202edd")

def waitAndClickClass(string, timeout, searchBy):
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CLASS_NAME, string)))
    element.click()

waitAndClickClass("o1kmxetl", 10 ) #chcę dostosować
time.sleep(2)



# data-test="button-cancel"


time.sleep(2)







# elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".content")))

# elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "content")))

# elements = driver.find_elements("content")

# buttons = driver.find_elements(By.TAG_NAME, "button")
# for button in buttons:
#     if button.text == 'Chcę dostosować':
#         print(button.text)
        # button.click() # nie działa


# print(cookies_element)
# cookies_element.click()

time.sleep(1)
driver.quit()
