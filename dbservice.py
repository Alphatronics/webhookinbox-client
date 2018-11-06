"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
"""

import sys
import sqlite3

DBFILE='requestdb.db'

class DbService:

    def __init__(self, db_file):
        self.dbfile=db_file
        self.connection=None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.dbfile)
        except Exception as e:
            print('[ERROR] No connection: {0}'.format(e))
            self.connection=None
    
    def disconnect(self):
        if self.connection==None:
            return
        self.connection.close()
        self.connection=None

    def showRequests(self):
        if self.connection==None:
            return
        sql = "SELECT * FROM requests"
        try:
            cur = self.connection.cursor()
            cur.execute(sql)
            rows = cur.fetchall()
            for row in rows:
                print('[INFO] {0}'.format(row))
        except Exception as e:
            print('[ERROR] Query failed: {0}'.format(e))

    def insertNewRequest(self, asyncRequestId, api):
        if self.connection==None:
            return None
        sql = "INSERT INTO requests(asyncResponseId, api) VALUES(?, ?);"
        try:
            cur = self.connection.cursor()
            cur.execute(sql, (asyncRequestId, api))
            self.connection.commit()
            return cur.lastrowid
        except Exception as e:
            print('[ERROR] Query failed: {0}'.format(e))
        return None

    def getRequest(self, asyncRequestId):
        if self.connection==None:
            return None
        sql = "SELECT * FROM requests WHERE asyncResponseId=?;"
        try:
            cur = self.connection.cursor()
            cur.execute(sql, (asyncRequestId,))
            row = cur.fetchone()
            return row
        except Exception as e:
            print('[ERROR] Query failed: {0}'.format(e))
        return None
    
    def updateNewRequest(self, asyncRequestId, responsePayload, responseStatus):
        if self.connection==None:
            return None
        sql = "UPDATE requests SET responsePayload=?, responseStatus=? WHERE asyncResponseId=?;"
        try:
            cur = self.connection.cursor()
            cur.execute(sql, (responsePayload, responseStatus, asyncRequestId))
            self.connection.commit()
            return True
        except Exception as e:
            print('[ERROR] Query failed: {0}'.format(e))
        return False

    def deleteRequest(self, asyncRequestId):
        if self.connection==None:
            return None
        sql = "DELETE FROM requests WHERE asyncResponseId=?"
        try:
            cur = self.connection.cursor()
            cur.execute(sql, (asyncRequestId,))
            self.connection.commit()
            return True
        except Exception as e:
            print('[ERROR] Query failed: {0}'.format(e))
        return False

if __name__ == '__main__':

    print('[INFO] Connecting to DB...')
    db = DbService(DBFILE)
    db.connect()
    print('[INFO] Db {0} Ready!'.format(DBFILE))
    print('[INFO] Querying data...')
    db.showRequests()

    # INSERT
    print('[INFO] Test inserting data...')
    reqid = "5796aa57-cf1f-4aa9-893e-28fa31d0c299"
    ret = db.insertNewRequest(reqid, "/30006")
    if ret > 0:
        print('[INFO] OK')
    print('[INFO] Querying data...')
    db.showRequests()

    # UPDATE
    print('[INFO] Test updating data...')
    ret = db.updateNewRequest(reqid, "Once upon a payload", 200)
    if ret == True:
        print('[INFO] OK')
    print('[INFO] Querying data...')
    db.showRequests()

    # SELECT ONE
    print('[INFO] Test selecting one...')
    ret = db.getRequest(reqid)
    if ret != None:
        print('[INFO] OK: {0}'.format(ret))

    # DELETE
    print('[INFO] Test deleting data...')
    ret = db.deleteRequest(reqid)
    if ret == True:
        print('[INFO] OK')
    print('[INFO] Querying data...')
    db.showRequests()
    db.disconnect()


