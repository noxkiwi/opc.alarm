import json

# I am the class to read configuration based on the "config.json" file in the project directory.
class ConfigManager:
    # I am the path to the configuration file.
    path = None
    # I am the file handle to the configuration file.
    file = None
    # I am the JSON content of the configuration file.
    data = None

    # I will construct the ConfigManager.
    def __init__(self):
        self.path = "config.json"
        self.file = open(self.path, "r")
        self.data = json.load(self.file)

    # I will return the value that is stored behind the given key.
    def get(self, key):
        return self.data[key]
