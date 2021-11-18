from ItemValueCache import ItemValueCache
from noxLogger import noxLogger


# I am the internal RemoteSubscriptionHandler of the BaseServer
class RemoteSubscriptionHandler(object):

    # I will update the given node to the given value when changed.
    def datachange_notification(self, node, val, data):
        if val is None:
            noxLogger.error("0x00020021 value is None.")
            return None

        RemoteNode = ItemValueCache.GetRemoteNode(node)
        if RemoteNode is None:
            noxLogger.error("0x00020022 RemoteNode is None.")
            return None

        ItemValueCache.SetData(RemoteNode.OpcItemAddress, val)
        LocalNode = RemoteNode.LocalNode

        if LocalNode is None:
            noxLogger.error("0x00020023 LocalNode is None.")
            return None

        try:
            CurrentValue = LocalNode.get_value()
        except:
            noxLogger.error("0x00020024 LocalNode cannot be read " + str(val))
            return None

        if CurrentValue == val:
            noxLogger.debug("0x00020025 LocalNode Is Already " + str(val))
            return None
        try:
            LocalNode.set_value(val)
        except:
            noxLogger.error("0x00020026 LocalNode is not Writeable.")
            return None

        noxLogger.debug("0x00020027 LocalNode Is Changed.")
        return True

    def event_notification(self, event):
        return None
