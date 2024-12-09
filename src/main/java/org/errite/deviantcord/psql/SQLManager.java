/*
 * DeviantCord 4
 * Copyright (C) 2020-2024  Errite Softworks LLC/ ErriteEpticRikez
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
package org.errite.deviantcord.psql;

public class SQLManager {
    public static String add_journal_notification = 
        "INSERT INTO deviantcord.journal_notifications(channelid, artist, pp_url, title, url, thumbnail, notifcation_creation, mature) " +
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
    public static String cleanup_journal_listener_leave = "DELETE FROM deviantcord.journal_listeners WHERE serverid = ?";
    public static String delete_notification_tasks = " DELETE FROM deviantcord.deviation_notifications WHERE id = ?;";
    public static String delete_listener = "DELETE FROM deviantcord.deviation_listeners WHERE serverid = ? AND artist = ? AND foldername = ? AND channelid = ?";
    public static String delete_server_listeners = "DELETE FROM deviantcord.deviation_listeners WHERE serverid = ?";
    public static String delete_server_journal = "DELETE FROM deviantcord.journal_listeners WHERE serverid = ?";
    public static String delete_server_config = "DELETE FROM deviantcord.server_config WHERE serverid = ?";
    public static String delete_journal = "DELETE FROM deviantcord.journal_listeners WHERE serverid = ? and artist = ? AND channelid = ?";
    public static String delete_status = "DELETE FROM deviantcord.status_listeners WHERE serverid = ? and artist = ? AND channelid = ?";
    public static String delete_all_listener = "DELETE FROM deviantcord.deviation_listeners where serverid = ? AND artist = ? AND mature = ? " +
            "AND channelid = ? AND foldertype = ? ";
    public static String delete_journal_notification = "DELETE FROM deviantcord.journal_notifications where id = ?";
    public static String  create_server_info = "INSERT INTO deviantcord.server_config(serverid, prefix, errite_optout,required_role, updated) VALUES(?,?,?,?,?); ";

    public static String duplicate_check = "SELECT artist FROM deviantcord.deviation_listeners WHERE channelid = ? AND serverid = ? AND artist = ? AND foldername = ? AND foldertype = 'regular'";
    public static String duplicate_all_check = "SELECT artist FROM deviantcord.deviation_listeners WHERE channelid = ? AND serverid = ? AND artist = ? AND foldertype = 'all-folder'";
    public static String grab_server_listeners = "SELECT * from deviantcord.deviation_listeners WHERE serverid = ? ORDER BY artist ASC";
    public static String grab_server_journals = "SELECT * FROM deviantcord.journal_listeners WHERE serverid = ?";
    public static String grab_server_info = "SELECT prefix, required_role FROM deviantcord.server_config WHERE serverid = ?;";
    public static String grab_server_info_explicit = "SELECT prefix, required_role FROM deviantcord.server_config WHERE serverid = ? AND errite_optout = ?;";
    public static String grab_update_listeners = "SELECT artist, foldername, channelid, mature, inverse from deviantcord.deviation_listeners WHERE serverid = ?";
    public static String grab_source_dcuuid = "SELECT dc_uuid, last_ids, last_hybrid_ids,folderid  from deviantcord.deviation_data WHERE artist = ? AND folder_name = ? AND " +
            "inverse_folder = ? AND hybrid = ?;";
    public static String grab_inverse = "SELECT inverse FROM deviantcord.deviation_listeners WHERE artist = ? AND folder_name = ? AND " +
            "channelid = ? AND serverid = ?";
    public static String get_all_source_journal = "SELECT * FROM deviantcord.journal_data";
    public static String get_all_journal_listeners = "SELECT * FROM deviantcord.journal_listeners";
    public static String get_all_journal_notifications = "SELECT * FROM deviantcord.journal_notifications";
    public static String grab_journal_source_all = "SELECT * FROM deviantcord.journal_data WHERE artist = ? AND mature = ?";
    public static String grab_journal_source_dcuuid = "SELECT dc_uuid, last_ids, latest_pp FROM deviantcord.journal_data WHERE artist = ? and mature = ?";
    public static String grab_status_source_dcuuid = "SELECT dc_uuid, last_statusid, last_pp FROM deviantcord.status_data" +
            " WHERE artist = ?";
    public static String grab_sync_journalsource = "SELECT * FROM deviantcord.journal_data";
    public static String status_source_exists = "SELECT dc_uuid, last_statusid, last_pp FROM deviantcord.status_data WHERE artist = ?";
    public static String status_listener_exists = "SELECT artist, dc_uuid FROM deviantcord.status_listeners WHERE artist = ?";
    public static String grab_journal_source = "SELECT * FROM deviantcord.journal_data";
    public static String grab_folder_uuid = "SELECT folderid FROM deviantcord.deviation_data WHERE artist = ? AND folder_name = ?";
    public static String journal_source_check = 
        "UPDATE deviantcord.journal_data " +
        "SET last_check = data.last_check " +
        "FROM (VALUES (?, ?)) AS data(last_check, artist) " +
        "WHERE deviantcord.journal_data.artist = data.artist";
    public static String journal_source_change = "UPDATE deviantcord.journal_data " +
            "SET dc_uuid = data.dcuuid, latest_update = data.latest_update, last_check = data.last_check, " +
            "thumb_img_url = data.thumb_img_url::text[], latest_pp = data.latest_pp_url::text, " +
            "latest_url = data.latest_deviation_url, response = data.response::jsonb, " +
            "last_urls = data.last_urls::text[], last_ids = data.last_ids::text[], " +
            "last_titles = data.last_titles::text[], thumb_ids = data.thumb_ids::text[], " +
            "last_excerpts = data.excerpts::text[] " +
            "FROM (VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)) AS data" +
            "(dcuuid, latest_update, last_check, thumb_img_url, latest_pp_url, latest_deviation_url, " +
            "response, last_urls, last_ids, last_titles, thumb_ids, last_thumbs, excerpts, artist, mature) " +
            "WHERE deviantcord.journal_data.artist = data.artist AND deviantcord.journal_data.mature = data.mature";
    public static String new_server = "INSERT INTO deviantcord.server_config(serverid, prefix, errite_optout, required_role, updated) VALUES (?, ?, ?, ?, default)";
    public static String server_leave_config = "DELETE FROM deviantcord.server_config WHERE serverid = ?";
    public static String server_leave_data = "DELETE FROM deviantcord.deviation_listeners WHERE serverid = ?";
    public static String update_rank = "UPDATE deviantcord.server_config set required_role = ?, updated = ? WHERE serverid = ?;";
    public static String update_prefix = "UPDATE deviantcord.server_config set prefix = ?, updated = ? WHERE serverid = ?;";
    public static String update_hybrid = "UPDATE deviantcord.deviation_listeners set hybrid = ?, dc_uuid = ?, last_ids = ?," +
            "last_hybrids = ?, last_update = ?  WHERE serverid = ? AND channelid = ? AND folderid =? AND foldertype = ?;";
    public static String update_inverse = "UPDATE deviantcord.deviation_listeners set inverse = ?, dc_uuid = ?, last_ids = ?," +
            "last_hybrids = ?, last_update = ?  WHERE serverid = ? AND channelid = ? AND folderid = ? AND foldertype = ?;";
    public static String update_channel = "UPDATE deviantcord.deviation_listeners set channelid = ? WHERE channelid = ? AND foldername = ? AND artist = ? AND serverid = ?";
    public static String change_journal_listener = " UPDATE deviantcord.journal_listeners " +
            "SET dc_uuid = data.dcuuid, latest_update = data.last_update," +
            "last_ids = data.last_ids::text[] FROM (VALUES ?) AS data(dcuuid, last_update, last_ids, artist, serverid, channelid)" +
            "WHERE deviantcord.journal_listeners.artist = data.artist AND deviantcord.journal_listeners.serverid " +
            "= data.serverid AND deviantcord.journal_listeners.channelid = data.channelid";
    public static String verify_journal_source_existance = "SELECT artist, dc_uuid FROM deviantcord.journal_data WHERE artist = ? AND mature = ?";
    public static String verify_journal_listener_existance = "SELECT artist, dc_uuid FROM deviantcord.journal_listeners WHERE artist = ? AND mature = ?";
    public static String verify_all_source_existance = "SELECT artist FROM deviantcord.deviation_data_all WHERE artist = ? AND mature = ?";
    public static String verify_source_existance = "SELECT artist FROM deviantcord.deviation_data WHERE artist = ? AND folder_name = ? AND " +
            "inverse_folder = ? AND hybrid = ? AND mature = ?";
    public static String no_listener_duplicate = "SELECT artist FROM deviantcord.deviation_listeners WHERE artist = ? AND foldername = ? AND channelid = ?";
    public static String get_listener = "SELECT * from deviantcord.deviation_listeners WHERE artist = ? AND foldername = ? AND channelid = ?;";
    public static String grab_source_import = "SELECT * FROM deviantcord.deviation_data WHERE folderid = ? AND inverse_folder = ? AND hybrid = ? AND mature = ?;";
    public static String grab_all_journal_import = "SELECT * FROM deviantcord.journal_data";
    public static String grab_all_source_import = "SELECT * FROM deviantcord.deviation_data_all WHERE artist = ? and mature = ?";
    public static String new_journal_source = "INSERT into deviantcord.journal_data(artist, dc_uuid, latest_title, latest_url, latest_excerpt, " +
            "last_ids, last_check, latest_update, latest_pp, mature, thumb_img_url, last_urls, last_excerpts, " +
            "last_titles, thumb_ids) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    public static String new_status_listener = "INSERT into deviantcord.status_listeners(artist, dc_uuid, last_ids, last_check" +
            ", latest_update, latest_pp, serverid, channelid) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
    public static String new_status_source = "INSERT into deviantcord.status_data(artist, dc_uuid, last_statusid, last_items_urls, last_urls, " +
            "last_bodys, last_update, last_check, last_pp, thumb_ids) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    public static String new_journal_listener = "INSERT into deviantcord.journal_listeners(artist, dc_uuid, last_ids, last_check, latest_update, " +
            "latest_pp, mature, serverid, channelid) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
    public static String new_source = "INSERT INTO deviantcord.deviation_data(artist, folder_name, folderid, inverse_folder, dc_uuid, " +
            "last_update, last_check, latest_img_urls, latest_deviation_url, latest_pp_url, mature, last_urls, " +
            "last_ids, last_hybrid_ids, hybrid, given_offset, hybrid_urls, hybrid_img_urls, shard_id) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";

    public static String new_all_source = "INSERT INTO deviantcord.deviation_data_all(artist, dc_uuid, last_update, last_check, latest_img_urls, " +
            "latest_pp_url, latest_deviation_url, mature, last_urls, last_ids, shard_id) " +
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    public static String new_task = "INSERT INTO deviantcord.deviation_listeners(serverid, artist, folderid, foldertype, dc_uuid, " +
            "ping_role, roles, channelid, created, last_update, hybrid, inverse, foldername, last_ids, " +
            "last_hybrids, mature, shard_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    public static String new_all_task = "INSERT INTO deviantcord.deviation_listeners(serverid, artist, folderid, foldertype, dc_uuid, " +
            "ping_role, roles, channelid, created, last_update, hybrid, inverse, foldername, last_ids, " +
            "mature, shard_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
    public static String get_channels = "SELECT * FROM deviantcord.deviation_listeners WHERE artist = ? AND foldername = ?";
    public static String get_channels_by_server = "SELECT channelid, artist, foldername FROM deviantcord.deviation_listeners WHERE serverid = ?";
    public static String get_journals_by_server = "SELECT channelid, artist FROM deviantcord.journal_listeners WHERE serverid = ?";
    public static String get_statuses_by_server = "SELECT channelid, artist FROM deviantcord.status_listeners WHERE serverid = ?";
    public static String grab_sql(String key){
        switch(key)
        {
           case "change_journal_listener": return change_journal_listener;
           case "delete_notifications": return delete_notification_tasks;
           case "add_journal_notification": return add_journal_notification;
           case "delete_listener": return delete_listener;
           case "delete_journal_notification": return delete_journal_notification;
           case "delete_journal": return delete_journal;
            case "delete_status": return delete_status;
            case "grab_update_listeners": return grab_update_listeners;
           case "cleanup_journal_Listener_leave": return cleanup_journal_listener_leave;
           case "delete_all_listener": return delete_all_listener;
            case "new_all_task": return new_all_task;
            case "delete_server_config": return server_leave_config;
            case "delete_server_data": return server_leave_data;
            case "insert_server_info": return create_server_info;
            case "get_channels": return get_channels;
            case "get_channels_by_server": return get_channels_by_server;
            case "get_journals_by_server": return get_journals_by_server;
            case "get_statuses_by_server": return get_statuses_by_server;
            case "get_all_journal_listeners": return get_all_journal_listeners;
            case "get_all_journal_notifications": return get_all_journal_notifications;
            case "grab_server_info": return grab_server_info;
            case "grab_server_journals": return grab_server_journals;
            case "grab_server_listeners": return grab_server_listeners;
            case "grab_server_info_exp": return grab_server_info_explicit;
            case "grab_all_source_journals": return grab_all_journal_import;
            case "grab_journal_source": return grab_journal_source;
            case "grab_journal_source_all": return grab_journal_source_all;
            case "grab_source_import": return grab_source_import;
            case "grab_all_source_import": return grab_all_source_import;
            case "grab_journal_source_dcuuid": return grab_journal_source_dcuuid;
            case "grab_status_source_dcuuid": return grab_status_source_dcuuid;
            case "status_source_exists": return status_source_exists;
            case "status_listener_exists": return status_listener_exists;
            case "grab_source_dcuuid": return grab_source_dcuuid;
            case "grab_folder_uuid": return grab_folder_uuid;
            case "get_listener": return get_listener;
            case "new_server": return new_server;
            case "journal_source_change": return journal_source_change;
            case "journal_source_check": return journal_source_check;
            case "new_journal_source": return new_journal_source;
            case "new_journal_listener": return new_journal_listener;
            case "new_status_source": return new_status_source;
            case "new_status_listener": return new_status_listener;
            case "update_rank": return update_rank;
            case "update_prefix": return update_prefix;
            case "update_hybrid": return update_hybrid;
            case "update_inverse": return update_inverse;
            case "update_channel": return update_channel;
            case "journal_exists": return verify_journal_source_existance;
            case "journal_listener_exists": return verify_journal_listener_existance;
            case "verify_all_source_exists": return verify_all_source_existance;
            case "verify_source_exists": return verify_source_existance;
            case "duplicate_check": return duplicate_check;
            case "duplicate_all_check": return duplicate_all_check;
            case "new_task": return new_task;
            case "new_source": return new_source;
            case "new_all_source": return new_all_source;

        }
        return "CANNOT FIND QUERY";
    }
}
