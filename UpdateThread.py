import threading
import time

from ArchiveThread import ArchiveThread

# I am an interval based ArchiveThread
class IntervalArchiveThread(ArchiveThread):
    def __init__(self, groupItem):
        self.groupItem = groupItem
        self.scanEnable = False
        self.saveThread = threading.Thread(target=self.runThread)
        self.saveThread.start()

    # I am the list of fieldNames and fieldValues for the next entry in the archive db.
    fields = {}
    # I am the save thread.
    saveThread = None

    def runThread(self):
        while True:
            self.saveEntry()
            time.sleep(self.groupItem.group_interval / 1000)

    # I am triggered from the subscription and tell the ArchiveThread to "Store this value for next entry!"
    def subscriptionTriggered(self, field, value):
        self.fields[field] = value

    # I will save the current entry.
    def saveEntry(self):
        fieldSql = ""
        valueSql = ""
        for fieldName in self.fields.keys():
            fieldSql = fieldSql + ", " + fieldName
            valueSql = valueSql + ", " + str(self.fields[fieldName])

        sql = "INSERT INTO entry (entry_created" + fieldSql + ") VALUES (CURRENT_TIMESTAMP" + valueSql + ");"
        return None
