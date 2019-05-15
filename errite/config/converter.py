import logging
import json
from errite.tools.mis import fileExists

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

            if triggered:
                jsonFile = open("artdata.json", "w+")
                jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                jsonFile.close()
