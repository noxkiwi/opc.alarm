import os
import sqlite3
import threading
import time

from AlarmRpcServer import AlarmRpcServer
from BaseClient import BaseClient
from AlarmGroupItem import AlarmGroupItem
from AlarmItem import AlarmItem
from noxLogger import noxLogger
from DatabaseManager import DatabaseManager
from ConfigManager import ConfigManager

# I am the collector service.
class AlarmService:
    configManager = ConfigManager()
    workingDirectory = os.path.dirname(os.path.realpath(__file__))
    namespace = "nox.lightsystem.opc.alarm"
    baseClient = None  # I am the opcClient of the opc.base service.
    archiveThreads = {}  # I am the list of ArchiveThread instances, co-ordinated by the group_id.
    alarmItems = {}
    server = None
    tree = {}
    scanThread = None
    scanEnable = False
    alarmRpcServer = None
    alarmRpcServerThread = None
    count = 0

    def __init__(self, server, servernamespace):
        self.configManager = ConfigManager()
        self.server = server
        self.serverNamespace = servernamespace
        # Register Root node
        self.root = self.server.get_objects_node()
        HostName  = self.configManager.get("baseServer>HostName")
        Port      = self.configManager.get("baseServer>Port")
        Endpoint  = self.configManager.get("baseServer>EndPoint")
        print("opc.tcp://" + HostName + ":" + str(Port) + "/" + Endpoint)
        self.baseClient = BaseClient("opc.tcp://" + HostName + ":" + str(Port) + "/" + Endpoint)
        self.baseClient.connect()
        self.connectGroups()
        self.makeServer()

    # Connect to all groups.
    def connectGroups(self):
        dm = DatabaseManager()
        # Load all active alarm groups.
        queryString    = "SELECT * FROM `alarm_group` WHERE `alarm_group_flags` &1=1;"
        queryData      = (1,2,3)
        alarmGroupRows = dm.read(queryString, queryData)

        for alarmGroupRow in alarmGroupRows:
            alarmGroupItem = AlarmGroupItem(alarmGroupRow, self.baseClient)
            
            # Then load all active alarms from that group!
            queryString   = """
SELECT 
	`alarm_item`.`alarm_item_id`,
	`alarm_item_created`,
	`alarm_item_modified`,
	`alarm_item_flags`,
	`alarm_item_name`,
	`readItem`.`opc_item_address` AS `readAddress`,
	`alarmItem`.`opc_item_address` AS `writeAddress`,
	`cameItem`.`opc_item_address` AS `cameAddress`,
	`goneItem`.`opc_item_address` AS `goneAddress`,
	`ackItem`.`opc_item_address` AS `ackAddress`,
	`alarm_item`.`alarm_item_hysteresis_seconds`,
	`alarm_item`.`alarm_item_hysteresis_value`,
	`alarm_item`.`alarm_item_comparison_type`,
	`alarm_item`.`alarm_item_compare_value`,
	`alarm_item`.`alarm_item_valence_on`,
	`alarm_item`.`alarm_item_valence_off`
FROM	`alarm_item`
JOIN	`opc_item`	AS	`readItem`	ON(`readItem`.`opc_item_id` = `alarm_item`.`opc_item_id_read`)
JOIN	`opc_item`	AS	`alarmItem`	ON(`alarmItem`.`opc_item_id` = `alarm_item`.`opc_item_id_alarm`)
JOIN	`opc_item`	AS	`cameItem`	ON(`cameItem`.`opc_item_id` = `alarm_item`.`opc_item_id_came`)
JOIN	`opc_item`	AS	`goneItem`	ON(`goneItem`.`opc_item_id` = `alarm_item`.`opc_item_id_gone`)
JOIN	`opc_item`	AS	`ackItem`	ON(`ackItem`.`opc_item_id` = `alarm_item`.`opc_item_id_ack`)
WHERE TRUE
	AND	`readItem`.`opc_item_flags`		&1=1
	AND	`alarmItem`.`opc_item_flags`	&1=1
	AND	`cameItem`.`opc_item_flags`		&1=1
	AND	`goneItem`.`opc_item_flags`		&1=1
	AND	`ackItem`.`opc_item_flags`		&1=1
	AND	`alarm_item`.`alarm_item_flags`	&1=1
	AND	`alarm_item`.alarm_group_id =  """ + str(alarmGroupItem.alarm_group_id)
            queryData     = (1,2,3)
            alarmItemRows = dm.read(queryString, queryData)

	
            for alarmItemRow in alarmItemRows:
                alarmItem = AlarmItem(alarmItemRow, self, alarmGroupItem)
                self.connect(alarmItem)
                self.alarmItems[alarmItem.alarm_address_write] = (alarmItem)

    # Return last Node name
    def GetEndNode(self, tree):
        return tree.split(".")[-1]

    # Generate Tree Branches and the end node.
    def MakeNode(self, tree):
        return self.GetBranchedNode(tree).add_variable(self.serverNamespace, self.GetEndNode(tree), 1)

    # Create new branches to the end node
    # JG.WHG.OG.LR.SOCKET01.OM.B_VALUE
    def GetBranchedNode(self, tree):
        branches = tree.split(".")  # ["JG", "WHG", "OG", "LR", "SOCKET01", "OM", "B_VALUE"]
        branchAddress = ""  # String to identify existing branches in tree.
        branchIndex = 1  # Index to count through all branches.
        parentNode = self.root  # Forces first branch to branch off the server root node.
        delim = ""
        del branches[-1]
        for branch in branches:
            branchAddress = branchAddress + delim + branch
            if not branchAddress in self.tree:
                parentNode = parentNode.add_object(self.serverNamespace, branch)
                self.tree[branchAddress] = parentNode
            else:
                parentNode = self.tree[branchAddress]
            delim = "."
            branchIndex = branchIndex + 1
        return parentNode

    # Start the server
    def start(self):
        self.server.start()

    # Stop the server
    def stop(self):
        self.server.stop()

    def connect(self, alarmItem):
        self.connectRead(alarmItem)
        self.connectWrite(alarmItem)
        self.connectCame(alarmItem)
        self.connectGone(alarmItem)
        self.connectAck(alarmItem)

    def MakeNodePath(self, address):
        branches = address.split(".")
        ret = []
        ret.append("0:Objects")
        for branch in branches:
            ret.append("2:" + branch)
        return ret

    def connectRead(self, alarmItem):
        alarmItem.node_read = alarmItem.alarmGroupItem.baseClient.get_root_node().get_child(self.MakeNodePath(alarmItem.alarm_address_read))

    def connectWrite(self, alarmItem):
        alarmItem.node_write = self.connectAddress(alarmItem.alarm_address_write)
        alarmItem.node_write.set_value(alarmItem.alarm_item_valence_off)

    def connectCame(self, alarmItem):
        if alarmItem.alarm_address_came is None:
            return
        alarmItem.node_came = self.connectAddress(alarmItem.alarm_address_came)
        alarmItem.node_came.set_value("")

    def connectGone(self, alarmItem):
        if alarmItem.alarm_address_gone is None:
            return
        alarmItem.node_gone = self.connectAddress(alarmItem.alarm_address_gone)
        alarmItem.node_gone.set_value("")

    def connectAck(self, alarmItem):
        if alarmItem.alarm_address_ack is None:
            return
        alarmItem.node_ack = self.connectAddress(alarmItem.alarm_address_ack)
        alarmItem.node_ack.set_value("")

    # Generate Tree Branches and the end node.
    def MakeNode(self, tree):
        return self.GetBranchedNode(tree).add_variable(self.serverNamespace, self.GetEndNode(tree), 1)

    # I will connect the OPC Item and put the remoteNode node in it.
    def connectAddress(self, address):
        return self.MakeNode(address)

    # I will return the array of nodes to the given address.
    def makeNodePath(self, address):
        branches = address.split(".")
        ret = []
        ret.append("0:Objects")
        for branch in branches:
            ret.append("2:" + branch)
        return ret

    def increaseCounter(self):
        self.count = self.count + 1
        return self.getCounter()

    def getCounter(self):
        return self.count

    def getList(self):
        retVal = {}
        for key, value in self.alarmItems.items():
            retVal[value.alarm_address_write] = value.getData()
        return retVal

    def _scan(self):
        while self.scanEnable:
            for key, value in self.alarmItems.items():
                value.work()
            time.sleep(1)

    def scan_on(self):
        self.scanThread = threading.Thread(target=self._scan)
        self.scanEnable = True
        self.scanThread.start()

    def scan_off(self):
        self.scanEnable = False
        self.scanThread.join()

    def acknowledge(self, alarm):
        self.alarmItems[alarm].acknowledge()

    def makeServer(self):
        self.alarmRpcServer = AlarmRpcServer(self)
        self.alarmRpcServerThread = threading.Thread(target=self.serverThread)
        self.alarmRpcServerThread.start()

    def serverThread(self):
        self.alarmRpcServer.start()
