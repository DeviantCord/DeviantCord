import json
import logging

def createConfig():
    logger = logging.getLogger('errite.config.configManager')
    try:
        print("configManager: Creating config.json")
        config = open("config.json", "a+")
        print("configManager: Writing to config.json")
        config.write("{\n}")
        config.close()
        with open("config.json", "r") as jsonFile:
            configdata = json.load(jsonFile)
            jsonFile.close()
            configdata["version"] = "bt-1.2.5"
            configdata["logchannelid"] = 0
            configdata["roleid"] = 0
            configdata["prefix"] = "$"
            configdata["logging"] = True
            configdata["publicmode"] = False
            configdata["errite"] = False
            configdata["errite-channel"] = 0
            configdata["region"] = "not-setup"
            configdata["server"] = "server-name"
            configdata["client"] = "discord-server-name"
            configdata["rolesetup-enabled"] = True
            configdata["guildid"] = 0
            configdata["sync-time"] = 900
            jsonFile = open("config.json", "w+")
            jsonFile.write(json.dumps(configdata, indent=4, sort_keys=True))
            jsonFile.close()
            return True;
    except IOError:
        print("ERROR: Experienced IO Error when creating config.json")
        return False;


def createSensitiveConfig():
    logger = logging.getLogger('errite.config.configManager')
    try:
        print("configManager: Creating client.json")
        config = open("client.json", "a+")
        print("configManager: Writing to client.json")
        config.write("{\n}")
        config.close()
        with open("client.json", "r") as jsonFile:
            configdata = json.load(jsonFile)
            jsonFile.close()
            configdata["discord-token"] = "discordtoken"
            configdata["da-client-id"] = "id here"
            configdata["da-secret"] = "secret"
            jsonFile = open("client.json", "w+")
            jsonFile.write(json.dumps(configdata, indent=4, sort_keys=True))
            jsonFile.close()
            return True;
    except IOError:
        print("ERROR: Experienced IO Error when creating client.json")
        return False;f