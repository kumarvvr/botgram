import os
import json
from . import css_selectors
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException
import time
import datetime
import db




selectors = css_selectors.selectors

curdir = os.path.dirname(os.path.realpath(__file__))
telegramconfigfile = "telegram_config.json"

# region Minor Utilities : PrintExceptionError

def PrintExceptionError(message, e):
    print("----------------- EXCEPTION --------------------")
    print(str(message))
    print(str(e))
    print("----------------- EXCEPTION --------------------")

# endregion

# region Configuration : telegramconfig

telegramconfig = None
with open(os.path.join(curdir,telegramconfigfile)) as tcf:
     telegramconfig = json.load(tcf)

# endregion

sleeptime = telegramconfig["SLEEP_TIME"]

class TelegramPage():

    def __init__(self, browser:webdriver):
        global telegramconfig
        self.browser = browser
        self.CONFIG = telegramconfig

    # region Private Methods : __FilterElements__

    def __FilterElements__(self, selector):
        return self.browser.find_elements_by_css_selector(selector)

    # endregion

    def UpdatePageState(self, PAGE_STATE ):
        self.pagestate = PAGE_STATE

    def GetChannelList(self):
        csselem = selectors["channels"]["names"]
        filteredelements = self.__FilterElements__(csselem)
        res = [fe.text for fe in filteredelements]
        return res

    def SelectChannel(self, channel_name):
        csselem = selectors["channels"]["names"]
        filteredelements = self.__FilterElements__(csselem)
        for fe in filteredelements:
            if fe.text == channel_name:
                fe.click()
                return True
        print("Channel : '"+channel_name+"' Not found")
        return False

    def GotoHomeChannel(self):
        self.SelectChannel(self.CONFIG["HOME_CHANNEL_NAME"])

    def GetCurrentChannelName(self):
        pass

    def ClickHeaderButton(self):
        csselem = selectors["headbutton"]
        felements = self.__FilterElements__(csselem)
        felements[0].click()

    def GotoChannelPage(self, channel_name):
        return self.SelectChannel(channel_name)

    def SendUserPM(self, username, send_message, demomode=True):
        url = self.CONFIG["IM_URL"]
        self.browser.get(url.format(userhandle=username))
        time.sleep(sleeptime)
        csselem = selectors["userpage"]["userimbox"]
        felements = self.__FilterElements__(csselem)

        csselem = selectors["userpage"]["usersendbutton"]
        sendbuttonelement = self.__FilterElements__(csselem)



        for message in send_message:
            felements[0].click()
            felements[0].clear()
            felements[0].send_keys(message)
            if not demomode:
                sendbuttonelement.click()

        return [username,str(datetime.datetime.now())]

    def GetChannelUsers(self, channel_name, usercountlimit=-1):

        results = {}

        if(self.GotoChannelPage(channel_name)):
            print("Waiting for the channel page to fully load.")
            time.sleep(sleeptime)
            self.ClickHeaderButton()
            print("Waiting for the members window to open...")
            time.sleep(sleeptime)

            csselem = selectors["channelpage"]["userlinks"]
            userlist = self.__FilterElements__(csselem)

            usernames = [(u.text,"",u) for u in userlist]
            print("Obtaining user handles for each user")

            count = 0
            for i in range(len(usernames)):
                count+=1
                unameselector = selectors["userprofilepage"]["username"]
                username = usernames[i][0]
                ele = usernames[i][2]
                try:
                    ele.click()
                except ElementNotVisibleException as enve:
                    print("Scrolling the page to view user name")
                    ele.location_once_scrolled_into_view
                    ele.click()
                time.sleep(2)
                if(self.CheckErrorModalWindow(True)):
                    print("Closed an error window")
                try:
                    uname = self.__FilterElements__(unameselector)[0].text
                    print(str(i + 1) + ": " + username + " - " + uname)
                    if(uname[0] == "@"):
                        results[uname] = usernames[i][0]

                        # Immediately add user to database.
                        db.InsertOrUpdateUser(uname,username,"")

                except IndexError as ie:
                    print(username+" : has hidden his user handle")

                # Close the Modal window.
                self.CloseUserProfileDialog()
                if usercountlimit != -1 and count > usercountlimit:
                    break

            # Iterate through the list of users and
            try:
                time.sleep(sleeptime)
                #userlist[0].location_once_scrolled_into_view
                self.CloseModalDialog()
            except Exception as e:
                print("Error closing modal dialog after getting channel user list. Message : "+str(e))

        return results

    def CheckErrorModalWindow(self, close=False):
        csselem = selectors["userprofilepage"]["angular_error"]
        felements = self.__FilterElements__(csselem)
        if(len(felements) > 0):
            #Elements are present
            if(close):
                self.CloseAngularErrorWindow()
                time.sleep(sleeptime)
            return True
        return False

    def GotoUserPage(self, userhandles:list):
        for user in userhandles:
            url = telegramconfig["IM_URL"].format(userhandle = user)

            # Go to the user URL

    def WriteMessageInCurrentPage(self, message):
        pass

    def CloseAngularErrorWindow(self):
        try:
            csselem = selectors["userprofilepage"]["angular_error_ok_button"]
            felements = self.__FilterElements__(csselem)
            if len(felements) > 0:
                felements[0].click()
        except Exception as e:
            print("No Angular Error Window found. Message : "+str(e))

    def CloseModalWindow(self):
        try:
            csselem = selectors["modalwindowclosebutton"]
            felements = self.__FilterElements__(csselem)
            felements[0].click()
        except Exception as e:
            print("No Modal Window Element found. Message : "+str(e))

    def CloseModalDialog(self):
        try:
            csselem = selectors["modaldialogclosebutton"]
            felements = self.__FilterElements__(csselem)
            felements[0].click()
        except Exception as e:
            print("No Modal Window Dialog found. Message : "+str(e))

    def CloseUserProfileDialog(self):
        try:
            csselem = selectors["userprofilepage"]["closebutton"]
            felements = self.__FilterElements__(csselem)[0]
            felements.click()
        except Exception as e:
            print("No User Profile Dialog Element found. Message : "+str(e))

    def CloseAllModalDialogs(self):
        # First check for user profile pages
        self.CloseAngularErrorWindow()
        time.sleep(2)

        self.CloseUserProfileDialog()
        time.sleep(2)

        self.CloseModalDialog()
        time.sleep(2)

        self.CloseModalWindow()
        time.sleep(2)

    def __str__(self):
        return "Current Page is : " + str(self.pagestate)

