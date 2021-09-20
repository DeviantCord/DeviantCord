"""

    DeviantCord 2 Discord Bot
    Copyright (C) 2020  Errite Games LLC/ ErriteEpticRikez

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
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