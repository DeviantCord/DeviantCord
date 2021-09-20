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
add_journal_notification = """ INSERT INTO deviantcord.journal_notifications(channelid, artist, pp_url, title, 
url, thumbnail, notifcation_creation, mature) VALUES %s """
cleanup_journal_listener_leave = """DELETE FROM deviantcord.journal_listeners WHERE serverid = %s"""
delete_notification_tasks = """ DELETE FROM deviantcord.deviation_notifications WHERE id = %s;"""
delete_listener = """DELETE FROM deviantcord.deviation_listeners where serverid = %s AND artist = %s AND foldername = %s
AND channelid = %s"""
delete_all_listener = """DELETE FROM deviantcord.deviation_listeners where serverid = %s AND artist = %s AND mature = %s 
AND channelid = %s AND foldertype = %s """
delete_journal_notification = """DELETE FROM deviantcord.journal_notifications where id = %s"""
delete_journal_listener = """DELETE FROM deviantcord.journal_listeners where artist = %s AND channelid = %s AND mature = %s"""
create_server_info = """INSERT INTO deviantcord.server_config(serverid, prefix, errite_optout,
                        required_role, updated)
                                     VALUES(%s,%s,%s,%s,%s); """

duplicate_check = """SELECT artist FROM deviantcord.deviation_listeners WHERE channelid = %s AND serverid = %s AND artist = %s
AND foldername = %s AND foldertype = 'regular'"""
duplicate_all_check = """SELECT artist FROM deviantcord.deviation_listeners WHERE channelid = %s AND serverid = %s AND artist = %s
AND foldername = %s AND foldertype = 'all-folder'"""
grab_server_listeners = """SELECT * from deviantcord.deviation_listeners WHERE serverid = %s ORDER BY artist ASC"""
grab_server_journals = """SELECT * FROM deviantcord.journal_listeners WHERE serverid = %s"""
grab_server_info = """SELECT prefix, required_role FROM deviantcord.server_config WHERE serverid = %s;"""
grab_server_info_explicit = """SELECT prefix, required_role FROM deviantcord.server_config WHERE serverid = %s AND errite_optout = %s;"""
grab_source_dcuuid = """SELECT dc_uuid, last_ids, last_hybrid_ids from deviantcord.deviation_data WHERE artist = %s AND folder_name = %s AND
inverse_folder = %s AND hybrid = %s;"""
get_all_source_journal = """SELECT * FROM deviantcord.journal_data"""
get_all_journal_listeners = """SELECT * FROM deviantcord.journal_listeners"""
get_all_journal_notifications = """SELECT * FROM deviantcord.journal_notifications"""
grab_journal_source_all = """SELECT * FROM deviantcord.journal_data WHERE artist = %s AND mature = %s"""
grab_journal_source_dcuuid = """SELECT dc_uuid, last_ids, latest_pp FROM deviantcord.journal_data WHERE artist = %s and mature = %s"""
grab_sync_journalsource = """SELECT * FROM deviantcord.journal_data"""
grab_journal_source = """SELECT * FROM deviantcord.journal_data"""
journal_source_check = """ UPDATE deviantcord.journal_data
             SET last_check = data.last_check FROM (VALUES %s) AS data(last_check, artist)
             WHERE deviantcord.journal_data.artist = data.artist"""
journal_source_change = """ UPDATE deviantcord.journal_data
             SET dc_uuid = data.dcuuid, latest_update = data.latest_update, last_check = data.last_check, 
             thumb_img_url = data.thumb_img_url::text[], latest_pp = data.latest_pp_url::text,
             latest_url = data.latest_deviation_url,  response = data.response::jsonb, last_urls = data.last_urls::text[],
              last_ids = data.last_ids::text[],last_titles = data.last_titles::text[], thumb_ids = data.thumb_ids::text[], last_excerpts = data.excerpts::text[] FROM (VALUES %s) AS data(dcuuid, latest_update, last_check, thumb_img_url, latest_pp_url, latest_deviation_url,
                         response, last_urls, last_ids, last_titles, thumb_ids, last_thumbs, excerpts, artist, mature)
             WHERE deviantcord.journal_data.artist = data.artist AND deviantcord.journal_data.mature = data.mature"""
new_server = """INSERT INTO deviantcord.server_config(serverid, prefix, errite_optout, required_role, updated) VALUES 
(%s, %s, %s, %s, default)"""
server_leave_config = """DELETE FROM deviantcord.server_config WHERE serverid = %s"""
server_leave_data = """DELETE FROM deviantcord.deviation_listeners WHERE serverid = %s"""
update_rank = """UPDATE deviantcord.server_config set required_role = %s, updated = %s WHERE serverid = %s;"""
update_prefix = """UPDATE deviantcord.server_config set prefix = %s, updated = %s WHERE serverid = %s;"""
update_hybrid = """UPDATE deviantcord.deviation_listeners set hybrid = %s, dc_uuid = %s, last_ids = %s,
 last_hybrids = %s, last_update = %s  WHERE serverid = %s AND channelid = %s AND folderid =%s AND foldertype = %s;"""
update_inverse = """UPDATE deviantcord.deviation_listeners set inverse = %s, dc_uuid = %s, last_ids = %s,
 last_hybrids = %s, last_update = %s  WHERE serverid = %s AND channelid = %s AND folderid =%s AND foldertype = %s;"""
update_channel = """UPDATE deviantcord.deviation_listeners set channelid = %s WHERE channelid = %s AND foldername = %s AND
artist = %s"""
change_journal_listener = """ UPDATE deviantcord.journal_listeners
                     SET dc_uuid = data.dcuuid, latest_update = data.last_update, 
                    last_ids = data.last_ids::text[] FROM (VALUES %s) AS data(dcuuid, last_update, last_ids, artist, serverid, channelid)
                     WHERE deviantcord.journal_listeners.artist = data.artist AND deviantcord.journal_listeners.serverid
                      = data.serverid AND deviantcord.journal_listeners.channelid = data.channelid"""
verify_journal_source_existance = """SELECT * FROM deviantcord.journal_data WHERE artist = %s AND mature = %s"""
verify_journal_listener_existance = """SELECT * FROM deviantcord.journal_listeners WHERE artist = %s AND mature = %s"""
verify_all_source_existance = """SELECT artist FROM deviantcord.deviation_data_all WHERE artist = %s AND mature = %s"""
verify_source_existance = """SELECT artist FROM deviantcord.deviation_data WHERE artist = %s AND folder_name = %s AND
                                                    inverse_folder = %s AND hybrid = %s AND mature = %s"""
no_listener_duplicate = """SELECT artist FROM deviantcord.deviation_listeners WHERE artist = %s AND foldername = %s AND
channelid = %s"""
get_listener = """SELECT * from deviantcord.deviation_listeners WHERE artist = %s AND foldername = %s AND
 channelid = %s;"""
grab_source_import = """SELECT * FROM deviantcord.deviation_data WHERE folderid = %s AND inverse_folder = %s AND hybrid = %s
 AND mature = %s;"""
grab_all_journal_import = """SELECT * FROM deviantcord.journal_data"""
grab_all_source_import = """SELECT * FROM deviantcord.deviation_data_all WHERE artist = %s and mature = %s"""
new_journal_source = """INSERT into deviantcord.journal_data(artist, dc_uuid, latest_title,
 latest_url, latest_excerpt, last_ids, last_check, latest_update, latest_pp, response, mature,
  thumb_img_url, last_urls, last_excerpts, last_titles, thumb_ids) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
new_journal_listener = """INSERT into deviantcord.journal_listeners(artist, dc_uuid, last_ids, last_check, latest_update, latest_pp, mature, serverid, channelid)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
new_source = """INSERT INTO deviantcord.deviation_data(artist, folder_name, folderid,
                         inverse_folder, dc_uuid, last_update, last_check, latest_img_urls, response, latest_deviation_url,
                         latest_pp_url, mature, last_urls, last_ids, last_hybrid_ids, hybrid, given_offset, hybrid_urls, 
                          hybrid_img_urls, shard_id)
                                     VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); """
new_all_source = """INSERT INTO deviantcord.deviation_data_all(artist,dc_uuid, last_update, last_check, latest_img_urls,
                    latest_pp_url, latest_deviation_url, response,mature, last_urls, last_ids, shard_id )
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s); """
new_task = """INSERT INTO deviantcord.deviation_listeners(serverid, artist,folderid, foldertype, dc_uuid, ping_role, roles, channelid, created, last_update, hybrid, inverse, foldername, last_ids, last_hybrids, mature, shard_id)
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s,%s, %s);"""


def grab_sql(sql_title):
    """
        Method ran grab SQL queries from sqlManager.

        :param sql_title: The Alias for the SQL Manager in Lambda.
        :type sql_title: string
        :return: str
        """
    queries ={
        "change_journal_listener": change_journal_listener,
        "delete_notifications": delete_notification_tasks,
        "add_journal_notification": add_journal_notification,
        "delete_listener": delete_listener,
        "delete_journal_notification": delete_journal_notification,
        "delete_journal_listener": delete_journal_listener,
        "cleanup_journal_Listener_leave": cleanup_journal_listener_leave,
        "delete_all_listener": delete_all_listener,
        "delete_server_config": server_leave_config,
        "delete_server_data": server_leave_data,
        "insert_server_info": create_server_info,
        "get_all_journal_listeners": get_all_journal_listeners,
        "get_all_journal_notifications": get_all_journal_notifications,
        "grab_server_info": grab_server_info,
        "grab_server_journals": grab_server_journals,
        "grab_server_listeners": grab_server_listeners,
        "grab_server_info_exp": grab_server_info_explicit,
        "grab_all_source_journals": grab_all_journal_import,
        "grab_journal_source": grab_journal_source,
        "grab_journal_source_all": grab_journal_source_all,
        "grab_source_import": grab_source_import,
        "grab_all_source_import": grab_all_source_import,
        "grab_journal_source_dcuuid": grab_journal_source_dcuuid,
        "grab_source_dcuuid": grab_source_dcuuid,
        "get_listener": get_listener,
        "new_server": new_server,
        "journal_source_change": journal_source_change,
        "journal_source_check": journal_source_check,
        "new_journal_source": new_journal_source,
        "new_journal_listener": new_journal_listener,
        "update_rank": update_rank,
        "update_prefix": update_prefix,
        "update_hybrid": update_hybrid,
        "update_inverse": update_inverse,
        "update_channel": update_channel,
        "journal_exists": verify_journal_source_existance,
        "journal_listener_exists": verify_journal_listener_existance,
        "verify_all_source_exists": verify_all_source_existance,
        "verify_source_exists": verify_source_existance,
        "duplicate_check": duplicate_check,
        "duplicate_all_check": duplicate_all_check,
        "new_task": new_task,
        "new_source": new_source,
        "new_all_source": new_all_source
    }
    return queries.get(sql_title, "INVALID LAMBDA QUERY. COULD NOT GET SQL QUERY")
def get_sql(value, sql):
    return {
        'delete_notifications': lambda sql: delete_notification_tasks,
    }.get(value)(sql)