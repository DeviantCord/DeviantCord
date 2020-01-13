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
import psycopg2
import uuid
import urllib3
import urllib
import datetime
import sys, traceback
import errite.da.daParser as dp
from errite.tools.mis import gatherGalleryFolderResources,checkHybridResources, enumerateAllID, fileExists
from errite.deviantcord.porterTools import determineInverseIDAge, determineNonInverseDeviations
from errite.psql.dataValidation import checkDeviationTask
print("DeviantCord Json to PSQL Importer")
print("v1.6.0")
print("Developed by Errite Games LLC")
dbFilePresent = False
configFilePresent = False
artDataPresent = False
if fileExists("artdata.json"):
    artDataPresent = True
if fileExists("config.json"):
    configFilePresent = True
if fileExists("db.json"):
    dbFilePresent = True
if artDataPresent and configFilePresent and dbFilePresent:
    with open("client.json") as senJson:
        senData = json.load(senJson)
        senJson.close()
        print("Authenticating with DeviantArt")
        clientToken = dp.getToken(senData["da-secret"], senData["da-client-id"])
        print("WARNING: THIS WILL PORT everything in the artdata json file to the PSQL server. Are you sure you want to proceed?")
        user_input = input("Type yes or no\n")
        if user_input.lower() == "yes":
            print("Opening artdata.json and porting to PGSQL server")
            with open("artdata.json") as adataJson:
                artdata = json.load(adataJson)
            with open("config.json") as configJson:
                configdata = json.load(configJson)
            with open("db.json") as dbJson:
                dbConfigData = json.load(dbJson)
            serverid = configdata["guildid"]
            try:
                connect_str = "dbname='" + dbConfigData["database-name"] + "' user='" + dbConfigData["database-username"]\
                              + "'host='" + dbConfigData["database-host"] + "' " + \
                              "password='" + dbConfigData["database-password"] + "'"

                conn = psycopg2.connect(connect_str)
                cursor = conn.cursor()
                for artistname in artdata["artist_store"]["used-artists"]:
                    print(artistname)
                    for usedfolder in artdata["art-data"][artistname]["folders"]["folder-list"]:
                        use_defined_var = None
                        task_ids = None
                        ni_deviation_analysis = None
                        deviation_analysis = None
                        gathered_hybrid = None
                        all_hybrids = None
                        all_hybrid_url = None
                        all_hybrid_img_url = None
                        mockid_needed = False
                        source_sql = """INSERT INTO deviantcord.deviation_data(artist, folder_name, folderid,
                         inverse_folder, dc_uuid, last_update, last_check, latest_img_urls, response, latest_deviation_url,
                         latest_pp_url, mature, last_urls, last_ids, last_hybrid_ids, hybrid, given_offset, hybrid_urls, 
                          hybrid_img_urls)
                                     VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); """
                        print("Importing artist " + artistname + " for folder " + usedfolder + " to queue")
                        folderid = artdata["art-data"][artistname]["folders"][usedfolder]["artist-folder-id"]
                        offset = artdata["art-data"][artistname]["folders"][usedfolder]["offset-value"]
                        folder_type = "regular"
                        use_defined_var = False
                        task_ids = []
                        ping_role = False
                        roles = []
                        channel_id = artdata["art-data"][artistname]["folders"][usedfolder]["discord-channel-id"]
                        inverse = artdata["art-data"][artistname]["folders"][usedfolder]["inverted-folder"]
                        hybrid = artdata["art-data"][artistname]["folders"][usedfolder]["hybrid"]
                        dcuuid = str(uuid.uuid1())
                        print("Grabbing folder information from DA...")
                        emptyfolder = False
                        if inverse:
                            dartdata = dp.getGalleryFolderArrayResponse(artistname, True, folderid, clientToken, 0)
                        if not inverse:
                            dartdata = dp.getGalleryFolderArrayResponse(artistname, True, folderid, clientToken, offset)
                        gathered_resources = gatherGalleryFolderResources(dartdata)
                        if len(dartdata["results"]) == 0:
                            print("Designated folder does not have any deviations, grabbing Profile Picture...")
                            try:
                                group_pass1 = dp.daHasDeviations(artistname, clientToken)
                                userinfo = dp.userInfoResponse(artistname, clientToken, True)
                                pp_picture = userinfo["user"]["usericon"]
                                emptyfolder = True
                            except urllib.error.HTTPError as err:
                                if err.code == 400:
                                    print("This is from a group, setting dummy profile picture")
                                    pp_picture = "none"
                                emptyfolder = True
                        processed_id_len = len(artdata["art-data"][artistname]["folders"][usedfolder]["processed-uuids"])
                        if processed_id_len == 0:
                            pp_picture = dartdata["results"][0]["author"]["usericon"]
                            print("Error! The test ID is not present. No ID's have been processed...")
                        if emptyfolder:
                            timestr = str(datetime.datetime.now())
                            if hybrid:
                                print(
                                    "NOTE: Hybrid for " + artistname + " for folder " + usedfolder + "has been turned off")
                                print(
                                    "This is due to changes with Hybrid in DeviantCord 2 with folders that have less then 20 "
                                    "deviations")
                                hybrid = False
                            cursor.execute(source_sql, (artistname, usedfolder, folderid, inverse, dcuuid, timestr, timestr,
                                                        gathered_resources["img-urls"], json.dumps(dartdata),
                                                        "none", pp_picture, True,
                                                        gathered_resources["deviation-urls"],
                                                        gathered_resources["deviation-ids"], None, hybrid, offset, None, None))
                            conn.commit()
                        elif dartdata["results"][0]["deviationid"] == \
                                artdata["art-data"][artistname]["folders"][usedfolder]["processed-uuids"][1] and inverse:
                            pp_picture = dartdata["results"][0]["author"]["usericon"]
                            if hybrid:
                                temp_store = dp.getGalleryFolderArrayResponse(artistname, True, folderid, clientToken,
                                                                              offset)
                                gathered_hybrid = checkHybridResources(temp_store,
                                                                       artdata["art-data"][artistname]["folders"][
                                                                           usedfolder]["processed-uuids"])
                                print("Found " + gathered_hybrid["new-hybrids"] + " new hybrid deviations. Excluding these"
                                                                                  " so that they are posted on next startup")
                                if gathered_hybrid["new-hybrids"] > 0:
                                    mockid_needed = True
                                    all_hybrids = gathered_hybrid["seen-hybrids"]
                                    all_hybrid_url = gathered_hybrid["seen-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["seen-hybrid-img-urls"]
                                else:
                                    all_hybrids = gathered_hybrid["all-hybrids"]
                                    all_hybrid_url = gathered_hybrid["all-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["all-hybrid-img-urls"]

                            timestr = str(datetime.datetime.now())
                            cursor.execute(source_sql, (artistname, usedfolder, folderid, inverse, dcuuid, timestr,
                                                        timestr, gathered_resources["img-urls"], json.dumps(dartdata),
                                                        gathered_resources["deviation-urls"][0], pp_picture, True,
                                                        gathered_resources["deviation-urls"],
                                                        gathered_resources["deviation-ids"],
                                                        all_hybrids, hybrid, offset, all_hybrid_url, all_hybrid_img_url))
                            conn.commit()
                        elif dartdata["results"][0]["deviationid"] == \
                                artdata["art-data"][artistname]["folders"][usedfolder]["processed-uuids"][processed_id_len - 1] and inverse:
                            pp_picture = dartdata["results"][0]["author"]["usericon"]
                            if hybrid:
                                temp_store = dp.getGalleryFolderArrayResponse(artistname, True, folderid, clientToken,
                                                                              offset)
                                gathered_hybrid = checkHybridResources(temp_store,
                                                                       artdata["art-data"][artistname]["folders"][
                                                                           usedfolder]["processed-uuids"])
                                print("Found " + gathered_hybrid["new-hybrids"] + " new hybrid deviations. Excluding these"
                                                                                  " so that they are posted on next startup")
                                if gathered_hybrid["new-hybrids"] > 0:
                                    mockid_needed = True
                                    all_hybrids = gathered_hybrid["seen-hybrids"]
                                    all_hybrid_url = gathered_hybrid["seen-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["seen-hybrid-img-urls"]


                                else:
                                    all_hybrids = gathered_hybrid["all-hybrids"]
                                    all_hybrid_url = gathered_hybrid["all-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["all-hybrid-img-urls"]

                            timestr = str(datetime.datetime.now())
                            cursor.execute(source_sql, (artistname, usedfolder, folderid, inverse, dcuuid, timestr,
                                                        timestr, gathered_resources["img-urls"], json.dumps(dartdata),
                                                        gathered_resources["deviation-urls"][0], pp_picture, True,
                                                        gathered_resources["deviation-urls"],
                                                        gathered_resources["deviation-ids"],
                                                        all_hybrids, hybrid, offset, all_hybrid_url, all_hybrid_img_url))
                            conn.commit()
                        elif dartdata["results"][0]["deviationid"] == \
                                artdata["art-data"][artistname]["folders"][usedfolder]["processed-uuids"][
                                    processed_id_len - 1] and not inverse:
                            pp_picture = dartdata["results"][0]["author"]["usericon"]
                            if hybrid:
                                temp_store = dp.getGalleryFolderArrayResponse(artistname, True, folderid, clientToken,
                                                                              0)
                                gathered_hybrid = checkHybridResources(temp_store,
                                                                       artdata["art-data"][artistname]["folders"][
                                                                           usedfolder]["processed-uuids"])
                                print("Found " + str(
                                    gathered_hybrid["new-hybrids"]) + " new hybrid deviations. Excluding these"
                                                                      " so that they are posted on next startup")
                                if gathered_hybrid["new-hybrids"] > 0:
                                    mockid_needed = True
                                    all_hybrids = gathered_hybrid["seen-hybrids"]
                                    all_hybrid_url = gathered_hybrid["seen-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["seen-hybrid-img-urls"]
                                else:
                                    all_hybrids = gathered_hybrid["all-hybrids"]
                                    all_hybrid_url = gathered_hybrid["all-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["all-hybrid-img-urls"]
                            timestr = str(datetime.datetime.now())
                            cursor.execute(source_sql, (artistname, usedfolder, folderid, inverse, dcuuid, timestr, timestr,
                                                        gathered_resources["img-urls"], json.dumps(dartdata),
                                                        gathered_resources["deviation-urls"][0], pp_picture, True,
                                                        gathered_resources["deviation-urls"],
                                                        gathered_resources["deviation-ids"],
                                                        all_hybrids, hybrid, offset, all_hybrid_url, all_hybrid_img_url))
                            conn.commit()
                        else:
                            if inverse:
                                deviation_analysis = determineInverseIDAge(artdata["art-data"][artistname]["folders"][usedfolder]["processed-uuids"],
                                                                           gathered_resources["deviation-ids"], inverse)
                                if deviation_analysis["outdated"]:
                                    if deviation_analysis["action"] == "use-da":
                                        task_ids = gathered_resources["deviation-ids"]
                                        use_defined_var = True
                                elif deviation_analysis["action"] == "use-da":
                                    use_defined_var = True
                                    task_ids = gathered_resources["deviation-ids"]
                                elif deviation_analysis["action"] == "use-obt-list":
                                    use_defined_var = True
                                    task_ids = deviation_analysis["obt_list"]
                            print("The current artdata is not up to date. Marking source and task with different dc_uuid")
                            mockid_needed = True
                            pp_picture = dartdata["results"][0]["author"]["usericon"]
                            if not inverse and not hybrid:
                                #Non Inverse Deviation Analysis
                                ni_deviation_analysis = determineNonInverseDeviations(artdata["art-data"][artistname]["folders"][usedfolder]["processed-uuids"],
                                                                                      gathered_resources["deviation-ids"])
                                if ni_deviation_analysis["action"] == "use-da":
                                    use_defined_var = True
                                    task_ids = gathered_resources["deviation-ids"]
                                elif ni_deviation_analysis["action"] == "use-obt-list":
                                    use_defined_var = True
                                    task_ids = ni_deviation_analysis["obt_list"]
                            if hybrid:
                                if inverse:
                                    temp_store = dp.getGalleryFolderArrayResponse(artistname, True, folderid, clientToken,
                                                                                  offset)
                                elif not inverse:
                                    temp_store = dp.getGalleryFolderArrayResponse(artistname, True, folderid, clientToken,
                                                                                  0)
                                gathered_hybrid = checkHybridResources(temp_store,
                                                                       artdata["art-data"][artistname]["folders"][
                                                                           usedfolder]["processed-uuids"])
                                print("Found " + str(
                                    gathered_hybrid["new-hybrids"]) + " new hybrid deviations. Excluding these"
                                                                      " so that they are posted on next startup")
                                if gathered_hybrid["new-hybrids"] > 0:
                                    mockid_needed = True
                                    all_hybrids = gathered_hybrid["seen-hybrids"]
                                    all_hybrid_url = gathered_hybrid["seen-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["seen-hybrid-img-urls"]
                                else:
                                    all_hybrids = gathered_hybrid["all-hybrids"]
                                    all_hybrid_url = gathered_hybrid["all-hybrid-urls"]
                                    all_hybrid_img_url = gathered_hybrid["all-hybrid-img-urls"]
                            timestr = str(datetime.datetime.now())
                            if gathered_hybrid is None:
                                cursor.execute(source_sql, (artistname, usedfolder, folderid, inverse, dcuuid, timestr, timestr,
                                                            gathered_resources["img-urls"], json.dumps(dartdata),
                                                            gathered_resources["deviation-urls"][0], pp_picture, True,
                                                            gathered_resources["deviation-urls"],
                                                            gathered_resources["deviation-ids"],
                                                            None, hybrid, offset, None, None))
                            else:
                                cursor.execute(source_sql,
                                               (artistname, usedfolder, folderid, inverse, dcuuid, timestr, timestr,
                                                gathered_resources["img-urls"], json.dumps(dartdata),
                                                gathered_resources["deviation-urls"][0], pp_picture, True,
                                                gathered_resources["deviation-urls"],
                                                gathered_resources["deviation-ids"],
                                                gathered_hybrid["all-hybrids"], hybrid, offset, all_hybrid_url, all_hybrid_img_url))
                            conn.commit()
                        test_query = "select * from deviantcord.deviation_data;"
                        # create a psycopg2 cursor that can execute queries
                        cursor = conn.cursor()
                        # create a new table with a single column called "name"
                        # insert = "INSERT INTO deviantcord.de values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                        cursor.execute(test_query)
                        if mockid_needed:
                            dcuuid = str(uuid.uuid1())
                        record = cursor.fetchall()
                        timestr = str(datetime.datetime.now())
                        print("ARTIST NAME: " + artistname)
                        sql = """INSERT INTO deviantcord.deviation_listeners(serverid, artist,folderid, foldertype, dc_uuid, ping_role, roles, channelid, created, last_update, hybrid, inverse, foldername, last_ids, last_hybrids, mature)
                                     VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s); """
                        print(sql)
                        if use_defined_var:
                            cursor.execute(sql, (
                                serverid, artistname, folderid, folder_type, dcuuid, ping_role, roles, channel_id, timestr,
                                timestr,
                                hybrid, inverse, usedfolder, task_ids, all_hybrids, True))
                        elif not use_defined_var:
                            cursor.execute(sql, (
                            serverid, artistname, folderid, folder_type, dcuuid, ping_role, roles, channel_id, timestr, timestr,
                            hybrid, inverse, usedfolder, gathered_resources["deviation-ids"], all_hybrids, True))
                        print("Successfully added to queue.")
                print("Committing queue")
                conn.commit()  # <--- makes sure the change is shown in the database

                print("Now importing all-artists")
                source_all_sql = """INSERT INTO deviantcord.deviation_data_all(artist,dc_uuid, last_update, last_check, latest_img_urls,
                    latest_pp_url, latest_deviation_url, response,mature, last_urls, last_ids )
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s); """
                listener_sql = """INSERT INTO deviantcord.deviation_listeners(serverid, artist,folderid, foldertype, dc_uuid, ping_role, roles, channelid, created, last_update, hybrid, inverse, foldername, last_ids, last_hybrids)
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s); """
                folderid = "none"
                hybrid = False
                inverse = False
                usedfolder = "All Folder"
                for artistname in artdata["artist_store"]["all-folder-artists"]:
                    mockid_needed = False
                    dcuuid = str(uuid.uuid1())
                    dartdata = dp.getAllFolderArrayResponse(artistname, True, clientToken, 0)
                    timestr = str(datetime.datetime.now())
                    pp_picture = dartdata["results"][0]["author"]["usericon"]
                    gathered_all = gatherGalleryFolderResources(dartdata)
                    img_urls = gathered_all["img-urls"]
                    deviation_urls = gathered_all["deviation-urls"]
                    latest_deviation = deviation_urls[0]
                    channel_id = artdata["art-data"][artistname]["all-folder"]["discord-channel-id"]
                    response = json.dumps(dartdata)
                    folder_type = "all-folder"
                    ping_role = False
                    roles = []
                    mature = True
                    deviation_ids = gathered_all["deviation-ids"]
                    gathered_import = enumerateAllID(artdata["art-data"][artistname]["all-folder"]["uuid_storage"])
                    if not gathered_all["deviation-ids"][0] == gathered_import[0]:
                        mockid_needed = True
                    print("UUID: " + dcuuid)
                    cursor.execute(source_all_sql, (artistname, dcuuid, timestr, timestr, img_urls,
                                                    pp_picture, latest_deviation, response, mature, deviation_urls,
                                                    deviation_ids))
                    cursor.execute(sql, (
                        serverid, artistname, folderid, folder_type, dcuuid, ping_role, roles, channel_id, timestr, timestr,
                        hybrid,
                        inverse, usedfolder, deviation_ids, [], True,))
                conn.commit()
                # rows = cursor.fetchall()
                # print(rows)
                cursor.close()
                conn.close()
            except psycopg2.OperationalError as operr:
                print("DeviantCord Importer was unable to connect to the database server using IP ")
                print("Please check your db.json file to make sure the information is correct")
            except Exception as e:
                print("Uh oh, an exception has occured!")
                print(e)
                traceback.print_exc(file=sys.stdout)
        else:
            print("Goodbye")
            quit()
else:
    print("Required json files for import are missing. Please make sure you have the following json files:"
          "\n artdata.json, config.json, db.json")