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

import psycopg2
import psycopg2.extras
import datetime

from errite.psql.sqlManager import grab_sql
from errite.da.datools import localDetermineNewDeviation
from errite.da.catchup import idlistHasId, ifAllNewDeviations, ifAllNewDeviationsListOnly
import errite.da.daParser as dp

def syncListeners(conn, task_cursor, source_cursor, deviant_secret, deviant_id):
    """
        Method ran grab SQL queries from sqlManager.

        :param conn: The database connection.
        :type conn: conn
        :param task_cursor: The cursor that will do task related SQL queries
        :type task_cursor: cursor
        :param source_cursor: The cursor that will do task related SQL queries
        :type source_cursor: cursor

        """
    change_sql = """ UPDATE deviantcord.deviation_listeners
                     SET dc_uuid = data.dcuuid, last_update = data.last_update, 
                    last_ids = data.last_ids::text[] FROM (VALUES %s) AS data(dcuuid, last_update, last_ids, artist, folderid, serverid, channelid)
                     WHERE deviantcord.deviation_listeners.artist = data.artist AND deviantcord.deviation_listeners.folderid = data.folderid
                     AND deviantcord.deviation_listeners.serverid = data.serverid AND deviantcord.deviation_listeners.channelid = data.channelid"""
    change_all_sql = """ UPDATE deviantcord.deviation_listeners
                         SET dc_uuid = data.dcuuid, last_update = data.last_update, 
                        last_ids = data.last_ids::text[] FROM (VALUES %s) AS data(dcuuid, last_update, last_ids, artist,serverid, channelid, mature)
                         WHERE deviantcord.deviation_listeners.artist = data.artist AND
                         deviantcord.deviation_listeners.serverid = data.serverid AND deviantcord.deviation_listeners.channelid = data.channelid
                         AND deviantcord.deviation_listeners.mature = data.mature 
                         AND deviantcord.deviation_listeners.foldertype = 'all-folder'"""
    change_hybrid_sql = """ UPDATE deviantcord.deviation_listeners
                         SET dc_uuid = data.dcuuid, last_update = data.last_update, 
                        last_ids = data.last_ids::text[], last_hybrids = data.last_hybrids::text[] 
                        FROM (VALUES %s) AS data(dcuuid, last_update, last_ids, last_hybrids, artist, folderid, serverid,
                        channelid)
                         WHERE deviantcord.deviation_listeners.artist = data.artist AND deviantcord.deviation_listeners.folderid = data.folderid
                         AND deviantcord.deviation_listeners.serverid = data.serverid AND deviantcord.deviation_listeners.channelid = data.channelid"""
    change_hybrid_only_sql = """ UPDATE deviantcord.deviation_listeners
                             SET dc_uuid = data.dcuuid, last_update = data.last_update, last_hybrids = data.last_hybrids::text[] 
                            FROM (VALUES %s) AS data(dcuuid, last_update, last_hybrids, artist, folderid, serverid, channelid)
                             WHERE deviantcord.deviation_listeners.artist = data.artist AND deviantcord.deviation_listeners.folderid = data.folderid
                             AND deviantcord.deviation_listeners.serverid = data.serverid AND deviantcord.deviation_listeners.channelid = data.channelid"""
    insert_notification_sql = """INSERT INTO deviantcord.deviation_notifications(channelid, artist, foldername, deviation_link, img_url, pp_url, id, inverse, notif_creation, mature_only)
                 VALUES %s """
    source_get_sql = """ SELECT * from deviantcord.deviation_data where artist = %s AND folderid = %s 
    AND inverse_folder = %s AND hybrid = %s"""
    source_get_all_sql = """SELECT * from deviantcord.deviation_data_all where artist = %s AND mature = %s"""
    task_get_sql = "select * from deviantcord.deviation_listeners where disabled = false"
    deviantlogger = logging.getLogger("deviantcog")
    task_cursor.execute(task_get_sql)
    obt = task_cursor.fetchall()

    for data in obt:
        timestr = datetime.datetime.now()
        all_folder_commits = []
        hybrid_commits = []
        normal_commits = []
        discord_commits = []
        hybrid_only_commits = []
        serverid: float = data[0]
        artist = data[1]
        folderid = data[2]
        foldertype = data[3]
        dc_uuid = data[4]
        channel_id = data[7]
        foldername = data[12]
        inverse = data[11]
        hybrid = data[10]
        last_update = data[8]
        last_ids = data[13]
        last_hybrids = data[14]
        mature = data[15]
        deviantlogger.info(
            "Adding source for artist " + artist + " in folder " + foldername + " using flags hybrid: " + str(hybrid)
            + " inverse: " + str(inverse) + " mature " + str(mature))
        print("Checking " + artist + " at folder " + foldername)
        if foldertype == "regular":
            print("Getting information...")
            source_cursor.execute(source_get_sql, (artist, folderid, inverse, hybrid))

            obt_token = dp.getToken(deviant_secret, deviant_id)
            obtained_source = source_cursor.fetchmany(1)
            obt_artist = obtained_source[0][0]
            obt_foldername = obtained_source[0][1]
            obt_folderid = obtained_source[0][2]
            obt_inverted = obtained_source[0][4]
            obt_offset = obtained_source[0][16]
            obt_dcuuid = obtained_source[0][4]
            obt_img_urls = obtained_source[0][7]
            obt_last_urls = obtained_source[0][12]
            obt_last_ids = obtained_source[0][13]
            obt_hybrid_ids = obtained_source[0][14]
            obt_hybrid_urls = obtained_source[0][17]
            obt_hybrid_img_urls = obtained_source[0][18]
            if len(last_ids) == 0:
                obt_latest_id = None
            else:
                obt_latest_id = last_ids[0]
            obt_pp = obtained_source[0][8]
            deviantlogger.info("Comparing DC UUID " + str(dc_uuid) + " from obt_dcuuid " + str(obt_dcuuid))
            print("DC UUID: " + dc_uuid)
            print("vs ")
            print(obt_dcuuid)
            if not dc_uuid == obt_dcuuid:
                if hybrid:
                    print("Entered hybrid")
                    new_deviation_count = localDetermineNewDeviation(obt_last_ids, last_ids, inverse)
                    new_hybrid_count = localDetermineNewDeviation(obt_hybrid_ids, last_hybrids, inverse)
                    if new_deviation_count == 0 and new_hybrid_count == 0:
                        deviantlogger.info("Executing Update only")
                        print("Execute Update only")
                    elif new_deviation_count > 0 and new_hybrid_count > 0:
                        hybrid_commits.append(
                            (obt_dcuuid, timestr, obt_last_ids, obt_hybrid_ids, artist, folderid, serverid, channel_id))
                    # If there are only deviations and not hybrid deviations
                    elif new_hybrid_count == 0 and new_deviation_count > 0:
                        normal_commits.append(
                            (obt_dcuuid, timestr, obt_last_ids, artist, folderid, serverid, channel_id))
                    elif new_hybrid_count > 0 and new_deviation_count == 0:
                        hybrid_only_commits.append(
                            (obt_dcuuid, timestr, obt_hybrid_ids, artist, folderid, serverid, channel_id))
                    # Dumping new notifications to notification_table
                    if not new_deviation_count == 0:
                        if inverse:
                            temp_index = 0
                            passes = 0
                            while not passes == new_deviation_count:
                                dump_tstr = datetime.datetime.now()
                                discord_commits.append(
                                    (channel_id, artist, foldername, obt_last_urls[temp_index],
                                     obt_img_urls[temp_index], obt_pp, inverse, dump_tstr, mature))
                                temp_index = temp_index + 1
                                passes = passes + 1
                        if not inverse:
                            temp_index = (len(obt_last_urls) - new_deviation_count) - 1
                            passes = (len(obt_last_urls) - new_deviation_count) - 1
                            while not passes == (len(obt_last_urls) - 1):
                                dump_tstr = datetime.datetime.now()
                                discord_commits.append(
                                    (channel_id, artist, foldername, obt_last_urls[temp_index],
                                     obt_img_urls[temp_index], obt_pp, inverse, dump_tstr, mature))

                                temp_index = temp_index + 1
                                passes = passes + 1
                    # Dumping new Hybrid Notifications
                    if not new_hybrid_count == 0:
                        if inverse:
                            temp_index = 0
                            passes = 0
                            sort_inverse = False
                            while not passes == new_hybrid_count:
                                dump_tstr = datetime.datetime.now()
                                discord_commits.append(
                                    (channel_id, artist, foldername, obt_hybrid_urls[temp_index],
                                     obt_hybrid_img_urls[temp_index], obt_pp, sort_inverse, dump_tstr, mature))
                                temp_index = temp_index + 1
                                passes = passes + 1
                        if not inverse:
                            temp_index = (len(obt_hybrid_ids) - new_hybrid_count) - 1
                            passes = (len(obt_hybrid_ids) - new_hybrid_count) - 1
                            sort_inverse = True
                            while not passes == (len(obt_hybrid_ids) - 1):
                                dump_tstr = datetime.datetime.now()
                                discord_commits.append(
                                    (channel_id, artist, foldername, obt_hybrid_urls[temp_index],
                                     obt_hybrid_img_urls[temp_index], obt_pp, sort_inverse, dump_tstr, mature))
                                temp_index = temp_index + 1
                                passes = passes + 1
                                # NOTE: MAYBE Change this to use values instead?
                if not hybrid:
                    print("Entered not hybrid")
                    deviantlogger.info("Entered not hybrid")
                    new_deviation_count = localDetermineNewDeviation(obt_last_ids, last_ids, inverse)
                    print("New Deviation Count: ", new_deviation_count)
                    deviantlogger.info("New Deviation count " + str(new_deviation_count))
                    deviantlogger.info("Checking if catch-up is needed")
                    didCatchup = False
                    if new_deviation_count == 10:
                        if not obt_latest_id == None:
                            if inverse:
                                # This will make sure that the normal way that deviations are added to DiscordCommits are
                                # not triggered again. Since catchup will add the necessary deviations to DiscordCommits
                                didCatchup = True
                                found_deviation = False
                                offset = 0
                                obt_token = dp.getToken(deviant_secret, deviant_id)
                                data_resources = {}
                                data_resources["ids"] = []
                                data_resources["urls"] = []
                                data_resources["img-urls"] = []
                                while not found_deviation:
                                    folder_response = dp.getGalleryFolderArrayResponse(artist, mature, folderid,
                                                                                       obt_token, offset)
                                    try:
                                        if not folder_response["has_more"] and len(folder_response["results"]) == 0:
                                            data_resources["ids"] = []
                                            didCatchup = False
                                            break
                                    except Exception as ex:
                                        print("Fuck some shit happened")
                                    gotId = idlistHasId(last_ids[0], folder_response)
                                    found_deviation = gotId
                                    if not found_deviation:
                                        catchup_index = 0
                                        for entry in folder_response["results"]:
                                            if entry["deviationid"] == last_ids[0]:
                                                break
                                            else:
                                                try:
                                                    check_var = entry["excerpt"]
                                                except KeyError:
                                                    data_resources["ids"].append(entry["deviationid"])
                                                    data_resources["urls"].append(entry["url"])
                                                    try:
                                                        data_resources["img-urls"].append(entry["content"]["src"])
                                                    except KeyError:
                                                        print("Trying other formats")
                                                        try:
                                                            data_resources["img-urls"].append(entry["flash"][
                                                                                                  "src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                        except KeyError:
                                                            try:
                                                                data_resources["img-urls"].append(entry["videos"][0][
                                                                                                      "src"] + str("DEVIANTCORDENDINGUSENONPREVIEW"))
                                                            except KeyError:
                                                                try:
                                                                    data_resources["img-urls"].append(
                                                                        entry["thumbs"]["src"])

                                                                except:
                                                                    data_resources["img-urls"].append(
                                                                        "IGNORETHISDEVIATION")
                                        offset = offset + 10
                                max_hits = len(data_resources["ids"])
                                hits = 0
                                catchup_finished = False
                                if not len(data_resources["ids"]) == 0:
                                    if not max_hits == 0:
                                        while not hits == max_hits:
                                            dump_tstr = datetime.datetime.now()
                                            discord_commits.append(
                                                (channel_id, artist, foldername, data_resources["urls"][hits],
                                                 data_resources["img-urls"][hits], obt_pp, inverse, dump_tstr, mature))
                                            hits = hits + 1
                            elif not inverse:
                                abort = False
                                didCatchup = True
                                found_deviation = False
                                data_resources = {}
                                data_resources["ids"] = []
                                data_resources["urls"] = []
                                data_resources["img-urls"] = []
                                found_deviation = False
                                offset = obt_offset
                                while not found_deviation:

                                    folder_response = dp.getGalleryFolderArrayResponse(obt_artist, mature, obt_folderid,
                                                                                       obt_token, offset)
                                    if not folder_response["has_more"] and len(folder_response["results"]) == 0:
                                        data_resources["ids"] = []
                                        abort = True
                                        didCatchup = False
                                        break
                                    gotId = idlistHasId(obt_latest_id, folder_response)
                                    found_deviation = gotId
                                    index = len(folder_response["results"])
                                    if not found_deviation:
                                        while not index == 0:
                                            index = index - 1
                                            try:
                                                check_var = folder_response["results"][index]["excerpt"]
                                            except KeyError:
                                                data_resources["ids"].append(
                                                    folder_response["results"][index]["deviationid"])
                                                data_resources["urls"].append(folder_response["results"][index]["url"])
                                                try:
                                                    data_resources["img-urls"].append(folder_response["results"][index]["content"]["src"])
                                                except KeyError:
                                                    print("Trying other formats")
                                                    try:
                                                        data_resources["img-urls"].append(
                                                            folder_response["results"][index]["flash"]["src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                    except KeyError:
                                                        try:
                                                            data_resources["img-urls"].append(folder_response["results"][index]["videos"][
                                                                                                  "src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                        except KeyError:
                                                            try:
                                                                data_resources["img-urls"].append(
                                                                    folder_response["results"][index]["thumbs"]["src"])

                                                            except:
                                                                data_resources["img-urls"].append("IGNORETHISDEVIATION")
                                        offset = offset - 10
                                        print("Diag point")
                                print("Adding last deviations in response")
                                reachedEnd = False
                                current_index = len(folder_response["results"])
                                if not abort:
                                    while not reachedEnd:
                                        index = index - 1
                                        if obt_latest_id == folder_response["results"][index]["deviationid"]:
                                            break
                                        else:
                                            try:
                                                check_var = folder_response["results"][index]["excerpt"]
                                            except KeyError:
                                                data_resources["ids"].append(folder_response["results"][index]["deviationid"])
                                                data_resources["urls"].append(folder_response["results"][index]["url"])
                                                try:
                                                    data_resources["img-urls"].append(folder_response["results"][index]["content"]["src"])
                                                except KeyError:
                                                    print("Trying other formats")
                                                    try:
                                                        data_resources["img-urls"].append(
                                                            folder_response["results"][index]["flash"]["src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                    except KeyError:
                                                        try:
                                                            data_resources["img-urls"].append(folder_response["results"][index]["videos"][
                                                                                                  "src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                        except KeyError:
                                                            try:
                                                                data_resources["img-urls"].append(
                                                                    folder_response["results"][index]["thumbs"]["src"])

                                                            except:
                                                                data_resources["img-urls"].append("IGNORETHISDEVIATION")
                                    print("End of offset " + str(offset))
                                    max_hits = len(data_resources["ids"])
                                    hits = len(data_resources["ids"])
                                    catchup_finished = False
                                    while not hits == 0:
                                        hits = hits - 1
                                        dump_tstr = datetime.datetime.now()
                                        discord_commits.append(
                                            (channel_id, artist, foldername, data_resources["urls"][hits],
                                             data_resources["img-urls"][hits], obt_pp, inverse, dump_tstr, mature))
                    elif ifAllNewDeviationsListOnly(obt_last_ids, last_ids):
                        if not obt_latest_id == None:
                            if inverse:
                                # This will make sure that the normal way that deviations are added to DiscordCommits are
                                # not triggered again. Since catchup will add the necessary deviations to DiscordCommits
                                didCatchup = True
                                found_deviation = False
                                offset = 0
                                obt_token = dp.getToken(deviant_secret, deviant_id)
                                data_resources = {}
                                data_resources["ids"] = []
                                data_resources["urls"] = []
                                data_resources["img-urls"] = []
                                while not found_deviation:
                                    folder_response = dp.getGalleryFolderArrayResponse(artist, mature, folderid,
                                                                                       obt_token, offset)
                                    if not folder_response["has_more"] and len(folder_response["results"]) == 0:
                                        data_resources["ids"] = []
                                        didCatchup = False
                                        break
                                    gotId = idlistHasId(last_ids[0], folder_response)
                                    found_deviation = gotId
                                    if not found_deviation:
                                        catchup_index = 0
                                        for entry in folder_response["results"]:
                                            if entry["deviationid"] == last_ids[0]:
                                                break
                                            else:
                                                try:
                                                    check_var = entry["excerpt"]
                                                except KeyError:
                                                    data_resources["ids"].append(entry["deviationid"])
                                                    data_resources["urls"].append(entry["url"])
                                                    try:
                                                        data_resources["img-urls"].append(entry["content"]["src"])
                                                    except KeyError:
                                                        print("Trying other formats")
                                                        try:
                                                            data_resources["img-urls"].append(entry["flash"][
                                                                                                  "src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                        except KeyError:
                                                            try:
                                                                data_resources["img-urls"].append(entry["videos"][0][
                                                                                                      "src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                            except KeyError:
                                                                try:
                                                                    data_resources["img-urls"].append(
                                                                        entry["thumbs"]["src"])

                                                                except:
                                                                    data_resources["img-urls"].append(
                                                                        "IGNORETHISDEVIATION")
                                        offset = offset + 10
                                max_hits = len(data_resources["ids"])
                                hits = 0
                                catchup_finished = False
                                if not len(data_resources["ids"]) == 0:
                                    while not hits == max_hits:
                                        dump_tstr = datetime.datetime.now()
                                        discord_commits.append(
                                            (channel_id, artist, foldername, data_resources["urls"][hits],
                                             data_resources["img-urls"][hits], obt_pp, inverse, dump_tstr, mature))
                                        hits = hits + 1
                            elif not inverse:
                                didCatchup = True
                                found_deviation = False
                                abort = False
                                data_resources = {}
                                data_resources["ids"] = []
                                data_resources["urls"] = []
                                data_resources["img-urls"] = []
                                found_deviation = False
                                offset = obt_offset
                                while not found_deviation:
                                    if offset < 0:
                                        print("Debug Breakpoint")
                                    folder_response = dp.getGalleryFolderArrayResponse(obt_artist, mature, obt_folderid,
                                                                                       obt_token, offset)
                                    if not folder_response["has_more"] and len(folder_response["results"]) == 0:
                                        data_resources["ids"] = []
                                        didCatchup = False
                                        abort = True
                                        break
                                    gotId = idlistHasId(obt_latest_id, folder_response)
                                    found_deviation = gotId
                                    index = len(folder_response["results"])
                                    if not found_deviation:
                                        while not index == 0:
                                            index = index - 1
                                            try:
                                                check_var = folder_response["results"][index]["excerpt"]
                                            except KeyError:
                                                data_resources["ids"].append(
                                                    folder_response["results"][index]["deviationid"])
                                                data_resources["urls"].append(folder_response["results"][index]["url"])
                                                try:
                                                    data_resources["img-urls"].append(folder_response["results"][index]["content"]["src"])
                                                except KeyError:
                                                    print("Trying other formats")
                                                    try:
                                                        data_resources["img-urls"].append(
                                                            folder_response["results"][index]["flash"]["src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                    except KeyError:
                                                        try:
                                                            data_resources["img-urls"].append(folder_response["results"][index]["videos"][
                                                                                                  "src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                        except KeyError:
                                                            try:
                                                                data_resources["img-urls"].append(
                                                                    folder_response["results"][index]["thumbs"]["src"])

                                                            except:
                                                                data_resources["img-urls"].append("IGNORETHISDEVIATION")
                                        offset = offset - 10
                                        print("Diag point")
                                print("Adding last deviations in response")
                                reachedEnd = False
                                current_index = len(folder_response["results"])
                                if not abort:
                                    while not reachedEnd:
                                        index = index - 1
                                        if obt_latest_id == folder_response["results"][index]["deviationid"]:
                                            break
                                        else:
                                            try:
                                                check_var = folder_response["results"][index]["excerpt"]
                                            except KeyError:
                                                data_resources["ids"].append(folder_response["results"][index]["deviationid"])
                                                data_resources["urls"].append(folder_response["results"][index]["url"])
                                                try:
                                                    data_resources["img-urls"].append(folder_response["results"][index]["content"]["src"])
                                                except KeyError:
                                                    print("Trying other formats")
                                                    try:
                                                        data_resources["img-urls"].append(
                                                            folder_response["results"][index]["flash"]["src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                    except KeyError:
                                                        try:
                                                            data_resources["img-urls"].append(folder_response["results"][index]["videos"][
                                                                                                  "src"] + " DEVIANTCORDENDINGUSENONPREVIEW")
                                                        except KeyError:
                                                            try:
                                                                data_resources["img-urls"].append(
                                                                    folder_response["results"][index]["thumbs"]["src"])

                                                            except:
                                                                data_resources["img-urls"].append("IGNORETHISDEVIATION")
                                    print("End of offset " + str(offset))
                                    max_hits = len(data_resources["ids"])
                                    hits = len(data_resources["ids"])
                                    catchup_finished = False
                                    while not hits == 0:
                                        hits = hits - 1
                                        dump_tstr = datetime.datetime.now()
                                        discord_commits.append(
                                            (channel_id, artist, foldername, data_resources["urls"][hits],
                                             data_resources["img-urls"][hits], obt_pp, inverse, dump_tstr, mature))
                    normal_commits.append((obt_dcuuid, timestr, obt_last_ids, artist, folderid, serverid, channel_id))
                    deviantlogger.info("Commiting Transaction to DB")
                    conn.commit()
                    deviantlogger.info("Transaction committed")
                    if inverse:
                        if not didCatchup:
                            temp_index = 0
                            passes = 0
                            while not passes == new_deviation_count:
                                dump_tstr = datetime.datetime.now()
                                discord_commits.append(
                                    (channel_id, artist, foldername, obt_last_urls[temp_index],
                                     obt_img_urls[temp_index], obt_pp, inverse, dump_tstr, mature))
                                temp_index = temp_index + 1
                                passes = passes + 1

                    elif not inverse:
                        if not didCatchup:
                            temp_index = (len(obt_last_urls) - new_deviation_count) - 1
                            passes = (len(obt_last_urls) - new_deviation_count) - 1
                            while not passes == (len(obt_last_urls) - 1):
                                dump_tstr = datetime.datetime.now()
                                discord_commits.append(
                                    (channel_id, artist, foldername, obt_last_urls[temp_index],
                                     obt_img_urls[temp_index], obt_pp, inverse, dump_tstr, mature))
                                temp_index = temp_index + 1
                                passes = passes + 1

                temp_cursor = conn.cursor()
                deviantlogger.info("Normal Commits: " + str(len(normal_commits)))
                deviantlogger.info("Discord Commits: " + str(len(discord_commits)))
                deviantlogger.info("Hybrid Commits " + str(len(hybrid_commits)))
                deviantlogger.info("Hybrid Only Commits " + str(len(hybrid_only_commits)))
                print("Normal ", len(normal_commits))
                print("Discord_commits ", len(discord_commits))
                print("Hybrid Commits ", len(hybrid_commits))
                print("Hybrid Only ", len(hybrid_only_commits))
                if not len(normal_commits) == 0:
                    psycopg2.extras.execute_values(temp_cursor, change_sql, normal_commits)
                if not len(hybrid_commits) == 0:
                    psycopg2.extras.execute_values(temp_cursor, change_hybrid_sql, hybrid_commits)
                if not len(hybrid_only_commits) == 0:
                    psycopg2.extras.execute_values(temp_cursor, change_hybrid_only_sql, hybrid_only_commits)
                if not len(discord_commits) == 0:
                    psycopg2.extras.execute_values(temp_cursor, insert_notification_sql, discord_commits,
                                                   "(%s, %s, %s, %s, %s, %s, default, %s, %s, %s)")
                deviantlogger.info("Committing transactions to DB")
                conn.commit()
                deviantlogger.info("Transactions committed.")
                temp_cursor.close()
        if foldertype == "all-folder":
            source_cursor.execute(source_get_all_sql, (artist, mature))
            obtained_source = source_cursor.fetchmany(1)
            obt_dcuuid = obtained_source[0][1]
            obt_img_urls = obtained_source[0][4]
            obt_last_urls = obtained_source[0][9]
            obt_last_ids = obtained_source[0][10]
            obt_pp = obtained_source[0][5]
            if not dc_uuid == obt_dcuuid:
                # All Folders can only be inverse! Thus why we dont grab the Inverse variable
                new_deviation_count = localDetermineNewDeviation(obt_last_ids, last_ids, True)
                # TODO: Make the check update when no deviations are found. This is not detrimental to launch
                if new_deviation_count > 0:
                    all_folder_commits.append((obt_dcuuid, timestr, obt_last_ids, artist, serverid, channel_id, mature))
                    temp_index = 0
                    passes = 0
                    while not passes == new_deviation_count:
                        dump_tstr = datetime.datetime.now()
                        discord_commits.append(
                            (
                                channel_id, artist, foldername, obt_last_urls[temp_index], obt_img_urls[temp_index],
                                obt_pp,
                                True, dump_tstr, mature))
                        temp_index = temp_index + 1
                        passes = passes + 1
                temp_cursor = conn.cursor()
                deviantlogger.info("AllFolder Commit Length " + str(len(all_folder_commits)))
                deviantlogger.info("AllFolder Discord Commits " + str(len(discord_commits)))
                if not len(all_folder_commits) == 0:
                    psycopg2.extras.execute_values(temp_cursor, change_all_sql, all_folder_commits)
                if not len(discord_commits) == 0:
                    psycopg2.extras.execute_values(temp_cursor, insert_notification_sql, discord_commits,
                                                   "(%s, %s, %s, %s, %s, %s, default, %s, %s, %s)")
                deviantlogger.info("Committing Transactions to DB")
                conn.commit()
                deviantlogger.info("Transactions committed successfully")
                temp_cursor.close()


def addalltask(serverid: int, channelid: int, artistname, mature, conn, shard_id):
    source_sql = grab_sql("grab_all_source_import")
    task_cursor = conn.cursor()
    task_cursor.execute(source_sql, (artistname, mature))
    obt_result = task_cursor.fetchone()
    dcuuid = obt_result[1]
    last_ids = obt_result[10]
    sql = grab_sql("new_task")
    timestr = datetime.datetime.now()
    deviantlogger = logging.getLogger("deviantcog")
    deviantlogger.info("Adding alltask for artist " + artistname
                       + " for guild " + str(serverid) + " in channel" + str(channelid) + " in mature " + str(mature))
    task_cursor.execute(sql,
                        (serverid, artistname, "none", "all-folder", dcuuid, False, [], channelid, timestr, timestr,
                         None, True, "All Folder", last_ids, None, mature, shard_id))
    deviantlogger.info("Committing transaction to database")
    conn.commit()
    deviantlogger.info("Transactions committed")


def addtask(serverid: int, channelid: int, artistname, foldername, folderid, inverse, hybrid, mature, conn, shard_id):
    source_sql = grab_sql("grab_source_import")
    task_cursor = conn.cursor()
    task_cursor.execute(source_sql, (folderid, inverse, hybrid, mature))
    obt_result = task_cursor.fetchone()
    dcuuid = obt_result[4]
    last_ids = obt_result[13]
    last_hybrid_ids = obt_result[14]
    sql = grab_sql("new_task")
    timestr = datetime.datetime.now()
    deviantlogger = logging.getLogger("deviantcog")
    deviantlogger.info(
        "Adding task for artist " + artistname + " in folder " + foldername + " using flags hybrid: " + str(hybrid)
        + " inverse: " + str(inverse) + " mature " + str(mature) + " for guild " + str(serverid) + " in channelid " +
        str(channelid))
    task_cursor.execute(sql, (serverid, artistname, folderid, "regular", dcuuid, False, [], channelid, timestr, timestr,
                              hybrid, inverse, foldername, last_ids, last_hybrid_ids, mature, shard_id))
    deviantlogger.info("Committing transaction to database")
    conn.commit()
    deviantlogger.info("Transactions committed")




