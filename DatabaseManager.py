import os
import shutil
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from noxLogger import noxLogger
from ConfigManager import ConfigManager
import logging

# I am the manager for the database. Duh. What else?
class DatabaseManager:
    # I am the configuration manager.
    configManager = None
    # I am the host name for the connection.
    HostName = None
    # I am the port for the connection.
    Port = None
    # I am the user name for the connection.
    UserName = None
    # I am the password for the connection.
    PassWord = None
    # I am the database for the connection.
    DataBase = None

    def GetDatabase(self):
        try:
            self.configManager = ConfigManager()
            self.HostName      = self.configManager.get("database>HostName")
            self.Port          = self.configManager.get("database>Port")
            self.UserName      = self.configManager.get("database>UserName")
            self.PassWord      = self.configManager.get("database>PassWord")
            self.DataBase      = self.configManager.get("database>DataBase")
            noxLogger.debug("[0x10000011] - Starting MySQL Connection")
            noxLogger.debug("             - HostName: " + self.HostName)
            noxLogger.debug("             -     Port: " + str(self.Port))
            noxLogger.debug("             - UserName: " + self.UserName)
            noxLogger.debug("             - PassWord: " + self.PassWord)
            noxLogger.debug("             - DataBase: " + self.DataBase)

            myDb = mysql.connector.connect(
                host=self.HostName,
                user=self.UserName,
                password=self.PassWord,
                db=self.DataBase
            )
            return myDb
        except Exception as e:
            noxLogger.error("[0x10000010] - Cannot connect to database at " + str(self.HostName))
            logging.fatal(e)

    # I will modify data (CREATE, UPDATE, DELETE)
    def query(self, queryString, queryData):
        myDb = self.GetDatabase()
        myCursor = myDb.cursor()
        try:
            noxLogger.debug("[0x10000011] - Starting query on " + str(self.HostName))
            noxLogger.debug("             - " + queryString)
            myCursor.execute(queryString)
            myDb.commit()
        except Exception as e:
            noxLogger.error("[0x10000010] - Query has failed on host " + str(self.HostName))
            noxLogger.error("             - " + queryString)
            logging.fatal(e)
        finally:
            myCursor.close()
            myDb.close()

    # I will only READ data.
    def read(self, queryString, queryData):
        myDb = self.GetDatabase()
        myCursor = myDb.cursor()
        try:
            noxLogger.debug("[0x10000021] - Starting query on " + str(self.HostName))
            noxLogger.debug("             - " + queryString)
            myCursor.execute(queryString)
            result = myCursor.fetchall()
            return result
        except Exception as e:
            noxLogger.error("[0x10000020] - Query has failed on host " + str(self.HostName))
            noxLogger.error("             - " + queryString)
            logging.fatal(e)
        finally:
            myCursor.close()
            myDb.close()
