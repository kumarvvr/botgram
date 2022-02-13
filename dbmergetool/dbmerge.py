import sys
import os
import sqlite3
from pathlib import Path

def MergeDBFiles():
    curdir = Path.cwd()
    targetfile = Path.cwd().joinpath("botgram.db")
    dbfiles = list(curdir.glob('**/*.db'))
    userlist = []

    for dbfile in dbfiles:
        dbconn = sqlite3.connect(str(dbfile.absolute()))
        with dbconn:
            cur = dbconn.cursor()
            cur.execute("SELECT userid,username,lastmessage FROM users")
            ulist = cur.fetchall()
            print("Processing "+dbfile.name+" with "+str(len(ulist))+" users.")
            userlist.extend(ulist)

    dbconn = sqlite3.connect(str(targetfile.absolute()))
    dbconn.execute("CREATE TABLE IF NOT EXISTS users (userid text PRIMARY KEY , username text, lastmessage text)")
    dbconn.commit()

    print("Merging above users into "+targetfile.name)
    count = 0
    for user in userlist:
        #print(" Processing user "+user[0])
        PrintOverWrite(" Processing user "+user[0])
        with dbconn:
            cur = dbconn.cursor()

            cur.execute("select * from users where userid=?",(user[0],))
            data = cur.fetchone()
            if data is None:
                # User not present in database.
                cur.execute('insert into users values(?,?,?)', (user[0], user[1],user[2]))
            else:
                cur.execute('update users set username=?, lastmessage=? where userid=?', (user[0], user[1],user[2]))


    with dbconn:
        cur.execute("select * from users")
        rows = cur.fetchall()
        print("Merged data contains " + str(len(rows)) + " users")


def PrintOverWrite(message):
    sys.stdout.write(message+"                            \r")
    sys.stdout.flush()

if __name__ == '__main__':
    MergeDBFiles()
    input("Process completed. Press any key to complete...")