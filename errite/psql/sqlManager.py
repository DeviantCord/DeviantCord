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
delete_notification_tasks = """ DELETE FROM deviantcord.deviation_notifications WHERE id = %s;"""
delete_listener = """DELETE FROM deviantcord.deviation_listeners where serverid = %s AND artist = %s AND foldername = %s
AND channelid = %s"""
delete_all_listener = """DELETE FROM deviantcord.deviation_listeners where serverid = %s AND artist = %s AND mature = %s 
AND channelid = %s AND foldertype = %s """

create_server_info = """INSERT INTO deviantcord.server_config(serverid, prefix, errite_optout,
                        required_role, updated)
                                     VALUES(%s,%s,%s,%s,%s); """

duplicate_check = """SELECT artist FROM deviantcord.deviation_listeners WHERE channelid = %s AND serverid = %s AND artist = %s
AND foldername = %s AND foldertype = 'regular'"""
duplicate_all_check = """SELECT artist FROM deviantcord.deviation_listeners WHERE channelid = %s AND serverid = %s AND artist = %s
AND foldername = %s AND foldertype = 'all-folder'"""
grab_server_listeners = """SELECT * from deviantcord.deviation_listeners WHERE serverid = %s ORDER BY artist ASC"""
grab_server_info = """SELECT prefix, required_role FROM deviantcord.server_config WHERE serverid = %s;"""
grab_server_info_explicit = """SELECT prefix, required_role FROM deviantcord.server_config WHERE serverid = %s AND errite_optout = %s;"""
grab_source_dcuuid = """SELECT dc_uuid, last_ids, last_hybrid_ids from deviantcord.deviation_data WHERE artist = %s AND folder_name = %s AND
inverse_folder = %s AND hybrid = %s;"""
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
verify_all_source_existance = """SELECT artist FROM deviantcord.deviation_data_all WHERE artist = %s AND mature = %s"""
verify_source_existance = """SELECT artist FROM deviantcord.deviation_data WHERE artist = %s AND folder_name = %s AND
                                                    inverse_folder = %s AND hybrid = %s AND mature = %s"""
no_listener_duplicate = """SELECT artist FROM deviantcord.deviation_listeners WHERE artist = %s AND foldername = %s AND
channelid = %s"""
get_listener = """SELECT * from deviantcord.deviation_listeners WHERE artist = %s AND foldername = %s AND
 channelid = %s;"""
grab_source_import = """SELECT * FROM deviantcord.deviation_data WHERE folderid = %s AND inverse_folder = %s AND hybrid = %s
 AND mature = %s;"""
grab_all_source_import = """SELECT * FROM deviantcord.deviation_data_all WHERE artist = %s and mature = %s"""
new_source = """INSERT INTO deviantcord.deviation_data(artist, folder_name, folderid,
                         inverse_folder, dc_uuid, last_update, last_check, latest_img_urls, response, latest_deviation_url,
                         latest_pp_url, mature, last_urls, last_ids, last_hybrid_ids, hybrid, given_offset, hybrid_urls, 
                          hybrid_img_urls)
                                     VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); """
new_all_source = """INSERT INTO deviantcord.deviation_data_all(artist,dc_uuid, last_update, last_check, latest_img_urls,
                    latest_pp_url, latest_deviation_url, response,mature, last_urls, last_ids )
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s); """
new_task = """INSERT INTO deviantcord.deviation_listeners(serverid, artist,folderid, foldertype, dc_uuid, ping_role, roles, channelid, created, last_update, hybrid, inverse, foldername, last_ids, last_hybrids, mature)
                             VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s,%s);"""


def grab_sql(sql_title):
    """
        Method ran grab SQL queries from sqlManager.

        :param sql_title: The artist's name that owns the folder.
        :type sql_title: string
        :return: str
        """
    queries ={
        "delete_notifications": delete_notification_tasks,
        "delete_listener": delete_listener,
        "delete_all_listener": delete_all_listener,
        "delete_server_config": server_leave_config,
        "delete_server_data": server_leave_data,
        "insert_server_info": create_server_info,
        "grab_server_info": grab_server_info,
        "grab_server_listeners": grab_server_listeners,
        "grab_server_info_exp": grab_server_info_explicit,
        "grab_source_import": grab_source_import,
        "grab_all_source_import": grab_all_source_import,
        "grab_source_dcuuid": grab_source_dcuuid,
        "get_listener": get_listener,
        "new_server": new_server,
        "update_rank": update_rank,
        "update_prefix": update_prefix,
        "update_hybrid": update_hybrid,
        "update_inverse": update_inverse,
        "update_channel": update_channel,
        "verify_all_source_exists": verify_all_source_existance,
        "verify_source_exists": verify_source_existance,
        "duplicate_check": duplicate_check,
        "duplicate_all_check": duplicate_all_check,
        "new_task": new_task,
        "new_source": new_source,
        "new_all_source": new_all_source
    }
    return queries.get(sql_title, "not found")
def get_sql(value, sql):
    return {
        'delete_notifications': lambda sql: delete_notification_tasks,
    }.get(value)(sql)