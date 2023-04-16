#
#input('Name')
#input('Password')

# Run docker container docker run -d -p o:4444 --shm-size=2g selenium/standalone-chrome
# docker-compose run https://github.com/SeleniumHQ/docker-selenium/blob/trunk/docker-compose-v3-video.yml
from imp import load_module
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.service import Service
import time
from time import sleep

print("Test Execution Started")


options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Remote(

command_executor='http://selenium:4444/wd/hub',
options=options
)
#maximize the window size
driver.maximize_window()
time.sleep(1)
#navigate to browserstack.com
### Input url
driver.get("https://www.tinkoff.ru/solutioncup/sre/")
time.sleep(1)
driver.find_element(By.LINK_TEXT,"SRE").click()
time.sleep(1)
driver.find_element(By.LINK_TEXT,"backend").click()

# driver.get("https://www.tinkoff.ru/solutioncup/sre/")
#close the browser
driver.close()
driver.quit()
print("Test Execution Successfully Completed!")