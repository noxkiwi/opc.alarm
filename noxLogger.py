from ConfigManager import ConfigManager
import time

configManager = ConfigManager()

# I am the logging class.
class noxLogger:
    logEmergency = 5
    logAlert = 4
    logCritical = 3
    logError = 2
    logWarning = 1
    logNotice = 0
    logInfo = -1
    logDebug = -2

    # I will write the given text into stdout.
    def write(text):
        with open(configManager.get("logging>LogFile"), "a") as logFile:
            timestamp = time.strftime('%Y-%m-%d %H:%m:%S %z')
            prefix    = configManager.get("logging>Prefix")
            logFile.write(timestamp + prefix + text + "\n")

    # I will decide whether to log the given text or not based on the given level.
    def writeLog(text, level):
        if level < configManager.get("logging>LogLevel"):
            return
        noxLogger.write(text)

    # I will write an emergency log entry.
    def emergency(text):
        noxLogger.writeLog("[Emergency] " + text, noxLogger.logEmergency)

    # I will write an alert log entry.
    def alert(text):
        noxLogger.writeLog("    [Alert] " + text, noxLogger.logAlert)

    # I will write a critical log entry.
    def critical(text):
        noxLogger.writeLog(" [Critical] " + text, noxLogger.logCritical)

    # I will write an error log entry.
    def error(text):
        noxLogger.writeLog("    [Error] " + text, noxLogger.logError)

    # I will write a warning log entry.
    def warning(text):
        noxLogger.writeLog("  [Warning] " + text, noxLogger.logWarning)

    # I will write a notice log entry.
    def notice(text):
        noxLogger.writeLog("   [Notice] " + text, noxLogger.logNotice)

    # I will write an info log entry.
    def info(text):
        noxLogger.writeLog("     [Info] " + text, noxLogger.logInfo)

    # I will write an debug log entry.
    def debug(text):
        noxLogger.writeLog("    [Debug] " + text, noxLogger.logDebug)
