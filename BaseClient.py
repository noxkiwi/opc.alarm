import logging
import threading
import time

from opcua import Client

from BaseItem import BaseItem
from ItemValueCache import ItemValueCache
from RemoteSubscriptionHandler import RemoteSubscriptionHandler
from noxLogger import noxLogger


class BaseClient(Client):
    # I am the thread where the connection is pinged within.
    pingThread = None
    # I am the status whether to scan or not to scan.
    scanEnabled = False
    # I am the result of each ping. I determine whether this client is connected to the server.
    isConnected = False
    # I am the status of the initialisation. After initialisation, you won't be able to add more items.
    isInitialized = False
    # I am the list of RemoteSubscriptionHandler instances
    RemoteSubscriptionHandlers = []
    # I am the list of opcItem instances
    opcItems = []
    remoteHandler = RemoteSubscriptionHandler()
    remotesub = None

    # I will solely return the name of the server I will connect to.
    def getServerName(self):
        return self.server_url.netloc

    # I will add the given opcItem to the list of opcItems
    def addOpcItem(self, myBaseItem: BaseItem):
        if self.isInitialized:
            noxLogger.error("0x00010071 Cannot add opcItem " + myBaseItem.OpcItemAddress + " to Server " + myBaseItem.getServerName())
            return
        self.opcItems.append(myBaseItem)
        noxLogger.debug("0x00010072 Added opcItem " + myBaseItem.OpcItemAddress + " to Server " + myBaseItem.getServerName())

    # I will return the pingThread and create it before if not set.
    def getPingThread(self):
        if self.pingThread is None:
            self.pingThread = threading.Thread(target=self.ping)
        return self.pingThread

    # I will initialize the BaseClient.
    def initialize(self):
        if self.isInitialized:
            noxLogger.error("0x00010051 Cannot initialize - Already initialized")
            return
        self.scanEnabled = True
        self.getPingThread().start()
        noxLogger.info("0x00010052 Now initialized")

    # Start up a new connection.
    def doConnect(self):
        self.secure_channel_timeout = 100000
        self.session_timeout = 100000

        if not self.isConnected:
            self.connect()

        if self.isInitialized:
            return True

        self.remotesub = self.create_subscription(1000, self.remoteHandler)
        try:
            for myBaseItem in self.opcItems:
                try:
                    myBaseItem.RemoteNode = self.get_root_node().get_child(myBaseItem.NodePath)
                except Exception as e:
                    logging.fatal(e)
                    noxLogger.error("0x00000043 " + myBaseItem.getIdentity())
                    continue

                ItemValueCache.AddRemoteNode(myBaseItem)
                self.remotesub.subscribe_data_change(myBaseItem.RemoteNode)
                noxLogger.debug("0x00000042 " + myBaseItem.getIdentity())
            noxLogger.notice("0x00000044 Connected all items for server " + self.getServerName())

        except:
            noxLogger.error("0x00000045 Item Connection error on server " + self.getServerName())
            self.setDisconnected()
            return False

        self.setConnected()
        self.setInitialized()
        return True

    # securely remove previous connection.
    def unConnect(self):
        self.setDisconnected()
        self.setUninitialized()

        try:
            self.resetSubscriptions()
        except:
            noxLogger.error("0x00010061 Error while resetting Subscriptions for " + self.getServerName())
        try:
            self.disconnect()
        except:
            noxLogger.error("0x00010062 Error while disconnecting from " + self.getServerName())

    # I will reset all subscriptions.
    def resetSubscriptions(self):
        for subscription in self.RemoteSubscriptionHandlers:
            self.deleteSubscription(subscription)
        self.RemoteSubscriptionHandlers = []
        noxLogger.info("BaseClient - resetSubscriptions - Success: Removed subscriptions for server " + self.getServerName())

    # I will delete the given subscription. This is only for stability reasons.
    def deleteSubscription(self, subscription):
        try:
            subscription.delete()
        except:
            noxLogger.info("BaseClient - deleteSubscription - Error: Removed subscription for server " + self.getServerName())

    # I will have the connection checked in intervals. If not connected I will try to reconnect.
    def ping(self):
        while self.scanEnabled:
            try:
                self.doConnect()
            except:
                self.unConnect()
                while not self.isConnected:
                    try:
                        self.doConnect()
                    except:
                        self.unConnect()
                        noxLogger.error("BaseClient - ping: Failed to connect to " + self.getServerName())
                    time.sleep(5)
            time.sleep(1)

    # I will set the isConnected flag to true if not already so. Also I will log the new connection status.
    def setConnected(self):
        if self.isConnected:
            noxLogger.debug("0x00010011 Already connected to " + self.getServerName())
            return None
        self.isConnected = True
        noxLogger.info("0x00010012 Now I am connected to " + self.getServerName())

    # I will set the isConnected flag to false if not already so. Also I will log the new connection status.
    def setDisconnected(self):
        if not self.isConnected:
            noxLogger.debug("0x00010021 Already disconnected from " + self.getServerName())
            return None
        self.isConnected = False
        noxLogger.info("0x00010022 Now I am disconnected from " + self.getServerName())

    # I will add the initialized flag.
    def setInitialized(self):
        if self.isInitialized:
            noxLogger.debug("0x00010031 Already initialized to " + self.getServerName())
            return None
        self.isInitialized = True
        noxLogger.info("0x00010032 Now I am initialized to " + self.getServerName())

    # I will remove the initialized flag.
    def setUninitialized(self):
        if not self.isInitialized:
            noxLogger.debug("0x00010041 Already uninitialized from " + self.getServerName())
            return None
        self.isInitialized = False
        noxLogger.info("0x00010042 Now I am uninitialized from " + self.getServerName())
