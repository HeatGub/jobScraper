import sqlite3, re, datetime
import pandas as pd
from settings import DATABASE_TABLE_NAME, DATABASE_COLUMNS

class Database():
    def createTableIfNotExists(): #if not exists
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        
        # PREPARE STRING TO CREATE DB FROM
        databaseColumnsCreationString = ''
        for key, value in DATABASE_COLUMNS.items():
            databaseColumnsCreationString += f"""{key} {value['dataType']} DEFAULT {value['default']}, """ 
        databaseColumnsCreationString = re.sub(r',\s*$', '', databaseColumnsCreationString) # remove the comma and space(s) from the end

        # EXECUTE COMMAND
        cursor.execute("CREATE TABLE IF NOT EXISTS " + DATABASE_TABLE_NAME + "("+ databaseColumnsCreationString +");")
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
        urlPartToCompare = re.split("[?]s=", url)[0] #split on '?s=' because after that it's only session related stuff. If no pattern found url stays unchanged (so it's just a whole URL for justjoin)
        # print(urlPartToCompare)
        connection = sqlite3.connect('results.db')
        cursor = connection.cursor()
        cursor.execute("SELECT datetimeFirst FROM " + DATABASE_TABLE_NAME + " WHERE url LIKE ('%" + urlPartToCompare + "%');") # also matches if urlPartToCompare is a part of another URL. But that's okay since these are usually the same offers
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
        # PREPARE COLUMN NAMES STR FROM PASSED DICTIONARY CONTAINING ONLY COMMON K-V PAIRS
        columnValuesString = ''
        for name in dictionary.keys():
            columnValuesString += f":{name}, "
        columnValuesString = re.sub(r',\s*$', '', columnValuesString) # remove the comma and space(s) from the end
        columnNamesString = re.sub(r':', '', columnValuesString) # just remove every :
        # EXECUTE INSERT
        cursor.execute("INSERT INTO " + DATABASE_TABLE_NAME + " ("+columnNamesString+") VALUES ("+columnValuesString+")", dictionary)
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