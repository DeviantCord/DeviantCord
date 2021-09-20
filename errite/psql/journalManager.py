import datetime
import json
import uuid

import psycopg2

from errite.psql.sqlManager import grab_sql
from errite.tools.mis import gatherJournal, createJournalInfoList
from errite.da.daParser import getJournalResponse
from errite.da.datools import determineNewJournals


def addjournalsource(daresponse, artist, conn, mature, dcuuid = str(uuid.uuid1())):
    gathered_journals = createJournalInfoList(daresponse["results"])
    write_cursor = conn.cursor()
    new_journal_sql = grab_sql("new_journal_source")
    last_title = gathered_journals["titles"][0]
    last_url = gathered_journals["journal-urls"][0]
    urls = gathered_journals["journal-urls"]
    last_ids = gathered_journals["deviation-ids"]
    thumburls = gathered_journals["thumbnails-img-urls"]
    thumbnail_ids = gathered_journals["thumbnail-ids"]
    last_excerpt = gathered_journals["excerpts"][0]
    excerpts = gathered_journals["excerpts"]
    titles = gathered_journals["titles"]
    profilepic = gathered_journals["profilepic"]
    timestr = str(datetime.datetime.now())
    write_cursor.execute(new_journal_sql,(artist, dcuuid, last_title, last_url, last_excerpt, last_ids,
                                          timestr, timestr, profilepic, json.dumps(daresponse), mature, thumburls,
                                          urls, excerpts, titles, thumbnail_ids,))
    conn.commit()
    return gathered_journals



def addjournallistener(serverid:int, channelid:int, artist, mature, conn ):
    journal_source_sql = grab_sql("grab_journal_source_dcuuid")
    obt_ids = []
    source_cursor = conn.cursor()
    source_cursor.execute(journal_source_sql,(artist, mature,))
    obt_source = source_cursor.fetchone()
    obt_dcuuid = obt_source[0]
    obt_ids = obt_source[1]
    task_cursor = conn.cursor()
    journal_listener_sql = grab_sql("new_journal_listener")
    timestr = str(datetime.datetime.now())
    task_cursor.execute(journal_listener_sql,(artist, obt_dcuuid, obt_ids, timestr, timestr, obt_source[2], mature, serverid, channelid,))

    conn.commit()
    task_cursor.close()
    source_cursor.close()




def verifySourceJournalExists(conn, artist, mature):
    journal_exists_sql = grab_sql("journal_exists")
    read_cursor = conn.cursor()
    write_cursor = conn.cursor()
    read_cursor.execute(journal_exists_sql,(artist,mature,))
    obt_journal = read_cursor.fetchone()
    if obt_journal is None:
        return False
    elif len(obt_journal) == 0:
        return False
    else:
        return True


def verifyListenerJournalExists(conn, artist, mature):
    journal_exists_sql = grab_sql("journal_listener_exists")
    read_cursor = conn.cursor()
    write_cursor = conn.cursor()
    read_cursor.execute(journal_exists_sql, (artist, mature,))
    obt_journal = read_cursor.fetchone()
    if obt_journal is None:
        return False
    elif len(obt_journal) == 0:
        return False
    else:
        return True


def updateJournals(conn, clienttoken):
    get_sources = grab_sql("grab_all_source_journals")
    read_cursor = conn.cursor()
    read_cursor.execute(get_sources)
    obt_results = read_cursor.fetchall()
    journal_change_sql = grab_sql("journal_source_change")
    journal_check_sql = grab_sql("journal_source_check")
    journalCommits = []
    journalCheck = []
    for row in obt_results:
        artist = row[0]
        dcuuid = row[1]
        latest_title = row[2]
        latest_url = row[3]
        latest_excerpt = row[4]
        last_ids = row[5]
        last_check = row[6]
        latest_update = row[7]
        latest_pp = row[8]
        response = row[9]
        mature = row[10]
        thumb_img_url = row[11]
        last_urls = row[12]
        last_excerpts = row[13]
        last_titles = row[14]
        dcuuid = str(uuid.uuid1())

        journalResponse = getJournalResponse(artist,clienttoken, False, mature)
        if not len(journalResponse["results"]) == 0:
            if not journalResponse["results"][0]["deviationid"] == last_ids[0]:
                infoList = createJournalInfoList(journalResponse["results"])
                timestr = datetime.datetime.now()

                sql = grab_sql("journal_source_change")
                journalCommits.append((dcuuid, timestr, timestr, infoList["thumbnails-img-urls"], infoList["profilepic"],
                                       infoList["journal-urls"][0],json.dumps(journalResponse), infoList["journal-urls"],
                                      infoList["deviation-ids"], infoList["titles"], infoList["thumbnail-ids"], infoList["thumbnail-ids"],
                                      infoList["excerpts"], artist, mature))
            else:
                timestr = datetime.datetime.now()
                journalCheck.append((timestr, artist))
        else:
            timestr = datetime.datetime.now()
            journalCheck.append((timestr, artist))
    temp_cursor = conn.cursor()
    if not len(journalCommits ) == 0:
        psycopg2.extras.execute_values(temp_cursor, journal_change_sql, journalCommits)
    if not len(journalCheck) == 0:
        try:
            psycopg2.extras.execute_values(temp_cursor, journal_check_sql, journalCheck)
        except Exception as ex:
            print("Exception")




def syncJournals(conn):
    changeCommits = []
    notificationCommits = []
    source_cursor = conn.cursor()
    journal_cursor = conn.cursor()
    write_cursor = conn.cursor()
    get_listeners = grab_sql("get_all_journal_listeners")
    journal_cursor.execute(get_listeners)
    obt_journals = journal_cursor.fetchall()
    for journal in obt_journals:
        artist = journal[0]
        dc_uuid = journal[1]
        last_ids = journal[2]
        last_check = journal[3]
        latest_update = journal[4]
        latest_pp = journal[5]
        mature = journal[6]
        serverid = journal[7]
        channelid = journal[8]
        sql = grab_sql("grab_journal_source_all")
        source_cursor.execute(sql,(artist, mature))
        obt_source = source_cursor.fetchone()
        obt_source_artist = obt_source[0]
        obt_source_dcuuid = obt_source[1]
        obt_source_latest_title = obt_source[2]
        obt_source_latest_url = obt_source[3]
        obt_source_latest_excerpt = obt_source[4]
        obt_source_last_ids = obt_source[5]
        obt_source_last_check = obt_source[6]
        obt_source_latest_update = obt_source[7]
        obt_source_latest_pp = obt_source[8]
        obt_source_response = obt_source[9]
        obt_source_mature = obt_source[10]
        obt_source_thumb_img_url = obt_source[11]
        obt_source_last_urls = obt_source[12]
        obt_source_last_excerpts = obt_source[13]
        obt_source_last_titles = obt_source[14]
        if not dc_uuid == obt_source_dcuuid:
            if not obt_source_last_ids[0] == last_ids[0]:
                new_deviations = determineNewJournals(obt_source_last_ids, last_ids)
                sql = grab_sql("add_journal_notification")
                index = 0
                change_sql = grab_sql("change_journal_listener")
                new_dccuid = str(uuid.uuid1())
                timestr = str(datetime.datetime.now())
                try:
                    changeCommits.append((new_dccuid, timestr, obt_source_last_ids, artist, serverid, channelid))
                except Exception as Ex:
                    print("Exception")
                while not index == new_deviations:
                    timestr = str(datetime.datetime.now())
                    notificationCommits.append((channelid, artist, latest_pp, obt_source_last_titles[index],obt_source_last_urls[index],obt_source_thumb_img_url[index], timestr, mature))
                    index = index + 1
                post_notif_sql = grab_sql("add_journal_notification")
                try:
                    psycopg2.extras.execute_values(write_cursor, change_sql, changeCommits)
                    psycopg2.extras.execute_values(write_cursor, post_notif_sql, notificationCommits)
                except Exception as EX2:
                    print("Exception")
                conn.commit()
            else:
                print("Skipped")


    print("Finished syncJournals!")