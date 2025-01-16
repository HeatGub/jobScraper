import sqlite3, re, datetime
import pandas as pd
from settings import DATABASE_TABLE_NAME

columnsAll = ['datetimeFirst', 'datetimeLast', 'url', 'title', 'salaryAndContract', 'salaryMin', 'salaryMax', 'employer', 'workModes', 'positionLevels', 'offerValidTo', 'location', 'techstackExpected', 'techstackOptional', 'responsibilities', 'requirements', 'optionalRequirements']

class Database():
    def createTableIfNotExists(): #if not exists
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS " + DATABASE_TABLE_NAME + """ (
                    datetimeFirst TEXT,
                    datetimeLast TEXT,
                    url TEXT,
                    title TEXT, 
                    salaryAndContract TEXT,
                    salaryMin INT,
                    salaryMax INT,
                    employer TEXT,
                    workModes TEXT,
                    positionLevels TEXT,
                    offerValidTo TEXT,
                    location TEXT,
                    techstackExpected TEXT,
                    techstackOptional TEXT,
                    responsibilities TEXT,
                    requirements TEXT,
                    optionalRequirements TEXT);""")
        connection.commit()
        cursor.close()
        connection.close()

    def selectAll():
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM" + DATABASE_TABLE_NAME +";")
        connection.commit()
        print(cursor.fetchall())
        cursor.close()
        connection.close()

    def executeQuery(query):
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        # print(cursor.fetchall())
        cursor.close()
        connection.close()
    
    def recordFound(url):
        urlPartToCompare = re.split("[?]s=", url)[0] #split on '?s=' because after that it's only session related stuff. If no pattern found url unchanged
        # print(urlPartToCompare)
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute("SELECT datetimeFirst FROM " + DATABASE_TABLE_NAME + " WHERE url LIKE ('%" + urlPartToCompare + "%');")
        connection.commit()
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        if len(result) >0:
            return True
        else:
            return False

    def insertRecord(dictionary):
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute("INSERT INTO " + DATABASE_TABLE_NAME + " VALUES (:datetimeFirst, :datetimeLast, :url, :title, :salaryAndContract, :salaryMin, :salaryMax, :employer, :workModes, :positionLevels, :offerValidTo, :location, :techstackExpected, :techstackOptional, :responsibilities, :requirements, :optionalRequirements)", dictionary)
        connection.commit()
        cursor.close()
        connection.close()

    def updateDatetimeLast(url):
        urlPartToCompare = re.split("[?]s=", url)[0] #split on '?s=' because after that it's only session related stuff. If no pattern found url unchanged
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute("UPDATE " + DATABASE_TABLE_NAME + " SET datetimeLast = '" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "'  WHERE url LIKE ('%" + urlPartToCompare + "%');")
        # cursor.execute("SELECT datetimeLast FROM " + DATABASE_TABLE_NAME + " WHERE url LIKE ('%" + urlPartToCompare + "%');")
        connection.commit()
        cursor.close()
        connection.close()
    
    def countAllRecords():
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT (*) FROM " + DATABASE_TABLE_NAME +";")
        connection.commit()
        resultTuple = cursor.fetchall()[0]
        (count,) = resultTuple #unpacking tuple
        cursor.close()
        connection.close()
        return str(count)

    def queryToDataframe(fullQuery):
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        # df = pd.read_sql("SELECT datetimeFirst, datetimeLast FROM " +DATABASE_TABLE_NAME+ ";", con=connection)
        df = pd.read_sql(fullQuery, con=connection)
        connection.commit()
        # print(cursor.fetchall())
        # print('\n'+str(len(cursor.fetchall())) + ' records found')
        cursor.close()
        connection.close()
        return df