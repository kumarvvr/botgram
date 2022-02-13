import sqlite3
import os
import datetime

from sqlite3 import IntegrityError

curdir = os.path.dirname(os.path.realpath(__file__))

dbfile = "botgram.db"

dbfilepath = os.path.join(curdir,dbfile)

dbconn = sqlite3.connect(dbfilepath)

dbconn.execute("CREATE TABLE IF NOT EXISTS users (userid text PRIMARY KEY , username text, lastmessage text)")

dbconn.commit()


def GetAllUsers():
    global dbconn
    rows = None
    with dbconn:
        cur = dbconn.cursor()
        cur.execute("select userid,username,lastmessage from users")
        rows = cur.fetchall()
        return rows

def GetUserCount():
    global dbconn
    with dbconn:
        cur = dbconn.cursor()
        cur.execute("select count(*) from users")
        data = cur.fetchone()
        return str(data[0])

def GetUser(userid):
    res = None
    with dbconn:
        cur = dbconn.cursor()
        cur.execute("select userid,username,lastmessage from users where userid=?",(userid,))
        res = cur.fetchone()
        return res

def IsUserInDatabase(uid):
    global dbconn

    with dbconn:
        cur:sqlite3.Cursor = None
        cur = dbconn.cursor()
        cur.execute("select * from users where userid=?",(uid,))
        data = cur.fetchone()
        if data is None:
            return False
        else:
            return True

def InsertOrUpdateUser(userid, username, lastmessage=""):

    global dbconn

    print("------------******------------")

    print("UPSERTING user into database. UserID : "+userid + " / Username : "+username)


    try:
        with dbconn:
            cur = dbconn.cursor()
            if (IsUserInDatabase(userid)):
                print("User: "+userid+" already in database, updating user records.")
                if lastmessage is "":
                    cur.execute('update users set username=? where userid=?', (username, userid))
                else:
                    cur.execute('update users set username=?, lastmessage=? where userid=?',(username, lastmessage, userid))
            else:
                print("New User found. Inserting user into user database.")
                cur.execute('insert into users values(?,?,?)',(userid, username,lastmessage))
    except Exception as e:
        print("Error Inserting / Updating user in database User Handle : "+userid)
        print("ERROR DESCRIPTION : "+str(e))
        return False
    print("\n USER COUNT IN DATABASE : "+GetUserCount())
    print("------------******------------")
    return True

def UpdateUserLastMessageSentTime(userid,lastmessagetime):
    global dbconn

    try:
        with dbconn:
            cur = dbconn.cursor()
            if(IsUserInDatabase(userid)):
                if len(lastmessagetime) > 0:
                    cur.execute("update users set lastmessage=? where userid=?",(lastmessagetime,userid))
                    return True
            else:
                return False
    except Exception as e:
        print("Error Updating user in database. User Handle : " + userid)
        print("ERROR DESCRIPTION : " + str(e))
        return False

def DeleteUser(userid):
    global cur
    with dbconn:
        cur = dbconn.cursor()
        cur.execute("delete from users where userid=?", (userid,))


if __name__ == '__main__':
    GetAllUsers()
    print(GetUser('@yahoo22'))
    DeleteUser('@yahoo')