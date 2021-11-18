# RelayItem fields.
class BaseItem:
    OpcItemId = None
    OpcItemCreated = None
    OpcItemModified = None
    OpcItemFlag = None
    OpcItemAddress = None
    ServerId = None
    OpcItemDatatype = None
    OpcItemLastValue = None
    ServerItem = None
    LocalNode = None
    RemoteNode = None
    NodePath = None

    def __init__(self, row):
        self.OpcItemId = row[0]
        self.OpcItemCreated = row[1]
        self.OpcItemModified = row[2]
        self.OpcItemFlag = row[3]
        self.OpcItemAddress = row[4]
        self.ServerId = row[5]
        self.OpcItemDatatype = row[6]
        self.OpcItemLastValue = row[7]
        self.NodePath = None

    def update(self):
        return None

    def getServerName(self):
        return self.ServerItem.ServerAddress + ":" + str(self.ServerItem.ServerPort)

    def getIdentity(self):
        return self.OpcItemAddress + " on " + self.getServerName()
