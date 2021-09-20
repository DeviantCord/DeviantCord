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
from sentry_sdk import configure_scope, set_context, set_extra, capture_exception
import psycopg2
import psycopg2.extras
import time
import json
import uuid
import datetime
import errite.da.daParser as dp
from errite.da.datools import determineNewDeviations
from errite.tools.mis import gatherGalleryFolderResources, createIDURLList
from errite.psql.sqlManager import grab_sql
def updateSources(cursor, con, data, clientToken):
    check_sql = """ UPDATE deviantcord.deviation_data
                 SET last_check = data.last_check FROM (VALUES %s) AS data(last_check, artist, folderid)
                 WHERE deviantcord.deviation_data.artist = data.artist AND deviantcord.deviation_data.folderid = data.folderid"""
    change_sql = """ UPDATE deviantcord.deviation_data
                 SET dc_uuid = data.dcuuid, last_update = data.last_update, last_check = data.last_check, 
                 latest_img_urls = data.latest_img_url::text[], latest_pp_url = data.latest_pp_url::text,
                 latest_deviation_url = data.latest_deviation_url,  response = data.response, last_urls = data.last_urls::text[],
                  last_ids = data.last_ids::text[], given_offset = data.given_offset FROM (VALUES %s) AS data(dcuuid, last_update, last_check, latest_img_url, latest_pp_url, latest_deviation_url,
                             response, last_urls, last_ids, given_offset, artist, folderid, inverse_folder, hybrid, mature)
                 WHERE deviantcord.deviation_data.artist = data.artist AND deviantcord.deviation_data.folderid = data.folderid AND
                 deviantcord.deviation_data.inverse_folder = data.inverse_folder AND deviantcord.deviation_data.hybrid = data.hybrid 
                 AND deviantcord.deviation_data.mature = data.mature"""
    #USED BY hybridCommits
    hybrid_change_sql = """ UPDATE deviantcord.deviation_data
                 SET dc_uuid = data.dcuuid, last_update = data.last_update, last_check = data.last_check, 
                 latest_img_urls = data.latest_img_url::text[], latest_pp_url = data.latest_pp_url::text,
                 latest_deviation_url = data.latest_deviation_url,  response = data.response, last_urls = data.last_urls::text[],
                  last_ids = data.last_ids::text[], given_offset = data.given_offset, last_hybrid_ids = data.last_hybrid_ids::text[],
                  hybrid_urls = data.hybrid_urls::text[], hybrid_img_urls = data.hybrid_img_urls::text[]
                   FROM (VALUES %s) AS data(dcuuid, last_update, last_check, latest_img_url, latest_pp_url, latest_deviation_url,
                             response, last_urls, last_ids, given_offset,last_hybrid_ids, hybrid_urls, hybrid_img_urls, artist, folderid,
                             hybrid, inverse_folder, mature)
                 WHERE deviantcord.deviation_data.artist = data.artist AND deviantcord.deviation_data.folderid = data.folderid
                 AND deviantcord.deviation_data.hybrid = data.hybrid AND deviantcord.deviation_data.inverse_folder = data.inverse_folder
                 AND deviantcord.deviation_data.mature = data.mature"""
    #Used by hybrid only
    hybrid_only_sql = """ UPDATE deviantcord.deviation_data
                     SET last_check = data.last_check, last_hybrid_ids = data.last_hybrid_ids::text[], 
                     hybrid_urls = data.hybrid_urls::text[], hybrid_img_urls = data.hybrid_img_urls::text[] FROM (VALUES %s) 
                     AS data(last_check, last_hybrid_ids, hybrid_urls, hybrid_img_urls, artist, folderid, hybrid, inverse_folder, mature)
                     WHERE deviantcord.deviation_data.artist = data.artist 
                     AND deviantcord.deviation_data.folderid = data.folderid AND deviantcord.deviation_data.hybrid = data.hybrid
                     AND deviantcord.deviation_data.inverse_folder = data.inverse_folder AND deviantcord.deviation_data.mature = data.mature"""
    test = []
    checks = []
    hybridCommits = []
    hybridOnly = []
    gathered_hybrids = None
    deviantlogger = logging.getLogger("deviantcog")
    try:
        for row in data:

            hybridResponse = None
            check_only = False
            normal_update = True
            has_hybrid = False
            foldername = row[1]
            artistname = row[0]
            print("Trying artist " + artistname + " in folder " + foldername)
            folderid = row[2]
            inverse = row[3]
            dc_uuid = row[4]
            last_updated = row[5]
            last_check = row[6]
            latest_img_url = row[7]
            latest_pp_url = row[8]
            latest_deviation_url = row[9]
            response = row[10]
            mature = row[11]
            last_urls = row[12]
            last_ids = row[13]
            last_hybrids = row[14]
            hybrid = row[15]
            offset = row[16]
            timestr = datetime.datetime.now()
            didCatchup = False

            deviantlogger.info("Normal Checking artist: " + artistname + " in folder " + foldername + " inverse: " +
                               str(inverse) +
                               " hybrid: " + str(hybrid) + " mature " + str(mature) + " offset " + str(offset))
            if inverse:
                da_response = dp.getGalleryFolderArrayResponse(artistname, mature, folderid, clientToken, 0)
                if len(da_response["results"]) == 0:
                    latest_pp_url = "none"
                else:
                    latest_pp_url = da_response["results"][0]["author"]["usericon"]
                if hybrid:
                    hybridResponse = dp.getGalleryFolderArrayResponse(artistname, mature, folderid, clientToken, offset)
                    if len(hybridResponse["results"]) == 0:
                        has_hybrid = True
                        gathered_hybrids = createIDURLList(hybridResponse)
                        normal_update = False
                    elif len(last_hybrids) == 0 and not len(hybridResponse["results"]) == 0:
                        has_hybrid = True
                        gathered_hybrids = createIDURLList(hybridResponse)
                        normal_update = False
                    elif not hybridResponse["results"][0]["deviationid"] == last_hybrids[0]:
                        has_hybrid = True
                        gathered_hybrids = createIDURLList(hybridResponse)
                        normal_update = False

            elif not inverse:
                da_response = dp.getGalleryFolderArrayResponse(artistname, mature, folderid, clientToken, offset)
                if da_response["has_more"]:
                    didCatchup = True
                    end_offolder = False
                    offset = da_response["next_offset"]
                    while not end_offolder:
                        da_response = dp.getGalleryFolderArrayResponse(artistname, mature, folderid, clientToken,
                                                                       offset)
                        if da_response["has_more"]:
                            offset = offset + 10
                        else:
                            end_offolder = True

                result_len = len(da_response["results"])
                if result_len == 0:
                    latest_pp_url = "none"
                else:
                    latest_pp_url = da_response["results"][result_len - 1]["author"]["usericon"]
                if hybrid:
                    hybridResponse = dp.getGalleryFolderArrayResponse(artistname, mature, folderid, clientToken, 0)
                    if len(last_hybrids) == 0 and not len(hybridResponse["results"]) == 0:
                        has_hybrid = True
                        gathered_hybrids = createIDURLList(hybridResponse)
                        normal_update = False
                    elif not hybridResponse["results"][0]["deviationid"] == last_hybrids[0]:
                        has_hybrid = True
                        gathered_hybrids = createIDURLList(hybridResponse)
                        normal_update = False
            if len(da_response["results"]) == 0:
                gathered_resources = gatherGalleryFolderResources(da_response)
                if len(last_ids) == 0:
                    continue
                try:
                    offset_increase = determineNewDeviations(da_response["results"], last_ids)
                    offset = offset + offset_increase
                except Exception as ex:
                    print(ex)
                dcuuid = str(uuid.uuid1())
                last_ids = gathered_resources["deviation-ids"]
                last_urls = gathered_resources["deviation-urls"]
                if len(gathered_resources["deviation-urls"]) == 0:
                    latest_deviation_url = "none"
                else:
                    latest_deviation_url = gathered_resources["deviation-urls"][0]
                last_updated = timestr
                last_check = timestr
                latest_img_url: str = gathered_resources["img-urls"]
                response = json.dumps(da_response)
            elif len(last_ids) == 0 and not len(da_response["results"]) == 0:
                gathered_resources = gatherGalleryFolderResources(da_response)
                if not didCatchup:
                    offset_increase = determineNewDeviations(da_response["results"], last_ids)
                    offset = offset + offset_increase
                dcuuid = str(uuid.uuid1())
                last_ids = gathered_resources["deviation-ids"]
                last_urls = gathered_resources["deviation-urls"]
                if len(gathered_resources["deviation-urls"]) == 0:
                    latest_deviation_url = []
                else:
                    latest_deviation_url = gathered_resources["deviation-urls"][0]
                last_updated = timestr
                last_check = timestr
                latest_img_url: str = gathered_resources["img-urls"]
                response = json.dumps(da_response)
            elif not da_response["results"][0]["deviationid"] == last_ids[0]:
                gathered_resources = gatherGalleryFolderResources(da_response)
                if not didCatchup:
                    offset_increase = determineNewDeviations(da_response["results"], last_ids)
                    offset = offset + offset_increase
                dcuuid = str(uuid.uuid1())
                last_ids = gathered_resources["deviation-ids"]
                last_urls = gathered_resources["deviation-urls"]
                if len(gathered_resources["deviation-urls"]) == 0:
                    latest_deviation_url = []
                else:
                    latest_deviation_url = gathered_resources["deviation-urls"][0]
                last_updated = timestr
                last_check = timestr
                latest_img_url:str = gathered_resources["img-urls"]
                response = json.dumps(da_response)
            else:
                last_check = timestr
                check_only = True
                normal_update = False
            if latest_pp_url is None:
                latest_pp_url = "none"
            if normal_update:
                test.append((dcuuid, last_updated, last_check, latest_img_url, latest_pp_url, latest_deviation_url,
                             response, last_urls, last_ids, offset, artistname, folderid, inverse, hybrid, mature))
                print(test[0])
            if check_only:
                checks.append((timestr, artistname, folderid))
            if has_hybrid:
                if check_only:
                    hybridOnly.append((timestr, gathered_hybrids["ids"], gathered_hybrids["urls"],
                                       gathered_hybrids["img-urls"], artistname,  folderid, hybrid, inverse, mature))
                else:
                    hybridCommits.append((dcuuid, last_updated, last_check, latest_img_url, latest_pp_url, latest_deviation_url,
                             response, last_urls, last_ids, offset, gathered_hybrids["ids"], gathered_hybrids["urls"],
                                          gathered_hybrids["img-urls"], artistname, folderid, hybrid, inverse, mature))
        if not len(checks) == 0:
            psycopg2.extras.execute_values(cursor, check_sql, checks)
        print("checks " + str(len(checks)))
        if not len(test) == 0:
            psycopg2.extras.execute_values(cursor, change_sql, test)
        if not len(hybridOnly) == 0:
            psycopg2.extras.execute_values(cursor, hybrid_only_sql, hybridOnly)
        if not len(hybridCommits) == 0:
            #HERE
            psycopg2.extras.execute_values(cursor, hybrid_change_sql, hybridCommits)
                #cursor.execute(
                 #   change_sql(dcuuid, last_updated, last_check, latest_img_url, latest_pp_url, latest_deviation_url,
                  #             response, last_urls, last_ids, offset, artistname, folderid))
                #con.commit()
    except Exception as e:
        print("Uh oh, an exception has occured")
        with configure_scope() as scope:
            capture_exception(e)
        print(e)

def updateallfolders(cursor, con, data, clientToken):
    check_sql = """ UPDATE deviantcord.deviation_data_all
                 SET last_check = data.last_check FROM (VALUES %s) AS data(last_check, artist, mature)
                 WHERE deviantcord.deviation_data_all.artist = data.artist AND deviantcord.deviation_data_all.mature = data.mature"""
    change_sql = """ UPDATE deviantcord.deviation_data_all
                 SET dc_uuid = data.dcuuid, last_update = data.last_update, last_check = data.last_check, 
                 latest_img_urls = data.latest_img_url::text[], latest_pp_url = data.latest_pp_url,
                 latest_deviation_url = data.latest_deviation_url,  response = data.response, last_urls = data.last_urls::text[],
                  last_ids = data.last_ids::text[] FROM (VALUES %s) AS data(dcuuid, last_update, last_check, latest_img_url, latest_pp_url, latest_deviation_url,
                             response, last_urls, last_ids, artist, mature)
                 WHERE deviantcord.deviation_data_all.artist = data.artist AND deviantcord.deviation_data_all.mature = data.mature"""
    deviantlogger = logging.getLogger("deviantcog")
    updates = []
    checks = []
    try:
        debug_index = 0
        for row in data:
            hybridResponse = None
            check_only = False
            normal_update = True
            has_hybrid = False
            new_uuid = str(uuid.uuid1())
            artistname = row[0]
            dc_uuid = row[1]
            last_updated = row[2]
            last_check = row[3]
            latest_img_url = row[4]
            latest_pp_url = row[5]
            latest_deviation_url = row[6]
            response = row[7]
            mature = row[8]
            last_urls = row[9]
            last_ids = row[10]
            timestr = datetime.datetime.now()
            deviantlogger.info("Checking artist: " + artistname + " mature " + str(mature))
            #Its always 0 since new deviations for all folders are only posted on the top
            da_response = dp.getAllFolderArrayResponse(artistname, mature, clientToken, 0)
            gathered_allfolders = gatherGalleryFolderResources(da_response)
            if len(da_response["results"]) == 0:
                latest_pp_url = "none"
            elif len(last_ids) == 0 and len(da_response["results"]) > 0:
                if latest_pp_url is None:
                    latest_pp_url = 'none'
                else:
                    latest_pp_url = da_response["results"][0]["author"]["usericon"]
                updates.append((new_uuid, last_updated, last_check, gathered_allfolders["img-urls"], latest_pp_url, latest_deviation_url,
                             response, gathered_allfolders["deviation-urls"], gathered_allfolders["deviation-ids"], artistname, mature))
            elif len(gathered_allfolders["deviation-ids"]) == 0 or not da_response["results"][0]["deviationid"] == last_ids[0]:
                if latest_pp_url is None:
                    latest_pp_url = 'none'
                else:
                    latest_pp_url = da_response["results"][0]["author"]["usericon"]
                updates.append((new_uuid, last_updated, last_check, gathered_allfolders["img-urls"], latest_pp_url, latest_deviation_url,
                             response, gathered_allfolders["deviation-urls"], gathered_allfolders["deviation-ids"], artistname, mature))
            else:
                checks.append((last_check, artistname, mature))
            debug_index = debug_index + 1

        if not len(checks) == 0:
            psycopg2.extras.execute_values(cursor, check_sql, checks)
        if not len(updates) == 0:
            psycopg2.extras.execute_values(cursor, change_sql, updates)
        print("checks " + str(len(checks)))
        print
    except Exception as e:
        deviantlogger.exception(e)
        print("Uh oh, an exception has occured!")
        print(e)

def verifySourceExistance(artist, folder, inverse, hybrid, mature, conn):
    sql = grab_sql("verify_source_exists")
    verify_cursor = conn.cursor()
    verify_cursor.execute(sql, (artist, folder, inverse, hybrid, mature))
    obt_results = verify_cursor.fetchone()
    verify_cursor.close()
    if obt_results is None:
        return False
    else:
        return True

def verifySourceExistanceExtra(artist, folder, inverse, hybrid, mature, conn):
    information = {}
    sql = grab_sql("verify_source_exists")
    verify_cursor = conn.cursor()
    verify_cursor.execute(sql, (artist, folder, inverse, hybrid, mature))
    obt_results = verify_cursor.fetchone()
    verify_cursor.close()
    if obt_results is None:
        information["results"] = False
        return information
    else:
        information["results "] = True
        information["ids"] = obt_results[1]
        information["hybrid-ids"] = obt_results[2]
        return information

def verifySourceExistanceAll(artist,mature, conn):
    sql = grab_sql("verify_all_source_exists")
    verify_cursor = conn.cursor()
    verify_cursor.execute(sql, (artist, mature))
    obt_results = verify_cursor.fetchone()
    verify_cursor.close()
    if obt_results is None:
        return False
    else:
        return True


def addallsource(daresponse, artist, conn, mature, shard_id:int, dcuuid = str(uuid.uuid1())):
    #Since the initial checks to make sure the given artist isn't a group. We already hit the DA API once.
    # No point in hitting it again
    deviantlogger = logging.getLogger("deviantcog")
    deviantlogger.info("Adding all source for artist " + artist + " with mature flag " + str(mature))
    gathered_allfolders = gatherGalleryFolderResources(daresponse)
    sql = grab_sql("new_all_source")
    source_cursor = conn.cursor()
    timestr = str(datetime.datetime.now())
    if len(daresponse["results"]) == 0:
        pp_picture = "none"
    else:
        pp_picture = daresponse["results"][0]["author"]["usericon"]
    if len(daresponse["results"]) == 0 or len(gathered_allfolders["deviation-ids"]) == 0:
        source_cursor.execute(sql, (artist, dcuuid, timestr, timestr, gathered_allfolders["img-urls"],
                                    pp_picture, "none", json.dumps(daresponse), mature, gathered_allfolders["deviation-urls"],
                                    gathered_allfolders["deviation-ids"], shard_id))
    else:
        source_cursor.execute(sql, (artist, dcuuid, timestr, timestr, gathered_allfolders["img-urls"],
                                    pp_picture, gathered_allfolders["deviation-urls"][0], json.dumps(daresponse), mature, gathered_allfolders["deviation-urls"],
                                    gathered_allfolders["deviation-ids"], shard_id))
    deviantlogger.info("AddallSource successfully executed. Committing to DB")
    conn.commit()
    deviantlogger.info("Committed")
    source_cursor.close()


def addsource(artist, folder, folderid, inverse, hybrid, client_token, conn, mature, shard_id, dcuuid = str(uuid.uuid1())):
    source_information = {}
    gathered_hybrid = None
    source_information["normal-ids"] = None
    source_information["hybrid-ids"] = None
    new_url = None
    deviantlogger = logging.getLogger("deviantcog")
    deviantlogger.info("Adding source for artist " + artist + " in folder " + folder + " using flags hybrid: " +
                       str(hybrid) + " inverse: " + str(inverse) + " mature " + str(mature))
    if inverse == False:
        offset = 0
        current_data = {}
        hybrid_data = None
        has_more = True
        while has_more:
            current_data = dp.getGalleryFolderArrayResponse(artist, mature, folderid, client_token, offset)
            if not current_data["has_more"]:
                break;
            else:
                offset = current_data["next_offset"]

        if hybrid:
            hybrid_data = dp.getGalleryFolderArrayResponse(artist, mature, folderid, client_token, 0)
            gathered_hybrid = gatherGalleryFolderResources(hybrid_data)

        sql = grab_sql("new_source")
        gathered_resources = gatherGalleryFolderResources(current_data)
        folder_cursor = conn.cursor()
        if len(current_data["results"]) == 0:
            pp_picture = "none"
        else:
            pp_picture = current_data["results"][0]["author"]["usericon"]
        if pp_picture is None:
            pp_picture = "none"
        timestr = datetime.datetime.now()
        if len(gathered_resources["deviation-urls"]) == 0:
            new_url = None
        else:
            new_url = gathered_resources["deviation-urls"][len(gathered_resources["deviation-urls"]) - 1]
        if hybrid:
            folder_cursor.execute(sql,(artist, folder, folderid, inverse, dcuuid, timestr, timestr,
                                       gathered_resources["img-urls"], json.dumps(current_data),
                                       new_url,
                                       pp_picture, mature, gathered_resources["deviation-urls"], gathered_resources["deviation-ids"],
                                       gathered_hybrid["deviation-ids"], hybrid, offset, gathered_hybrid["deviation-urls"],
                                       gathered_hybrid["img-urls"], shard_id,))
        else:
            folder_cursor.execute(sql, (artist, folder, folderid, inverse, dcuuid, timestr, timestr,
                                        gathered_resources["img-urls"], json.dumps(current_data),
                                        new_url,pp_picture, mature, gathered_resources["deviation-urls"],
                                        gathered_resources["deviation-ids"],None, hybrid, offset, None, None, shard_id))
    elif inverse == True:
        print("Entered true")
        current_data = dp.getGalleryFolderArrayResponse(artist, mature, folderid, client_token, 0)
        if hybrid:
            has_more = True
            offset = 0
            while has_more:
                hybrid_data = dp.getGalleryFolderArrayResponse(artist, mature, folderid, client_token, offset)
                if not hybrid_data["has_more"]:
                    break;
                else:
                    offset = hybrid_data["next_offset"]

            gathered_hybrid = gatherGalleryFolderResources(hybrid_data)
        sql = grab_sql("new_source")
        gathered_resources = gatherGalleryFolderResources(current_data)
        folder_cursor = conn.cursor()
        if len(current_data["results"]) == 0:
            pp_picture = "none"
        else:
            pp_picture = current_data["results"][0]["author"]["usericon"]
        dcuuid = str(uuid.uuid1())
        timestr = datetime.datetime.now()
        if len(gathered_resources["deviation-urls"]) == 0:
            new_url = None
        else:
            new_url = gathered_resources["deviation-urls"][len(gathered_resources["deviation-urls"]) - 1]
        if hybrid:
            # HERE
            folder_cursor.execute(sql,(artist, folder, folderid, inverse, dcuuid, timestr, timestr,
                                       gathered_resources["img-urls"], json.dumps(current_data),
                                       new_url,
                                       pp_picture, mature, gathered_resources["deviation-urls"], gathered_resources["deviation-ids"],
                                       gathered_hybrid["deviation-ids"], hybrid, offset, gathered_hybrid["deviation-urls"],
                                       gathered_hybrid["img-urls"], shard_id,))
        else:
            folder_cursor.execute(sql, (artist, folder, folderid, inverse, dcuuid, timestr, timestr,
                                        gathered_resources["img-urls"], json.dumps(current_data),
                                        new_url,
                                        pp_picture, mature, gathered_resources["deviation-urls"],
                                        gathered_resources["deviation-ids"],None, hybrid, 0,None,None, shard_id))
    deviantlogger.info("Committing transactions to DB")
    conn.commit()
    deviantlogger.info("Successfully committed transactions to DB")
    folder_cursor.close()
    source_information["normal-ids"] = gathered_resources["deviation-ids"]
    if hybrid:
        source_information["hybrid-ids"] = gathered_hybrid["deviation-ids"]
    else:
        source_information["hybrid-ids"] = None
    return source_information
