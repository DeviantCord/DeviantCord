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
import logging
import json
from errite.tools.mis import fileExists

def convert20():
    logger = logging.getLogger('errite.config.configManager')
def convert():
    logger = logging.getLogger('errite.config.configManager')
    triggered = False
    with open("config.json", "r") as jsonFile:
        configdata = json.load(jsonFile)
        jsonFile.close()
        if configdata["version"] == "bt-1.0.0":
            triggered = True
            logger.info("Converter found version bt-1.0.0 config")
            if not configdata["roleid"] == 0:
                configdata["rolesetup-enabled"] = False
            else:
                configdata["rolesetup-enabled"] = True
            configdata["version"] = "bt-1.0.1"
        if configdata["version"] == "bt-1.0.1":
            triggered = True
            configdata["version"] = "bt-1.2.0"
        if configdata["version"] == "bt-1.2.0":
            triggered = True
            configdata["errite"] = False
            configdata["errite-channel"] = 0
            configdata["region"] = "not-setup"
            configdata["server"] = "server-name"
            configdata["client"] = "discord-server-name"
            configdata["version"] = "bt-1.2.5"
        if triggered:
            jsonFile = open("config.json", "w+")
            jsonFile.write(json.dumps(configdata, indent=4,sort_keys=True))
            jsonFile.close()
            triggered = False
    if fileExists("artdata.json"):
        with open("artdata.json", "r") as jsonFile:
            artdata = json.load(jsonFile)
            if artdata["version"] == "bt-1.0.0":
                logger.info("Converter found version bt-1.0.0 ArtData")
                artdata["version"] = "bt-1.0.1"
                triggered = True
            if artdata["version"] == "bt-1.0.1":
                logger.info("Converter found version bt-1.0.1 ArtData")
                artdata["version"] = "bt-1.2.0"
                if len(artdata["artist_store"]["used-artists"]) > 0:
                    output = "**Current Folder Listeners**\n"
                    for artist in artdata["artist_store"]["used-artists"]:
                        for folder in artdata["art-data"][artist]["folder-list"]:
                            if artdata["art-data"][artist][folder]["inverted-folder"]:
                                logger.info(artist +"'s " + folder + "is inverted putting in hybrid as false")
                                artdata["art-data"][artist][folder]["hybrid"] = False
                                triggered = True
                            if not artdata["art-data"][artist][folder]["inverted-folder"]:
                                logger.info(artist + "'s " + folder + "is inverted putting in hybrid as false")
                                artdata["art-data"][artist][folder]["hybrid"] = True
                                triggered = True
            if artdata["version"] == "bt-1.2.0":
                triggered = True
                logger.info("Converter found version bt-1.2.0")
                artdata["version"] = "bt-1.4.0"
                if len(artdata["artist_store"]) > 0:
                    for artist in artdata["artist_store"]["used-artists"]:
                        artdata["art-data"][artist]["folders"] = {}
                        for folder in artdata["art-data"][artist]["folder-list"]:
                            print(folder)
                            artdata["art-data"][artist]["folders"][folder] = artdata["art-data"][artist][folder]
                            del artdata["art-data"][artist][folder]
                        artdata["art-data"][artist]["folders"]["folder-list"] = artdata["art-data"][artist]["folder-list"]
                        del artdata["art-data"][artist]["folder-list"]
                artdata["artist_store"]["all-folder-artists"] = []
            if triggered:
                jsonFile = open("artdata.json", "w+")
                jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                jsonFile.close()
