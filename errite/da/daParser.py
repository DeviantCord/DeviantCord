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
    with open("artdata.json", "r") as jsonFile:
        # artdata = json.loads(jsonFile)
            # print("Offset:", offset)
            # print("Before: ")
            # print("BEFORE FAILURE: ", offset)
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
                            artdata["art-data"][artist.lower()][folder]["artist-folder-id"] = uuid["folderid"]
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
                data = getGalleryFolderArrayResponse(artist.lower() ,bool,folder,accesstoken,providedoffset)
                # print(data)
                tmp = data["has_more"]
                # print(tmp)
                if tmp == True:
                    for uuid in data['results']:
                        # print (uuid["deviationid"])
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()][foldername]["offset-value"] = data["next_offset"]
                        artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])
                        # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    for uuid in data['results']:
                        artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])

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
        jsonFile.close()
        if inverted == True:
            invertOffset = 0
            while invertOffset <= 20:
                data = getGalleryFolderArrayResponse(artist.lower(), bool, folder, accesstoken, invertOffset)
                # print(data);
                tmp = data["has_more"]
                if tmp == True:
                    logger.info("For loop started for getGalleryFolder")
                    for uuid in data['results']:
                        # print(uuid["deviationid"])
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()][foldername]["processed-uuids"], uuid["deviationid"], artist.lower(),
                                                            foldername) == False):
                            logger.info("True Inverse: , UUID " + uuid["deviationid"] + "passed")
                            newurls.append(uuid["url"])
                            artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])

                        if data["next_offset"] is not None:
                            invertOffset = data["next_offset"]

                        # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    logger.info("getGalleryFolder: False entered")
                    for uuid in data['results']:
                        logger.debug("UUID: " + str(uuid["deviationid"]))
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()][foldername]["processed-uuids"], uuid["deviationid"], artist.lower(),
                                                            foldername) == False):
                            logger.info("False Inverse: , UUID " + uuid["deviationid"] + "passed")
                            newurls.append(uuid["url"])
                            artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])

                        if data["next_offset"] is not None:
                            invertOffset = data["next_offset"]
                    break
            jsonFile = open("artdata.json", "w+")
            jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
            jsonFile.close()
            return newurls;
                        # print (uuid.get("deviationid"))


        if inverted == False:
            # Begins Hybrid Check
            if artdata["art-data"][artist.lower()][foldername]["hybrid"]:
                invertOffset = 0
                while invertOffset <= 20:
                    data = getGalleryFolderArrayResponse(artist.lower(), bool, folder, accesstoken, invertOffset)
                    # print(data);
                    tmp = data["has_more"]
                    if tmp == True:
                        logger.info("For loop started for getGalleryFolder")
                        for uuid in data['results']:
                            # print(uuid["deviationid"])
                            if (findDuplicateElementArray(artdata["art-data"][artist.lower()][foldername]["processed-uuids"], uuid["deviationid"], artist.lower(),
                                                                foldername) == False):
                                logger.info("True Hybrid: , UUID " + uuid["deviationid"] + "passed")
                                hybridurls.append(uuid["url"])
                                artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(
                                    uuid["deviationid"])

                            if data["next_offset"] is not None:
                                invertOffset = data["next_offset"]

                            # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                    if tmp == False:
                        logger.info("getGalleryFolder: False entered")
                        for uuid in data['results']:
                            logger.debug("UUID: " + str(uuid["deviationid"]))
                            if (findDuplicateElementArray(artdata["art-data"][artist.lower()][foldername]["processed-uuids"], uuid["deviationid"], artist.lower(),
                                                                foldername) == False):
                                logger.info("False Hybrid : , UUID " + uuid["deviationid"] + "passed")
                                hybridurls.append(uuid["url"])
                                artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(
                                    uuid["deviationid"])
                            if data["next_offset"] is not None:
                                invertOffset = data["next_offset"]
                        break

            providedoffset = artdata["art-data"][artist.lower()][foldername]["offset-value"]
            while finished == False:
                logger.debug("GetGalleryFolder: Before moving to method: " + str(providedoffset))
                data = getGalleryFolderArrayResponse(artist.lower(), bool, folder, accesstoken, providedoffset)
                # print(data);
                tmp = data["has_more"]
                if tmp == True:
                    logger.info("For loop started, inverted false(NOT VARIABLE)")
                    for uuid in data['results']:
                        # print(uuid["deviationid"])
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()][foldername]["processed-uuids"], uuid["deviationid"], artist.lower(),
                                                            foldername) == False):
                            logger.info("Final True NonInverse: , UUID " + uuid["deviationid"] + "passed")
                            newurls.append(uuid["url"])
                            artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])

                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()][foldername]["offset-value"] = data["next_offset"]

                        # artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    logger.info("getGallery: False entered")
                    for uuid in data['results']:
                        # print("UUID: " + uuid["deviationid"])
                        if (findDuplicateElementArray(artdata["art-data"][artist.lower()][foldername]["processed-uuids"], uuid["deviationid"], artist.lower(),
                                                            foldername) == False):
                            logger.info("Final False NonInverse: , UUID " + uuid["deviationid"] + "passed")
                            newurls.append(uuid["url"])
                            artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()][foldername]["offset-value"] = data["next_offset"]
                        # print (uuid.get("deviationid"))
                    if len(hybridurls) == 0:
                        jsonFile = open("artdata.json", "w+")
                        jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                        jsonFile.close()
                        return newurls
                    for url in newurls:
                        finalurls.append(url)
                    currentlength = len(hybridurls)
                    while currentlength >= 1:
                        finalurls.append(hybridurls[currentlength - 1])
                        currentlength = currentlength - 1
                    jsonFile = open("artdata.json", "w+")
                    jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                    jsonFile.close()
                    return finalurls

def getGalleryFolderOLD(artist, bool, folder, accesstoken,foldername):
    finished = False;
    print("Starting check of " + artist + " gallery")
    with open("artdata.json", "r") as jsonFile:
        artdata = json.load(jsonFile)
        newurls = []
        jsonFile.close()
        providedoffset = artdata["art-data"][artist.lower()][foldername]["offset-value"]
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
                            artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])

                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()][foldername]["offset-value"] = data["next_offset"]

                        #artdata[artist.lower()]["processed-uuids"].append(uuid['results']['folderid'])4

                if tmp == False:
                    print("False entered")
                    for uuid in data['results']:
                        print("UUID: " + uuid["deviationid"])
                        if (findDuplicateJsonElementGallery("artdata.json", uuid["deviationid"], artist,foldername) == False):
                            print("No duplicates found")
                            newurls.append(uuid["url"])
                            artdata["art-data"][artist.lower()][foldername]["processed-uuids"].append(uuid["deviationid"])
                        if (findDuplicateJsonElementGallery("artdata.json", uuid["deviationid"], artist,foldername) == True):
                            print("Triggered");
                        if data["next_offset"] is not None:
                            providedoffset = data["next_offset"]
                            artdata["art-data"][artist.lower()][foldername]["offset-value"] = data["next_offset"]
                        # print (uuid.get("deviationid"))
                    jsonFile = open("artdata.json", "w+")
                    jsonFile.write(json.dumps(artdata, indent=4, sort_keys=True))
                    jsonFile.close()
                    return newurls;

