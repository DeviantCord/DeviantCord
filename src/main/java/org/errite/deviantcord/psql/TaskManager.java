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
import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.util.mis;

import java.sql.*;
import java.util.UUID;

public class TaskManager {

    public static void addAllTask(long serverId, long channelId, String artistName, String folderId,
                                  boolean mature, HikariDataSource ds, int shardId){
        String sql = SQLManager.grab_sql("grab_all_source_import");

        try{
            Connection taskConnection = ds.getConnection();
            PreparedStatement pstmt = taskConnection.prepareStatement(sql);
            pstmt.setString(1, artistName);
            pstmt.setBoolean(2, mature);
            ResultSet obtSource = pstmt.executeQuery();
            sql = SQLManager.grab_sql("new_all_task");
            PreparedStatement writePstmt = taskConnection.prepareStatement(sql);
            writePstmt.setLong(1,serverId);
            writePstmt.setString(2, artistName);
            writePstmt.setString(3, folderId);
            writePstmt.setString(4, "all-folder");
            UUID uuid = UUID.randomUUID();
            writePstmt.setString(5, uuid.toString());
            writePstmt.setBoolean(6, false);
            writePstmt.setArray(7, null);
            writePstmt.setLong(8, channelId);
            Timestamp timestamp = new Timestamp(System.currentTimeMillis());
            writePstmt.setTimestamp(9, timestamp);
            writePstmt.setTimestamp(10, timestamp);
            writePstmt.setBoolean(12, true);
            writePstmt.setBoolean(11, false);
            writePstmt.setString(13, "ALL FOLDER");
            obtSource.next();
            writePstmt.setArray(14, obtSource.getArray(11));
            writePstmt.setBoolean(15, mature);
            writePstmt.setInt(16, shardId);
            writePstmt.executeUpdate();
            taskConnection.close();

        } catch (SQLException e) {
            throw new RuntimeException(e);
        }


    }
    public static void AddTask(long server_id, long channel_id, String artist_name, String folder_id, String foldername, boolean inverse,
                        boolean hybrid, boolean mature, HikariDataSource ds, int shard_id) {

        String sql = SQLManager.grab_sql("grab_source_import");
        try{
        Connection task_conn = ds.getConnection();
        PreparedStatement pstmt = task_conn.prepareStatement(sql);
        // use pstmt here
        pstmt.setString(1, folder_id);
        pstmt.setBoolean(2,inverse);
        pstmt.setBoolean(3, hybrid);
        pstmt.setBoolean(4, mature);
        ResultSet taskRS = pstmt.executeQuery();
        String nt_sql = SQLManager.grab_sql("new_task");
        int index = 0;
        while(!(index == 1) && taskRS.next())
        {
            pstmt = task_conn.prepareStatement(nt_sql);
            pstmt.setLong(1,server_id);
            pstmt.setString(2, artist_name);
            pstmt.setString(3, folder_id);
            pstmt.setString(4, "regular");
            UUID uuid = UUID.randomUUID();
            pstmt.setString(5, uuid.toString());
            pstmt.setBoolean(6, false);
            pstmt.setArray(7, null);
            pstmt.setLong(8, channel_id);
            Timestamp timestamp = new Timestamp(System.currentTimeMillis());
            pstmt.setTimestamp(9, timestamp);
            pstmt.setTimestamp(10, timestamp);
            pstmt.setBoolean(12, inverse);
            pstmt.setBoolean(11, hybrid);
            pstmt.setString(13, foldername);
            pstmt.setArray(14, taskRS.getArray(14));
            pstmt.setArray(15, taskRS.getArray(15) );
            pstmt.setBoolean(16, mature);
            pstmt.setInt(17, shard_id);
            pstmt.executeUpdate();
            index++;
        }

        } catch (SQLException throwables) {
            throwables.printStackTrace();
        }

    }
    public static void DeleteTask(long serverid, long channel_id, String artist_name, String foldername, String folder_id, boolean mature, HikariDataSource ds)
    {
        String sql = SQLManager.grab_sql("delete_listener");
        try{
            Connection task_conn = ds.getConnection();
            PreparedStatement pstmt = task_conn.prepareStatement(sql);
            pstmt.setLong(1, serverid);
            pstmt.setString(2, artist_name);
            pstmt.setString(3, foldername);
            pstmt.setLong(4, channel_id);
            pstmt.executeUpdate();

        }
        catch (SQLException throwables) {
            throwables.printStackTrace();
        }

    }

    public static boolean verifyAllTaskDuplicate(String artist, long serverId, long channelId,
                                                 HikariDataSource ds) throws SQLException {
        Connection obt_conn = ds.getConnection();
        String sql = SQLManager.grab_sql("duplicate_all_check");
        PreparedStatement pstmt = obt_conn.prepareStatement(sql, ResultSet.TYPE_SCROLL_SENSITIVE,
                ResultSet.CONCUR_UPDATABLE);
        pstmt.setLong(1, channelId);
        pstmt.setLong(2, serverId);
        pstmt.setString(3, artist);
        ResultSet rs = pstmt.executeQuery();
        return mis.InvertBoolean(DBUtils.resultSetEmpty(rs));
    }
}
