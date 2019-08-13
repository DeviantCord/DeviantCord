"""

    Copyright 2019 Errite Games LLC / ErriteEpticRikez

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
from errite.tools.mis import convertBoolString
import urllib.request, json;
import urllib.error;
import logging
from errite.da.jsonTools import findDuplicateJsonElementGallery, findDuplicateElementArray


def getToken(clientsecret, clientid):
    """
            Method ran to grab a new token from DA and return it, Login tokens on DeviantArt last for 60 minutes.

            :param clientsecret: The clientsecret associated with your app registered on DeviantArts Dev Area.
            :type clientsecret: string
            :param clientid: The clientid associated with your app registered on DeviantArts Dev Area.
            :type clientid: string
            :return: string
    """
    logger = logging.getLogger('errite.da.daparser')
    tokenRequestURL = "https://www.deviantart.com/oauth2/token?grant_type=client_credentials&client_id=" +clientid + \
                      "&client_secret=" + clientsecret
    # logger.info(tokenRequestURL)
    with urllib.request.urlopen(tokenRequestURL) as result:
        data = json.loads(result.read().decode())
        # print(data);
        tmp = data["access_token"]
        # print("Access Code: " +tmp)
        return tmp;

def checkTokenValid(token):
    """
            Method ran to check if a token is valid, Login tokens on DeviantArt last for 60 minutes.

            :param token: The artist's name that owns the folder.
            :type token: string
            :return: int (0 means valid, any other number corresponds with the DeviantArt HTTP Error Code)
            """
    logger = logging.getLogger('errite.da.daparser')
    tokenCheckURL = "https://www.deviantart.com/api/v1/oauth2/gallery/folders?access_token=" + token + \
                    "&username=zander-the-artist&calculate_size=false&ext_preload=false&limit=10&mature_content=true&offset=0"
    try:
        with urllib.request.urlopen(tokenCheckURL) as result:
            logger.info("CheckTokenValid: Token is valid")
            return 0;
    except urllib.error.HTTPError as Err:
        if Err.code == 401:
            logger.info("Token is not valid...")
            return 401;
        if Err.code == 503:
            logger.error("DA Servers are down for maintenance")
            return 503;
        if Err.code == 500:
            logger.error("DA experienced an issue")
            return 500;
        if Err.code == 429:
            logger.error("DA API is currently overloaded...")
            return 429;

def daHasDeviations(artist, accesstoken):
    """
            Method ran to check if a an artist has Deviations on DA by checking their Gallery All View.

            :param artist: The name of the artist who's deviations we are working with. This is needed for json references
            :type artist: string
            :param accesstoken: The name of the gallery folder we are working with. Used for json references
            :type accesstoken: string
            :return: bool
    """

    data = getAllFolderArrayResponse(artist.lower(), bool, accesstoken, 0)
    try:
        if len(data["results"]) == 0:
            print("No deviations")
            return False
    except KeyError:
        print("Invalid Data sent. ")
        return False
    return True


def getFolderArrayResponse(artist, bool, folder, accesstoken, offset):
    """
            Method ran to get the list of folders from an artist from deviantart's API.

            :param artist: The artist's name that owns the folder.
            :type artist: string
            :param bool: Whether mature folders will show or not.
            :type bool: bool
            :param folder: The Exact folder name to grab the UUID of
            :type folder: string
            :param accesstoken: The DA Access token to use for this query
            :type accesstoken: string
            :param offset: The offset value at which to request the gallery folder contents from. The starting value
            :type offset: int
            :return: array
    """
    finished = False;
    logger = logging.getLogger('errite.da.daparser')
    logger.info("GetFolderArrayResponse: Started")
    with open("artdata.json", "r") as jsonFile:
        # artdata = json.loads(jsonFile)
            logger.debug("GetFolderArray: Offset:" + str(offset))
            folderRequestURL = "https://www.deviantart.com/api/v1/oauth2/gallery/folders?access_token=" + accesstoken + "&username=" + artist + "&calculate_size=false&ext_preload=false&limit=10&mature_content=" + convertBoolString(
                bool) + "&offset=" + str(offset)
            # print(folderRequestURL)
            with urllib.request.urlopen(folderRequestURL) as url:
                data = json.loads(url.read().decode())
                return data;


def getAllFolderArrayResponse(artist,bool, accesstoken, offset):
    """
        Method ran to get the Gallery Folder data all view from deviantart's API.

        :param artist: The artist's name that owns the folder.
        :type artist: string
        :param bool: Whether mature folders will show or not.
        :type bool: bool
        :param accesstoken: The DA Access token to use for this query
        :type accesstoken: string
        :param offset: The offset value at which to request the gallery folder contents from. The starting value
        :type offset: int
        :return: array
        """

    folderRequestURL = "https://www.deviantart.com/api/v1/oauth2/gallery/all" + "?username=" + artist + "&access_token=" + accesstoken + "&limit=10&mature_content=" + convertBoolString(
        bool) + "&offset=" + str(offset)
    with urllib.request.urlopen(folderRequestURL) as url:
        data = json.loads(url.read().decode())
        return data;


def getGalleryFolderArrayResponse(artist, bool, folder, accesstoken, offset):
    """
        Method ran to get the Gallery Folder data from deviantart's API.

        :param artist: The artist's name that owns the folder.
        :type artist: string
        :param bool: Whether mature folders will show or not.
        :type bool: bool
        :param folder: UUID of the folder that data is being grabbed from
        :type folder: string
        :param accesstoken: The DA Access token to use for this query
        :type accesstoken: string
        :param offset: The offset value at which to request the gallery folder contents from. The starting value
        :type offset: int
        :return: array
        """
    finished = False;

    folderRequestURL = "https://www.deviantart.com/api/v1/oauth2/gallery/" + folder + "?username=" + artist + "&access_token=" + accesstoken + "&limit=10&mature_content=" + convertBoolString(
        bool) + "&offset=" + str(offset)
    # print(offset)
    with urllib.request.urlopen(folderRequestURL) as url:
        data = json.loads(url.read().decode())
        return data;


def findFolderUUID(artist, bool, folder, accesstoken):
    """
    Method ran to get the List of Folders from an artist and determine if the folder requested exists.
    If it exists then it returns the UUID
    Returns None if it does not exist.

    :param artist: The artist's name to request the folder's UUID id's from
    :type artist: string
    :param bool: Whether mature folders will show or not.
    :type bool: bool
    :param folder: The Exact folder name to grab the UUID of
    :type folder: string
    :param accesstoken: The DA Access token to use for this query
    :type accesstoken: string
    :return: array
    """
    finished = False
    providedoffset = 0
    while (finished == False):
        try:
            data = getFolderArrayResponse(artist, bool, folder, accesstoken, providedoffset)
            if data["error"] is not None:
                return "ERROR";
        except urllib.error.HTTPError:
            return"ERROR";
        except KeyError:
            tmp = data["has_more"]
            print("Error was not triggered...")

        tmp = data["has_more"]
        # print(data);

        # print(tmp)
        if tmp == True:
            for uuid in data['results']:
                # print (uuid["folderid"])
                if uuid["name"].lower() == folder.lower():
                        return uuid["folderid"];
                providedoffset = data["next_offset"]

        if tmp == False:
            for uuid in data['results']:
                if uuid["name"].lower() == folder.lower():
                        return uuid["folderid"]
            finished = True
    return "None";


def refindFolderUUID(artist, bool, folder, accesstoken):
    finished = False;
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        providedoffset = 0
        while (finished == False) :
                data = getFolderArrayResponse(artist,bool,folder,accesstoken,providedoffset)
                # print(data);
                tmp = data["has_more"]
                # print(tmp)
                if tmp == True:
                    for uuid in data['results']:
                        #print (uuid["folderid"])
                        if uuid["name"].lower() == folder.lower():
                            artdata["art-data"][artist.lower()]["folders"][folder]["artist-folder-id"] = uuid["folderid"]
                            jsonFile = open("artdata.json", "w+")
                            jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                            jsonFile.close()
                            return uuid["folderid"];
                            tmp = True;
                        providedoffset = data["next_offset"]
                        #artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    # for uuid in data['results']:
                     #    print (uuid.get("folderid"))
                    finished = True

                # print(data)


def getallFolder(artist, bool, accesstoken, inverted):
    """
    Method ran to get the all view data devations id's and populate it into the json file.
    This method is different from the getGalleryFolderFT. Designed with Slices in mind
    This method in particular is only ran on the first time/when a new folder is added.


    :param artist: The artist's name to request the folder's deviation id's from
    :type artist: string
    :param bool: Whether mature images will show or not.
    :type bool: bool
    :param accesstoken: The DA Access token to use for this query
    :type accesstoken: string
    :param inverted: If the folder is inverted or not.
    :return: array
    """
    finished = False;
    triggered = False
    logger = logging.getLogger('errite.da.daparser')
    deviant_info = {}
    deviant_info["index"] = 0
    deviant_info["da-urls"] = []
    deviant_info["photo-urls"] = []
    deviant_info["profile-pic-url"] = "none"
    deviant_info["trigger"] = False
    logger.info("getAllFolder: Opening artdata.json")
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        logger.info("getAllFolder: Closing artdata.json")
        jsonFile.close()
        providedoffset = 0
        if not inverted:
            logger.warning("getAllFolder: Inverse is not True, if the user is experiencing issues this may be why.")
            providedoffset = artdata["art-data"][artist.lower()]["all-folder"]["offset"]
        written_outset = artdata["art-data"][artist.lower()]["all-folder"]["currentindex"]
        ad_outset = artdata["art-data"][artist.lower()]["all-folder"]["currentindex"]
        if ad_outset < 10:
            logger.info("getAllFolder: ad_outset is less than 10! Skipping slicing")
            recent_uuids = artdata["art-data"][artist.lower()]["all-folder"]["uuid_storage"]
        else:
            logger.info("getAllFolder: ad_outset is greater than 10")
            # Unlike indexes outside of using slices, out of bounds are handled gracefully
            # Additionally the index number at the end indicates where it should stop and the last index
            # will not be read. THis is why we add 1
            recent_uuids = artdata["art-data"][artist.lower()]["all-folder"]["uuid_storage"][ad_outset-9:ad_outset+1]
        if inverted:
            print("getAllFolder: Inverted Before moving to method: ", providedoffset)
            logger.info("getAllFolder: Inverted Before moving to method: " + str(providedoffset))
            data = getAllFolderArrayResponse(artist.lower(), bool, accesstoken, providedoffset)
            logger.info("getAllFolder: Setting profile picture in deviant_info ")
            deviant_info["profile-pic-url"] = data["results"][0]["author"]["usericon"]
            logger.debug("getAllFolder: START ARRAY COMPARE")
            for elemental in recent_uuids:
                logger.debug("getAllFolder: Element: " + elemental)
            logger.debug("getAllFolder: VS")
            for uuid in data["results"]:
                logger.debug("getAllFolder: CHECKING " + uuid["deviationid"])
                if not findDuplicateElementArray(recent_uuids, uuid["deviationid"]):
                    artdata["art-data"][artist.lower()]["all-folder"]["uuid_storage"].append(uuid["deviationid"])
                    deviant_info["index"] = deviant_info["index"] + 1
                    deviant_info["da-urls"].append(uuid["url"])
                    deviant_info["photo-urls"].append(uuid["content"]["src"])
                    deviant_info["trigger"] = True
                    logger.info(uuid["deviationid"] + " is not in store")
                    written_outset = written_outset + 1
                    triggered = True
            if triggered:
                deviant_info["index"] = deviant_info["index"] - 1
            artdata["art-data"][artist.lower()]["all-folder"]["currentindex"] = written_outset
            artdata["art-data"][artist.lower()]["all-folder"]["offset"] = providedoffset
            logger.info("getAllFolder: Opening artdata.json for writing")
            jsonFile = open("artdata.json", "w+")
            logger.info("getAllFolder: Writing to artdata.json")
            jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
            jsonFile.close()
            logger.info("Returning DeviantInfo")
            return deviant_info
        if not inverted:
            while (finished == False) :
                    logger.warning("getAllFolder: Inverse is not True, if the user is experiencing issues this may be why.")
                    print("Before moving to method: ", providedoffset)
                    logger.info("getAllFolder: Inverted Before moving to method: " + str(providedoffset))
                    data = getAllFolderArrayResponse(artist.lower(), bool, accesstoken, providedoffset)
                    logger.info("getAllFolder: Setting profile picture in deviant_info ")
                    deviant_info["profile-pic-url"] = data["results"][0]["author"]["usericon"]
                    tmp = data["has_more"]
                    if tmp == True:
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]

                    if tmp == False:
                        for uuid in data['results']:
                            logger.debug("getAllFolder: CHECKING " + uuid["deviationid"])
                            if not findDuplicateElementArray(recent_uuids, uuid["deviationid"]):
                                triggered = True
                                written_outset = written_outset + 1
                                logger.info(uuid["deviationid"] + " is not in store")
                                artdata["art-data"][artist.lower()]["all-folder"]["uuid_storage"].append(uuid["deviationid"])
                                logger.info("GetAllFolderDeviant_Info Index is " + str(deviant_info["index"]))
                                deviant_info["index"] = deviant_info["index"] + 1
                                deviant_info["da-urls"].append(uuid["url"])
                                deviant_info["photo-urls"].append(uuid["content"]["src"])
                                deviant_info["trigger"] = True
                        if triggered:
                            logger.info("GetAllFolder: Entered triggered")
                            artdata["art-data"][artist.lower()]["all-folder"]["currentindex"] = written_outset
                            deviant_info["index"] = deviant_info["index"] - 1
                        artdata["art-data"][artist.lower()]["all-folder"]["offset"] = providedoffset
                        logger.info("getAllFolder: Opening artdata.json for writing")
                        jsonFile = open("artdata.json", "w+")
                        logger.info("getAllFolder: Writing to artdata.json")
                        jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                        jsonFile.close()
                        logger.info("Returning DeviantInfo")
                        return deviant_info

            return

def getallFolderFT(artist, bool, accesstoken, inverted):
    """
    Method ran to get the all view data devations id's and populate it into the json file.
    This method is different from the getGalleryFolderFT. Designed with Slices in mind
    This method in particular is only ran on the first time/when a new folder is added.


    :param artist: The artist's name to request the folder's deviation id's from
    :type artist: string
    :param bool: Whether mature images will show or not.
    :type bool: bool
    :param accesstoken: The DA Access token to use for this query
    :type accesstoken: string
    :param inverted: If the folder is inverted or not.
    :return: array
    """
    logger = logging.getLogger('errite.da.daparser')
    finished = False;
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        providedoffset = 0
        written_outset = 0
        if inverted:
            print("AllFolderFT: Inverse Before moving to method: ", providedoffset)
            logger.info("AllFolderFT: Inverse Before moving to method: " + str(providedoffset))
            logger.info("AllFolderFT: Getting Inverse AllFolder Response")
            data = getAllFolderArrayResponse(artist.lower(), bool, accesstoken, providedoffset)
            logger.info("AllFolderFT:Before going into writtenoutset:  " + str(written_outset))
            for uuid in data["results"]:
                logger.debug("AllFolderFT: Adding deviation id " + uuid["deviationid"] + " to uuid_storage")
                artdata["art-data"][artist.lower()]["all-folder"]["uuid_storage"].append(uuid["deviationid"])
                # artdata["art-data"][artist.lower()]["all-folder"]["uuid_storage"].append(uuid[0]['deviationid'])
                logger.info("AllFolderFT: Incrementing written_outset")
                written_outset = written_outset + 1
                print("After offset " + str(written_outset))
            logger.info("AllFolderFT: Decrementing wrriten outset")
            artdata["art-data"][artist.lower()]["all-folder"]["currentindex"] = written_outset - 1
            logger.info("Offset " + str(providedoffset))
            artdata["art-data"][artist.lower()]["all-folder"]["offset"] = providedoffset
            logger.info("AllFolderFT: Opening artdata.json")
            jsonFile = open("artdata.json", "w+")
            logger.info("AllFolderFT: Writing to artdata.json")
            jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
            logger.info("AllFolderFT: Closing artdata.json")
            jsonFile.close()
        if not inverted:
            while (finished == False) :
                    print("Before moving to method: ", providedoffset)
                    logger.info("AllFolderFT: Before moving to method: " + str(providedoffset))
                    logger.info("AllFolderFT: Getting AllFolder Response")
                    data = getAllFolderArrayResponse(artist.lower(), bool, accesstoken , providedoffset)
                    # print(data)
                    tmp = data["has_more"]
                    # print(tmp)
                    if tmp == True:
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]

                    if tmp == False:
                        for uuid in data['results']:
                            logger.info("AllFolderFT Incrementing writtenoutset to " + str(written_outset + 1))
                            written_outset = written_outset + 1
                            logger.debug("AllFolderFT: Adding deviation id " + uuid["deviationid"] + " to uuid_storage")
                            artdata["art-data"][artist.lower()]["all-folder"]["uuid_storage"].append(uuid["deviationid"])
                            # print (uuid.get("deviationid"))
                        artdata["art-data"][artist.lower()]["all-folder"]["currentindex"] = written_outset
                        artdata["art-data"][artist.lower()]["all-folder"]["offset"] = providedoffset
                        logger.info("AllFolderFT: Opening artdata.json")
                        jsonFile = open("artdata.json", "w+")
                        logger.info("AllFolderFT: Writing to artdata.json")
                        jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                        logger.info("AllFolderFT: Closing artdata.json")
                        jsonFile.close()
                        finished = True


def getGalleryFolderFT(artist, bool, folder, accesstoken,foldername):
    """
    Method ran to get the GalleryFolder data devations id's and populate it into the json file.
    This method in particular is only ran on the first time/when a new folder is added.


    :param artist: The artist's name to request the folder's deviation id's from
    :type artist: string
    :param bool: Whether mature images will show or not.
    :type bool: bool
    :param folder: The UUID associated with the folder we are grabbing deviations from.
    :type folder: string
    :param accesstoken: The DA Access token to use for this query
    :type accesstoken: string
    :param foldername: The Exact folder name in the artists gallery
    :type foldername: string
    :return: array
    """
    finished = False;
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        jsonFile.close()
        providedoffset = 0
        while (finished == False) :
                print("Before moving to method: ", providedoffset)
                data = getGalleryFolderArrayResponse(artist.lower(), bool,folder,accesstoken,providedoffset)
                # print(data)
                tmp = data["has_more"]
                # print(tmp)
                if tmp == True:
                    for uuid in data['results']:
                        # print (uuid["deviationid"])
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()]["folders"][foldername]["offset-value"] = data["next_offset"]
                        artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])
                        # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    for uuid in data['results']:
                        artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])

                        # print (uuid.get("deviationid"))
                    jsonFile = open("artdata.json", "w+")
                    jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                    jsonFile.close()
                    finished = True

                # print(data)





def getGalleryFolder(artist, bool, folder, accesstoken,foldername, inverted):
    """
    Method ran to get deviation id's of new deviations in the folder and returns the new deviation url's
    in a array.


    :param artist: The artist's name to request the folder's deviation id's from
    :type artist: string
    :param bool: Whether mature images will show or not.
    :type bool: bool
    :param folder: The UUID associated with the folder we are grabbing deviations from.
    :type folder: string
    :param accesstoken: The DA Access token to use for this query
    :type accesstoken: string
    :param foldername: The Exact folder name in the artists gallery
    :type foldername: string
    :param inverted: Whether newest deviations are at the top for this folder.
    :type inverted: bool
    :return: array
    """
    logger = logging.getLogger('errite.da.daparser')
    finished = False;
    logger.info("Starting check of " + artist.lower() + " gallery")
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        newurls = []
        hybridurls = []
        finalurls = []
        deviant_info = {}
        deviant_info["da-urls"] = []
        deviant_info["photo-url"] = []
        deviant_info["profile-pic-url"] = "test"
        jsonFile.close()
        if inverted == True:
            invertOffset = 0
            while invertOffset < 20:
                data = getGalleryFolderArrayResponse(artist.lower(), bool, folder, accesstoken, invertOffset)
                # print(data);
                tmp = data["has_more"]
                if tmp == True:
                    logger.info("For loop started for getGalleryFolder")
                    for uuid in data['results']:
                        # print(uuid["deviationid"])
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"], uuid["deviationid"]) == False):
                            logger.info("True Inverse: , UUID " + uuid["deviationid"] + "passed")
                            deviant_info["profile-pic-url"] = str(uuid["author"]["usericon"])
                            logger.debug("InverseT: Appending to array DA URL: " + str(uuid["url"]))
                            deviant_info["da-urls"].append(uuid["url"])
                            logger.debug("InverseF: Appending to Array PHOTO URL: " + str(uuid["content"]["src"]))
                            deviant_info["photo-url"].append(uuid["content"]["src"])
                            artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])

                        if data["next_offset"] is not None:
                            invertOffset = data["next_offset"]

                        # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    logger.info("getGalleryFolder: False entered")
                    for uuid in data['results']:
                        logger.debug("UUID: " + str(uuid["deviationid"]))
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"], uuid["deviationid"]) == False):
                            logger.info("False Inverse: , UUID " + uuid["deviationid"] + "passed")
                            deviant_info["profile-pic-url"] = uuid["author"]["usericon"]
                            logger.debug("InverseF: Appending to array DA URL: " + str(uuid["url"]))
                            deviant_info["da-urls"].append(uuid["url"])
                            logger.debug("InverseF: Appending to Array PHOTO URL: " + str(uuid["content"]["src"]))
                            deviant_info["photo-url"].append(uuid["content"]["src"])
                            artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])
                        if data["next_offset"] is not None:
                            invertOffset = data["next_offset"]
                    break
            jsonFile = open("artdata.json", "w+")
            jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
            jsonFile.close()
            print("Reached")
            return deviant_info;
                        # print (uuid.get("deviationid"))


        if inverted == False:
            # Begins Hybrid Check
            print("Begin Hybrid")
            if artdata["art-data"][artist.lower()]["folders"][foldername]["hybrid"]:
                invertOffset = 0
                while invertOffset < 20:
                    data = getGalleryFolderArrayResponse(artist.lower(), bool, folder, accesstoken, invertOffset)
                    # print(data);
                    tmp = data["has_more"]
                    if tmp == True:
                        logger.info("For loop started for getGalleryFolder")
                        for uuid in data['results']:
                            # print(uuid["deviationid"])
                            if (findDuplicateElementArray(artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"], uuid["deviationid"]) == False):
                                logger.info("True Hybrid: , UUID " + uuid["deviationid"] + "passed")
                                deviant_info["profile-pic-url"] = uuid["author"]["usericon"]
                                logger.debug("HybridT: Appending to Array PHOTO URL: " + str(uuid["content"]["src"]))
                                hybridurls.append(uuid["content"]["src"])
                                logger.debug("HybridT: Appending to array DA URL: " + str(uuid["url"]))
                                hybridurls.append(uuid["url"])
                                print(uuid["url"])
                                artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(
                                    uuid["deviationid"])

                            if data["next_offset"] is not None:
                                invertOffset = data["next_offset"]

                            # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                    if tmp == False:
                        logger.info("getGalleryFolder: False entered")
                        for uuid in data['results']:
                            logger.debug("UUID: " + str(uuid["deviationid"]))
                            if (findDuplicateElementArray(artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"], uuid["deviationid"]) == False):
                                logger.info("False Hybrid : , UUID " + uuid["deviationid"] + "passed")
                                logger.debug("HybridF: Appending to array DA URL: " + str(uuid["url"]))
                                hybridurls.append(uuid["url"])
                                logger.debug("HybridF: Appending to Array PHOTO URL: " + str(uuid["content"]["src"]))
                                hybridurls.append(uuid["content"]["src"])
                                deviant_info["profile-pic-url"] = uuid["author"]["usericon"]

                                artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(
                                    uuid["deviationid"])
                            if data["next_offset"] is not None:
                                invertOffset = data["next_offset"]
                        break

            providedoffset = artdata["art-data"][artist.lower()]["folders"][foldername]["offset-value"]
            while finished == False:
                logger.debug("GetGalleryFolder: Before moving to method: " + str(providedoffset))
                data = getGalleryFolderArrayResponse(artist.lower(), bool, folder, accesstoken, providedoffset)
                # print(data);
                tmp = data["has_more"]
                if tmp == True:
                    logger.info("For loop started, inverted false(NOT VARIABLE)")
                    for uuid in data['results']:
                        # print(uuid["deviationid"])
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"], uuid["deviationid"]) == False):
                            logger.info("Final True NonInverse: , UUID " + uuid["deviationid"] + "passed")
                            deviant_info["profile-pic-url"] = uuid["author"]["usericon"]
                            newurls.append(uuid["url"])
                            newurls.append(uuid["content"]["src"])
                            artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])

                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()]["folders"][foldername]["offset-value"] = data["next_offset"]

                        # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    logger.info("getGallery: False entered")
                    for uuid in data['results']:
                        # print("UUID: " + uuid["deviationid"])
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"], uuid["deviationid"]) == False):
                            logger.info("Final False NonInverse: , UUID " + uuid["deviationid"] + "passed")
                            deviant_info["profile-pic-url"] = uuid["author"]["usericon"]
                            newurls.append(uuid["url"])
                            newurls.append(uuid["content"]["src"])
                            artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()]["folders"][foldername]["offset-value"] = data["next_offset"]
                        # print (uuid.get("deviationid"))
                    if len(hybridurls) == 0:
                        logger.debug("Entered 1")
                        jsonFile = open("artdata.json", "w+")
                        jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                        jsonFile.close()
                        for url in newurls:
                            logger.debug("Checking URL " + url)
                            if url.find("wixmp.com") > -1:
                                deviant_info["photo-url"].append(url)
                            elif url.find("deviantart.net") > -1:
                                if url.find("https://img") > -1:
                                    deviant_info["photo-url"].append(url)
                            elif url.find("deviantart.com") > -1:
                                if url.find("https://img") > -1:
                                    deviant_info["photo-url"].append(url)
                                else:
                                    deviant_info["da-urls"].append(url)
                        return deviant_info

                    logger.debug("Beginning 2")
                    for url in newurls:
                        logger.debug("URL in new URL " + str(url))
                        if url.find("wixmp.com") > -1:
                            deviant_info["photo-url"].append(url)
                        elif url.find("deviantart.net") > -1:
                            if url.find("https://img") > -1:
                                deviant_info["photo-url"].append(url)
                        elif url.find("deviantart.com") > -1:
                            if url.find("https://img") > -1:
                                deviant_info["photo-url"].append(url)
                            else:
                                deviant_info["da-urls"].append(url)
                    currentlength = len(hybridurls)
                    logger.debug("Hybrid Urls Length: " + str(currentlength))
                    while currentlength >= 1:
                        logger.debug("Now starting check on URL " + str(hybridurls[currentlength - 1]))
                        print("Entered hybrid")
                        if hybridurls[currentlength - 1].find("wixmp.com") > -1:
                            print("Occured here?")
                            deviant_info["photo-url"].append(hybridurls[currentlength -1])
                        elif hybridurls[currentlength - 1].find("deviantart.net") > -1:
                            if hybridurls[currentlength - 1].find("https://img") > -1:
                                deviant_info["photo-url"].append(hybridurls[currentlength - 1])
                        elif hybridurls[currentlength - 1].find("deviantart.com") > -1:
                            if hybridurls[currentlength - 1].find("https://img") > -1:
                                deviant_info["photo-url"].append(hybridurls[currentlength - 1])
                            else:
                                deviant_info["da-urls"].append(hybridurls[currentlength -1])
                        currentlength = currentlength - 1
                    jsonFile = open("artdata.json", "w+")
                    jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                    jsonFile.close()
                    return deviant_info

def getGalleryFolderOLD(artist, bool, folder, accesstoken,foldername):
    finished = False;
    print("Starting check of " + artist + " gallery")
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        newurls = []
        jsonFile.close()
        providedoffset = artdata["art-data"][artist.lower()]["folders"][foldername]["offset-value"]
        while finished == False:
                print("Before moving to method: ", providedoffset)
                data = getGalleryFolderArrayResponse(artist,bool,folder,accesstoken,providedoffset)
                # print(data);
                tmp = data["has_more"]
                if tmp == True:
                    print("For loop started")
                    for uuid in data['results']:
                        print (uuid["deviationid"])
                        if(findDuplicateJsonElementGallery("artdata.json",uuid["deviationid"],artist,foldername) == False):
                            newurls.append(uuid["url"])
                            artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])

                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()]["folders"][foldername]["offset-value"] = data["next_offset"]

                        #artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    print("False entered")
                    for uuid in data['results']:
                        print("UUID: " + uuid["deviationid"])
                        if (findDuplicateJsonElementGallery("artdata.json", uuid["deviationid"], artist,foldername) == False):
                            print("No duplicates found")
                            newurls.append(uuid["url"])
                            artdata["art-data"][artist.lower()]["folders"][foldername]["processed-uuids"].append(uuid["deviationid"])
                        if (findDuplicateJsonElementGallery("artdata.json", uuid["deviationid"], artist,foldername) == True):
                            print("Triggered");
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()]["folders"][foldername]["offset-value"] = data["next_offset"]
                        # print (uuid.get("deviationid"))
                    jsonFile = open("artdata.json", "w+")
                    jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                    jsonFile.close()
                    return newurls;

