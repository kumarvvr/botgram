# Sri Rama Jaya Rama Jaya Jaya Rama

#####################################################################

# Program to do marketing of content over telegram channels.
# Programmed by Ananth for Arnie from Upwork
# Hi Arnie !

#####################################################################
import sys
import os
import json
import time
import datetime
import db

from selenium import webdriver
from utilities import PrintExceptionError
from telegramWM.telegrampage import TelegramPage as tp
from colorama import init as cinit
from colorama import Fore, Back, Style
from testuserdata import userlist
from dateutil import parser

cinit()

# region DISK FILES : CONFIG, sid, message

curdir = os.path.dirname(os.path.realpath(__file__))
#chromedirverfile = "chromedriver.exe"
sessionfile = "selenium.json"
configfile = "config.json"
messagefile = "marketingmessage.json"
sid = None

with open(os.path.join(curdir,configfile),'r')as cf:
    CONFIG = json.load(cf)

with open(os.path.join(curdir,sessionfile),'r') as sf:
    sid = json.load(sf)

with open(os.path.join(curdir,messagefile),'r') as mf:
    message = json.load(mf)

message = message["message"]

print("PM Message is "+ str(message))

# endregion

# region CONFIGURATION VARIABLES

sleeptime = CONFIG["SLEEP_TIME"]
selserver_url = sid["url"]
selsession_id = sid["sessionid"]

channellist = CONFIG["CHANNEL_SCAN_LIST"]
channellistscancount = CONFIG["CHANNEL_LIST_SCAN_REPEAT"]
channellistscangap = CONFIG["CHANNEL_LIST_SCAN_TIME_GAP"]
channeluserlimit = CONFIG["CHANNEL_USER_LIMIT"]
pmtimelimit = CONFIG["PM_MESSAGE_TIMEGAP"]

# endregion



browser = None


def GatherUsersFromChannelListIntoDB(page):
    global sleeptime, channellist, channeluserlimit, channellistscancount

    channelnames = []
    for cl in channellist:
        channelnames.append(cl["CHANNELNAME"])

    for i in range(channellistscancount):
        print("Channel scan : "+str(i+1))
        userlist = {}
        for cname in channelnames:
            print("Gathering users from : "+cname)
            cusers = page.GetChannelUsers(channel_name=cname, usercountlimit=channeluserlimit)
            time.sleep(sleeptime)
            userlist = {**userlist, **cusers}

        print("Pushing users into database.")

        for key, value in userlist.items():
            db.InsertOrUpdateUser(key, value)

        dbusers = db.GetAllUsers()
        print("Current User count in database : " + str(len(dbusers)))

def InitiateUserGatheringProcess(page):
    global sleeptime, channellistscancount, channellistscangap

    time.sleep(sleeptime)

    page.CloseAllModalDialogs()

    for i in range(channellistscancount):
        try:
            GatherUsersFromChannelListIntoDB(page)
        except Exception as e:
            print("GLOBAL Error : "+str(e))
            input("Press any key to continue gathering users...")
            continue

        print("Next cycle starts in : " + str(channellistscangap) + " seconds")
        time.sleep(channellistscangap)

def SendMessageToUsersInDatabase(page:tp, timelimitseconds = 3600, forcemessages=False, demomode=True):

    global message

    # Close all modal dialogs in the page.
    page.CloseAllModalDialogs()

    # Goto the home page.
    page.GotoHomeChannel()

    # Get users in database as a tuple.
    users = db.GetAllUsers()
    res = []
    for usertuple in users:

        user = db.GetUser(usertuple[0])
        try:
            if(user[2] != ""):
                lastmessagetime = parser.parse(user[2])
                seconds_from_lastmessage = (datetime.datetime.now() - lastmessagetime).total_seconds()
            else:
                # Manually tweak time to force sending user the message
                # This only happens if the user does not have a last
                # message time in the database.
                seconds_from_lastmessage = 3601

            if forcemessages:
                seconds_from_lastmessage = 3601

            if seconds_from_lastmessage > timelimitseconds:
                res = page.SendUserPM(user[0],message, demomode)
                db.InsertOrUpdateUser(res[0], user[1], res[1])
            else:
                print("User : "+user[0]+" skipped due to time limit")
        except Exception as e:
            # This is for some bots being included in user list.
            print("No PM facility available for : "+ user[0])

def PrintCLIHelp():
    print("Available options")
    print("---------------------------------------------------------------")
    print("--sendmessage")
    print(" Example 1 : python botgram.py --sendmessage --real")
    print(" Action : Sends messages to all users, observing time limit")

    print(" Example 2 : python botgram.py --sendmessage --demo")
    print(" Action : Simulated Sending messages to all users, without observing time limit")
    print("---------------------------------------------------------------")

    print("---------------------------------------------------------------")
    print("--sendmessage")
    print(" Example 1 : python botgram.py --sendmessage --real --force")
    print(" Action : Sends messages to all users, observing time limit")

    print(" Example 2 : python botgram.py --sendmessage --demo --force")
    print(" Action : Simulated Sending messages to all users, without observing time limit")
    print("---------------------------------------------------------------")

    print("---------------------------------------------------------------")
    print("--gatherusers")
    print(" Example 1 : python botgram.py --gatherusers")
    print(" Action : Gathers users from all communities listed in ")
    print(" Config.json and saves user details into the database ")
    print("---------------------------------------------------------------")

def main():
    global browser, pmtimelimit

    arguments = sys.argv
    arglength = len(arguments)
    if arglength == 2 and arguments[1] == "--help" or arguments[1] == '-h':
        PrintCLIHelp()
        quit()

    if arglength > 1:
        try:
            print("Connecting to remote Telegram Window")
            browser = webdriver.Remote(command_executor=selserver_url, desired_capabilities={})
            browser.session_id = selsession_id
            print("Successfully connected to remote window..")

        except Exception as e:
            PrintExceptionError("Error starting Remote Controlled Browser", e)
            quit()

        page = tp(browser)
        input("Log into Telegram in the remote browser and then press ENTER")

        if arguments[1] == "--gatherusers" or arguments[1] == "-g":
            GatherUsersFromChannelListIntoDB(page)

        elif arguments[1] == "--sendmessages" or arguments[1] == '-s':
            if arglength == 4:
                if arguments[2] == "--real" and arguments[3] == '--force':
                    SendMessageToUsersInDatabase(page,timelimitseconds=pmtimelimit,forcemessages=True, demomode=False)
                elif arguments[2] == "--demo" and arguments[3] == '--force':
                    SendMessageToUsersInDatabase(page,timelimitseconds=pmtimelimit, forcemessages=True, demomode=True)
            elif arglength == 3:
                if arguments[2] == "--real":
                    SendMessageToUsersInDatabase(page,timelimitseconds=pmtimelimit,forcemessages=False, demomode=False)
                elif arguments[2] == "--demo":
                    SendMessageToUsersInDatabase(page,timelimitseconds=pmtimelimit, forcemessages=False, demomode=True)
            else:
                print("Error Incorrect no. of arguments for --sendmessages")
                PrintCLIHelp()
                quit()
        else:
            print("Error processing command")
            PrintCLIHelp()

    else:
        PrintCLIHelp()
        quit()

    input("Process completed.. Press any key to continue....")


if __name__ == '__main__':
    print("Connecting to remote Telegram Window")
    browser = webdriver.Remote(command_executor=selserver_url, desired_capabilities={})
    browser.session_id = selsession_id
    print("Successfully connected to remote window..")
    page = tp(browser)
    SendMessageToUsersInDatabase(page, timelimitseconds=100, forcemessages=True, demomode=True)
    #main()