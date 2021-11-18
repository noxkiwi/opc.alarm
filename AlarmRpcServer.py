from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from noxLogger import noxLogger
from ConfigManager import ConfigManager


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = '/alarm'


# I am the RPC Server that is used to communicate with the web-based frontend.
class AlarmRpcServer:
    # I am the configuration manager
    configManager = None
    server = None
    AlarmService = None

    # Construct the Service.
    def __init__(self, AlarmService):
        self.configManager = ConfigManager()
        self.AlarmService = AlarmService
        hostname = self.configManager.get("xmlrpc>HostName")
        port = self.configManager.get("xmlrpc>Port")
        self.server = SimpleXMLRPCServer((hostname, port), requestHandler=RequestHandler)
        self.server.register_introspection_functions()
        self.server.register_function(self.getCounter)
        self.server.register_function(self.count)
        self.server.register_function(self.list)
        self.server.register_function(self.acknowledge)

    # Starts the server
    def start(self):
        self.server.serve_forever()

    # Returns the change counter of the AlarmService.
    def getCounter(self):
        try:
            ret = self.AlarmService.getCounter()
            return ret
        except Exception as e:
            noxLogger.error("AlarmRpcServer - count: Unable obtain counter")

    # Returns the counter
    def count(self):
        return self.getCounter()

    # Returns the list of alarms.
    def list(self):
        try:
            ret = self.AlarmService.getList()
            return ret
        except Exception as e:
            noxLogger.error("AlarmRpcServer - list: Unable to read alarms")

    # Acknlowedges the given alarm.
    def acknowledge(self, alarm):
        self.AlarmService.acknowledge(alarm)
        return True
