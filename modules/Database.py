import sqlite3, re, datetime
import pandas as pd
from settings import DATABASE_TABLE_NAME, DATABASE_COLUMNS
DATABASE_FILE_NAME = 'database.db'

# multiple processes can't share same sqlite connection - create and close a new connection everytime (more than enough for that request frequency)
def createDatabaseConnectionAndCursor():
    # timeout=10 - wait 10 seconds before raising databaseLocked exception (happens on simultaneous write attempts)
    connection = sqlite3.connect(DATABASE_FILE_NAME, timeout=1, check_same_thread=False)
    cursor = connection.cursor()
    return connection, cursor
    
def closeDatabaseConnectionAndCursor(connection, cursor):
    try:
        cursor.close()
        connection.close()
    except Exception as exception: # shouldn't reach this point, but its safer like this
        print(exception)

class Database(): # this class is just for functions encapsulation, no instance is ever created

    def createTableIfNotExists(): #if not exists
        try:
            connection, cursor = createDatabaseConnectionAndCursor()
            # PREPARE STRING TO CREATE DB FROM
            databaseColumnsCreationString = ''
            for column in DATABASE_COLUMNS:
                databaseColumnsCreationString += f"""{column['dbColumnName']} {column['dataType']} DEFAULT {column['default']}, """ 
            databaseColumnsCreationString = re.sub(r',\s*$', '', databaseColumnsCreationString) # remove the comma and space(s) from the end
            # print(databaseColumnsCreationString)
            # EXECUTE COMMAND
            cursor.execute("CREATE TABLE IF NOT EXISTS " + DATABASE_TABLE_NAME + "("+ databaseColumnsCreationString +");")
            connection.commit()
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback() # rollback database changes if any were made
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)

    def selectAll():
        try:
            connection, cursor = createDatabaseConnectionAndCursor() 
            cursor.execute("SELECT * FROM" + DATABASE_TABLE_NAME +";")
            connection.commit()
            # print(cursor.fetchall())
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback()
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)

    def executeQuery(query):
        try:
            connection, cursor = createDatabaseConnectionAndCursor() 
            cursor.execute(query)
            connection.commit()
            # print(cursor.fetchall())
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback()
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)
    
    def recordFound(url):
        try:
            connection, cursor = createDatabaseConnectionAndCursor() 
            urlPartToCompare = re.split("[?]s=", url)[0] #split on '?s=' because after that it's only session related stuff. If no pattern found url stays unchanged (so it's just a whole URL for justjoin)
            # print(urlPartToCompare)
            cursor.execute("SELECT datetimeFirst FROM " + DATABASE_TABLE_NAME + " WHERE url LIKE ('%" + urlPartToCompare + "%');") # also matches if urlPartToCompare is a part of another URL. But that's okay since these are usually the same offers
            connection.commit()
            result = cursor.fetchall()
            if len(result) >0:
                return True
            else:
                return False
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback()
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)

    def insertRecord(dictionary):
        try:
            connection, cursor = createDatabaseConnectionAndCursor() 
            # PREPARE COLUMN NAMES STR FROM PASSED DICTIONARY CONTAINING ONLY COMMON K-V PAIRS
            columnValuesString = ''
            for name in dictionary.keys():
                columnValuesString += f":{name}, "
            columnValuesString = re.sub(r',\s*$', '', columnValuesString) # remove the comma and space(s) from the end
            columnNamesString = re.sub(r':', '', columnValuesString) # just remove every :
            # EXECUTE INSERT
            cursor.execute("INSERT INTO " + DATABASE_TABLE_NAME + " ("+columnNamesString+") VALUES ("+columnValuesString+")", dictionary)
            connection.commit()
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback()
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)

    def updateDatetimeLast(url):
        try:
            connection, cursor = createDatabaseConnectionAndCursor() 
            urlPartToCompare = re.split("[?]s=", url)[0] #split on '?s=' because after that it's only session related stuff. If no pattern found url unchanged
            cursor.execute("UPDATE " + DATABASE_TABLE_NAME + " SET datetimeLast = '" + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "'  WHERE url LIKE ('%" + urlPartToCompare + "%');")
            # cursor.execute("SELECT datetimeLast FROM " + DATABASE_TABLE_NAME + " WHERE url LIKE ('%" + urlPartToCompare + "%');")
            connection.commit()
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback()
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)
    
    def countAllRecords():
        try:
            connection, cursor = createDatabaseConnectionAndCursor() 
            cursor.execute("SELECT COUNT (*) FROM " + DATABASE_TABLE_NAME +";")
            connection.commit()
            resultTuple = cursor.fetchall()[0]
            (count,) = resultTuple #unpacking tuple
            return str(count)
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback()
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)

    def queryToDataframe(fullQuery):
        try:
            connection, cursor = createDatabaseConnectionAndCursor() 
            # df = pd.read_sql("SELECT datetimeFirst, datetimeLast FROM " +DATABASE_TABLE_NAME+ ";", con=connection)
            df = pd.read_sql(fullQuery, con=connection)
            connection.commit()
            # print(cursor.fetchall())
            # print('\n'+str(len(cursor.fetchall())) + ' records found')
            return df
        except sqlite3.Error as sqliteError:
            print(f"SQLite Error: {sqliteError}")
            connection.rollback()
        finally:
            closeDatabaseConnectionAndCursor(connection, cursor)