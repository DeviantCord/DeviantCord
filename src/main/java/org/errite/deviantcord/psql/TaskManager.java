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
import io.sentry.Sentry;
public class TaskManager {

    public static void addAllTask(long serverId, long channelId, String artistName, String folderId,
                             boolean mature, HikariDataSource ds, int shardId) {
    String sourceSql = SQLManager.grab_sql("grab_all_source_import");
    String taskSql = SQLManager.grab_sql("new_all_task");

    try (Connection taskConnection = ds.getConnection();
         PreparedStatement pstmt = taskConnection.prepareStatement(sourceSql);
         PreparedStatement writePstmt = taskConnection.prepareStatement(taskSql)) {
        
        // Start transaction
        taskConnection.setAutoCommit(false);
        
        try {
            // Execute source query
            pstmt.setString(1, artistName);
            pstmt.setBoolean(2, mature);
            
            try (ResultSet obtSource = pstmt.executeQuery()) {
                if (!obtSource.next()) {
                    throw new SQLException("No data found for artist: " + artistName);
                }
                
                // Prepare the task insert
                writePstmt.setLong(1, serverId);
                writePstmt.setString(2, artistName);
                writePstmt.setString(3, folderId);
                writePstmt.setString(4, "all-folder");
                writePstmt.setString(5, UUID.randomUUID().toString());
                writePstmt.setBoolean(6, false);
                writePstmt.setArray(7, null);
                writePstmt.setLong(8, channelId);
                
                Timestamp timestamp = new Timestamp(System.currentTimeMillis());
                writePstmt.setTimestamp(9, timestamp);
                writePstmt.setTimestamp(10, timestamp);
                writePstmt.setBoolean(11, false);
                writePstmt.setBoolean(12, true);
                writePstmt.setString(13, "ALL FOLDER");
                writePstmt.setArray(14, obtSource.getArray(11));
                writePstmt.setBoolean(15, mature);
                writePstmt.setInt(16, shardId);
                
                writePstmt.executeUpdate();
                
                // Commit the transaction
                taskConnection.commit();
            }
        } catch (SQLException e) {
            try {
                taskConnection.rollback();
            } catch (SQLException rollbackEx) {
                // Log rollback failure
                e.addSuppressed(rollbackEx);
            }
            throw e;  // Re-throw the original exception
        }
    } catch (SQLException e) {
            // Log the error here
            throw new RuntimeException("Failed to add all task: " + e.getMessage(), e);
        }
    }

    
    public static void AddTask(long server_id, long channel_id, String artist_name, String folder_id, 
                          String foldername, boolean inverse, boolean hybrid, boolean mature, 
                          HikariDataSource ds, int shard_id) {
    
    String sourceSql = SQLManager.grab_sql("grab_source_import");
    String taskSql = SQLManager.grab_sql("new_task");

    try (Connection taskConn = ds.getConnection();
         PreparedStatement sourceStmt = taskConn.prepareStatement(sourceSql)) {
        
        // Start transaction
        taskConn.setAutoCommit(false);
        
        try {
            sourceStmt.setString(1, folder_id);
            sourceStmt.setBoolean(2, inverse);
            sourceStmt.setBoolean(3, hybrid);
            sourceStmt.setBoolean(4, mature);
            
            try (ResultSet taskRS = sourceStmt.executeQuery()) {
                if (!taskRS.next()) {
                    throw new SQLException("No data found for folder: " + folder_id);
                }
                
                try (PreparedStatement taskStmt = taskConn.prepareStatement(taskSql)) {
                    // Prepare the task insert
                    taskStmt.setLong(1, server_id);
                    taskStmt.setString(2, artist_name);
                    taskStmt.setString(3, folder_id);
                    taskStmt.setString(4, "regular");
                    taskStmt.setString(5, UUID.randomUUID().toString());
                    taskStmt.setBoolean(6, false);
                    taskStmt.setArray(7, null);
                    taskStmt.setLong(8, channel_id);
                    
                    Timestamp timestamp = new Timestamp(System.currentTimeMillis());
                    taskStmt.setTimestamp(9, timestamp);
                    taskStmt.setTimestamp(10, timestamp);
                    taskStmt.setBoolean(11, hybrid);
                    taskStmt.setBoolean(12, inverse);
                    taskStmt.setString(13, foldername);
                    taskStmt.setArray(14, taskRS.getArray(14));
                    taskStmt.setArray(15, taskRS.getArray(15));
                    taskStmt.setBoolean(16, mature);
                    taskStmt.setInt(17, shard_id);
                    
                    taskStmt.executeUpdate();
                }
                
                // Commit the transaction
                taskConn.commit();
            }
        } catch (SQLException e) {
            try {
                taskConn.rollback();
            } catch (SQLException rollbackEx) {
                e.addSuppressed(rollbackEx);
            }
            throw e;
        }
    } catch (SQLException e) {
        throw new RuntimeException("Failed to add task: " + e.getMessage(), e);
        }
    }   


    public static void DeleteTask(long serverid, long channel_id, String artist_name, String foldername, String folder_id, boolean mature, HikariDataSource ds)
    {
        String sql = SQLManager.grab_sql("delete_listener");
        
        try(Connection task_conn = ds.getConnection();)
        {
            task_conn.setAutoCommit(false);
            try{
                
            PreparedStatement pstmt = task_conn.prepareStatement(sql);
            pstmt.setLong(1, serverid);
            pstmt.setString(2, artist_name);
            pstmt.setString(3, foldername);
            pstmt.setLong(4, channel_id);
            pstmt.executeUpdate();
            task_conn.commit();
            }
            catch(SQLException e){
                task_conn.rollback();
                throw e;
            }
        }
        catch (SQLException throwables) {
            throwables.printStackTrace();
            Sentry.captureException(throwables);
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
