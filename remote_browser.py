from selenium import webdriver
import os
import time
import json


curdir = os.path.dirname(os.path.realpath(__file__))
chromedirverfile = "chromedriver.exe"

savefile = "selenium.json"

browser = None

sid = {}

sid["url"]=""
sid["sessionid"] = ""

print("Starting a Selenium based browser instance")

try:
    browser = webdriver.Chrome(executable_path=os.path.join(curdir,chromedirverfile))
    print("Waiting for the browser to load..")
    time.sleep(5)

    browser.get("https://web.telegram.org")

    sid["url"] = str(browser.command_executor._url)
    sid["sessionid"] = str(browser.session_id)

    with open(os.path.join(curdir,savefile),'w') as sf:
        json.dump(sid,sf, indent=2)


    print("Keep this terminal running as long as the browser is required.")

    print("Press any key to exit and close the browser")

    input("")

except Exception as e:
    print("Error starting selenium Browser. \nError Description :\n"+e)
