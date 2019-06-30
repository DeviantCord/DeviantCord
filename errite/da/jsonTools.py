import json
import logging
def findDuplicateJsonElementGallery(file, element, artist,foldername):
    """
            Method ran to check if a Deviation UUID is already in the ArtData json file.

            :param file: UNUSED The name of the json file that would be used to compare the provided UUID with existing UUID's
            :type file: string
            :param element: The UUID we are comparing with the JSON file.
            :type element: string
            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :return: bool
    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close();
        for storeduuid in artdata["art-data"][artist.lower()][foldername]["processed-uuids"]:
            if storeduuid == element:
                # print("Compared element: " + element + "vs " + storeduuid)
                # print("Triggered Found match")
                return True;
        return False;

def findDuplicateElementArray(array, element, artist,foldername):
    """
            Method ran to check if a Deviation UUID is already in the array.

            :param array: The array that holds the current processed uuids for the particular artist
            :type array: array
            :param element: The UUID we are comparing with the JSON file.
            :type element: string
            :param artist: UNUSED TO BE REMOVED The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: May be reused: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :return: bool
    """
    # TODO Change the docstring for this method
    logger = logging.getLogger('errite.da.jsonTools')
    for stored_uuid in array:
        if stored_uuid == element:
            return True
    return False

def folderExists(artist,foldername):
    """
            Method ran to check if a folder is already in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :return: bool
    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("artdata.json", "r") as jsonFile:
        try:
            artdata = json.load(jsonFile)
            jsonFile.close()

            if artdata["art-data"][artist.lower()][foldername]["artist-folder-id"] is not None:
                return True
            else:
                return True
        except KeyError:
            #print("Folder check, revealed found that the folder is not present in ArtData.")
            return False

def artistExists(artist):
    """
            Method ran to check if a artist is already in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :return: bool
    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("artdata.json", "r") as jsonFile:
        try:
            artdata = json.load(jsonFile)
            jsonFile.close()
            if artdata["art-data"][artist.lower()] is not None:
                return True
            else:
                return True
        except KeyError:
            # print("Does not exist")
            return False


def createArtistData(artist, folderid, foldername, channelid, inverted):
    """
            Method ran to create a new artist in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param folderid: The UUID of the folder that we are adding to the ArtData json file
            :type folderid: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :param channelid: The Discord channelid that notifications will be posted to.
            :type channelid: int
            :param inverted: Whether the newest deviations are posted at the top.
    """
    logger = logging.getLogger('errite.da.jsonTools')
    newartistcontent = {}
    emptyauthor = {}
    stringarray = ['test']
    folderarray = []
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        newartistcontent['artist-folder-id'] = folderid
        # newartistcontent['artist-folder-name'] = foldername
        newartistcontent['offset-value'] = 0
        newartistcontent['inverted-folder'] = inverted
        if inverted is True:
            newartistcontent['hybrid'] = False
        if inverted is False:
            newartistcontent['hybrid'] = True
        newartistcontent['discord-channel-id'] = int(channelid)
        newartistcontent['processed-uuids'] = stringarray
        folderarray.append(foldername)
        artdata["art-data"][artist.lower()] = emptyauthor
        artdata["art-data"][artist.lower()]['folder-list'] = folderarray
        artdata["art-data"][artist.lower()][foldername] = newartistcontent
        jsonFile = open("artdata.json", "w+")
        artdata["artist_store"]["used-artists"].append(artist.lower())
        jsonFile.write(json.dumps(artdata, indent=4,sort_keys=True))
        jsonFile.close()


def createFolderData(artist, folderid, foldername, channelid, inverted):
    """
            Method ran to create a new folder to an existing artist in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param folderid: The UUID of the folder that we are adding to the ArtData json file
            :type folderid: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :param channelid: The Discord channelid that notifications will be posted to.
            :type channelid: int
            :param inverted: Whether the newest deviations are posted at the top.
    """
    logger = logging.getLogger('errite.da.jsonTools')
    newartistcontent = {}
    emptyauthor = {}
    stringarray = ['test']
    folderarray = []
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        newartistcontent['artist-folder-id'] = folderid
        newartistcontent['offset-value'] = 0
        newartistcontent['discord-channel-id'] = int(channelid)
        newartistcontent['inverted-folder'] = inverted
        if inverted is True:
            newartistcontent['hybrid'] = False
        if inverted is False:
            newartistcontent['hybrid'] = True
        newartistcontent['processed-uuids'] = stringarray
        folderarray.append(foldername)
        artdata["art-data"][artist.lower()][foldername] = newartistcontent
        jsonFile = open("artdata.json", "w+")
        artdata["art-data"][artist.lower()]["folder-list"].append(foldername)
        jsonFile.write(json.dumps(artdata, indent=4,sort_keys=True))
        jsonFile.close()


def updateDiscordChannel(artist, foldername, newchannelid):
    """
            Method ran to update a listeners discord channel id in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :param newchannelid: The Discord channelid that notifications will be posted to.
            :type newchannelid: int

    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        print("New ChannelID ", newchannelid)
        artdata["art-data"][artist.lower()][foldername]["discord-channel-id"] = int(newchannelid)
        jsonFile = open("artdata.json", "w+")
        jsonFile.write(json.dumps(artdata, indent=4,sort_keys=True))
        jsonFile.close()


def updatehybridproperty(artist, foldername, hybrid):
    """
            Method ran to update a listeners discord channel id in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :param hybrid: The value the new hybrid should be in the Json file
            :type hybrid: bool

    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        logger.info("UpdateHybrid: Updating Artdata")
        if bool(hybrid) is True:
            artdata["art-data"][artist.lower()][foldername]["hybrid"] = True
        elif bool(hybrid) is False:
            artdata["art-data"][artist.lower()][foldername]["hybrid"] = False
        logger.info("UpdateHybrid: Writing to JSON file")
        jsonFile = open("artdata.json", "w+")
        jsonFile.write(json.dumps(artdata, indent=4,sort_keys=True))
        jsonFile.close()


def updateinverseproperty(artist, foldername, inverse):
    """
            Method ran to update a listeners discord channel id in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :param inverse: The value the new inverse should be in the Json file
            :type inverse: bool

    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        print("New Inverse ", inverse)
        logger.info("UpdateInverse: Updating Artdata")
        artdata["art-data"][artist.lower()][foldername]["inverted-folder"] = bool(inverse)
        if bool(inverse) is True:
            artdata["art-data"][artist.lower()][foldername]["hybrid"] = False
        elif bool(inverse) is False:
            artdata["art-data"][artist.lower()][foldername]["hybrid"] = True
        logger.info("UpdateInverse: Writing to JSON file")
        jsonFile = open("artdata.json", "w+")
        jsonFile.write(json.dumps(artdata, indent=4,sort_keys=True))
        jsonFile.close()

def update_errite(property):
    """
            Method ran to toggle the errite property in the config.json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :param hybrid: The value the new hybrid should be in the Json file
            :type hybrid: bool

    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("config.json", "r") as jsonFile:
        configdata = json.load(jsonFile)
        jsonFile.close()
        logger.info("update_errite: Updating Config")
        if bool(property) is True:
            logger.info("update_errite: Updating value to True")
            configdata["errite"] = True
        elif bool(property) is False:
            logger.info("update_errite: Updating value to False")
            configdata["errite"] = False
        logger.info("update_errite: Writing to JSON file")
        jsonFile = open("config.json", "w+")
        jsonFile.write(json.dumps(configdata, indent=4,sort_keys=True))
        jsonFile.close()


def updatelogchannel(channelid):
    """
            Method ran to update the logchannelid handles debug logging.

            :param channelid: The roleid that will become the central role to the bot.
            :type channelid: int

    """
    logger = logging.getLogger('errite.da.jsonTools')
    with open("config.json", "r") as jsonFile:
        configdata = json.load(jsonFile)
        jsonFile.close()
        print("New ChannelID ", channelid)
        configdata["logchannelid"] = int(channelid)
        jsonFile = open("config.json", "w+")
        jsonFile.write(json.dumps(configdata, indent=4,sort_keys=True))
        jsonFile.close()

def updateRole(roleid, guildid):
    """
            Method ran to update the role that commands check for to make sure a user is authorized.

            :param roleid: The roleid that will become the central role to the bot.
            :type roleid: int

    """
    logger = logging.getLogger('errite.da.jsonTools')
    logger.info("Update Role Started")
    with open("config.json", "r") as jsonFile:
        configdata = json.load(jsonFile)
        jsonFile.close()
        logger.debug("New RoleID " + str(roleid))
        configdata["roleid"] = int(roleid)
        configdata["rolesetup-enabled"] = False
        configdata["guildid"] = int(guildid)
        jsonFile = open("config.json", "w+")
        jsonFile.write(json.dumps(configdata, indent=4,sort_keys=True))
        jsonFile.close()


def updateprefix(prefix):
    """
            Method ran to update the prefix that commands use check for to make sure a user is authorized.

            :param prefix: The new prefix that will replace the old one
            :type prefix: string

    """
    with open("config.json", "r") as jsonFile:
        configdata = json.load(jsonFile)
        jsonFile.close()
        print("New prefix ", prefix)
        configdata["prefix"] = prefix
        jsonFile = open("config.json", "w+")
        jsonFile.write(json.dumps(configdata, indent=4,sort_keys=True))
        jsonFile.close()


def delfolder(artist, folder):

    """
            Method ran to delete a folder in the ArtData json file.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param foldername: The name of the gallery folder we are working with. Used for json references
            :type foldername: string
            :return: bool
    """
    with open("artdata.json", "r") as jsonFile:
        tempartdata = json.load(jsonFile)
        jsonFile.close()
        correctartistform = artist.lower()
        if len(tempartdata["art-data"][artist.lower()]["folder-list"]) == 1:
            del tempartdata["art-data"][artist.lower()]
            for element in tempartdata["artist_store"]["used-artists"]:
                print(element)
            tempartdata["artist_store"]["used-artists"].remove(correctartistform)
        elif len(tempartdata["art-data"][artist.lower()]["folder-list"]) > 1:
            del tempartdata["art-data"][artist.lower()][folder]
            tempartdata["art-data"][artist.lower()]["folder-list"].remove(folder)
        jsonFile = open("artdata.json", "w+")
        jsonFile.write(json.dumps(tempartdata, indent=4, sort_keys=True))
        jsonFile.close()

def dumpURLListDebug(list):
    for element in list:
        print(element)
