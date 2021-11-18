from noxLogger import noxLogger


class ItemValueCache:
    # I am the plain Key Value Storage
    PlainData = {}
    # I am the list of Remote Items.
    RemoteItems = {}
    # I am the list of Local Items.
    LocalItems = {}
    # I am the dict of PVName->Item.
    ProcessVariables = {}

    # I will set the current value of the given itemAddress into the instance for later use through APIs
    def setCurrentData(itemAddress, itemValue):
        noxLogger.error("0x00040011 " + itemAddress + " changed to " + str(itemValue))
        ItemValueCache.PlainData[itemAddress] = itemValue

    # I will add the remote item identified by the node object.
    def AddLocalNode(BaseItem):
        ItemValueCache.LocalItems[BaseItem.LocalNode] = BaseItem

    # I will add the given BaseItem to the list of PVNames
    def AddProcessVariable(BaseItem):
        ItemValueCache.ProcessVariables[BaseItem.OpcItemAddress] = BaseItem

    # I will return the desired BaseItem.
    def GetProcessVariable(OpcItemAddress):
        return ItemValueCache.ProcessVariables[OpcItemAddress]

    # I will add the remote item identified by the node object.
    def AddRemoteNode(BaseItem):
        ItemValueCache.RemoteItems[ItemValueCache.GetSimpleRemoteName(BaseItem.RemoteNode)] = BaseItem

    def GetSimpleRemoteName(RemoteNode):
        return str(RemoteNode.server) + "_" + str(RemoteNode)

    # I will return the remote item identified by the given remoteNode.
    def GetRemoteNode(RemoteNode):
        try:
            return ItemValueCache.RemoteItems[ItemValueCache.GetSimpleRemoteName(RemoteNode)]
        except KeyError:
            noxLogger.error("ItemValueCache - getRemoteItem: KeyError")
            return None

    # I will return the remote item identified by the given localNode.
    def GetLocalNode(LocalNode):
        try:
            return ItemValueCache.LocalItems[LocalNode]
        except KeyError:
            noxLogger.error("ItemValueCache - getLocalNode: KeyError")
            return None

    # I will set the plainData object for the given address.
    def SetData(Name, Value):
        ItemValueCache.PlainData[Name] = Value;

    # I will return the complete plainData Object.
    def GetData():
        return ItemValueCache.PlainData
