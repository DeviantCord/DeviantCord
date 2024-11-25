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
import io.restassured.response.Response;
import org.errite.deviantcord.types.StatusObject;
import org.errite.deviantcord.util.mis;

import java.sql.*;
import java.util.Locale;
import java.util.UUID;

import static org.errite.deviantcord.util.mis.gatherStatuses;

public class StatusManager {

    public static void addStatusSource(Response da_response, String artist, HikariDataSource ds) throws SQLException {
        StatusObject gatheredStatuses = gatherStatuses(da_response);
        Connection writeCon = ds.getConnection();
        String sql = SQLManager.grab_sql("new_status_source");
        PreparedStatement pstmt = writeCon.prepareStatement(sql);
        pstmt.setString(1, artist.toUpperCase(Locale.ROOT));
        UUID uuid = UUID.randomUUID();
        pstmt.setString(2,uuid.toString());
        pstmt.setArray(3, writeCon.createArrayOf("TEXT", gatheredStatuses.getStatusIds().toArray()));
        pstmt.setArray(4, writeCon.createArrayOf("TEXT", gatheredStatuses.getThumbnailImgUrls().toArray(new String[0])));
        pstmt.setArray(5, writeCon.createArrayOf("TEXT", gatheredStatuses.getStatusUrls().toArray()));
        pstmt.setArray(6, writeCon.createArrayOf("TEXT", gatheredStatuses.getExcerpts().toArray(new String[0])));
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        pstmt.setTimestamp(7,timestamp);
        pstmt.setTimestamp(8, timestamp);
        pstmt.setString(9, gatheredStatuses.getProfilePic());
        pstmt.setArray(10, writeCon.createArrayOf("TEXT",gatheredStatuses.getThumbnailIds().toArray()));
        pstmt.executeUpdate();
        writeCon.close();


    }
    public static void addStatusTask(HikariDataSource ds, String artist, long serverId,
                                      long channelId) throws SQLException {
        String obtSourceSQL = SQLManager.grab_sql("grab_status_source_dcuuid");
        Connection obtSourceCon = ds.getConnection();
        PreparedStatement obtSourceStmt = obtSourceCon.prepareStatement(obtSourceSQL);
        obtSourceStmt.setString(1, artist);
        ResultSet obtSource = obtSourceStmt.executeQuery();
        obtSource.next();
        String obt_dccuid = obtSource.getString(1);
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());

        String listenerSQL = SQLManager.grab_sql("new_status_listener");
        PreparedStatement pstmt = obtSourceCon.prepareStatement(listenerSQL);
        pstmt.setString(1, artist.toUpperCase(Locale.ROOT));
        pstmt.setString(2, obt_dccuid);
        pstmt.setArray(3,obtSource.getArray(2));
        pstmt.setString(4, timestamp.toString());
        pstmt.setString(5,timestamp.toString());
        pstmt.setString(6, obtSource.getString(3));
        pstmt.setLong(7, serverId);
        pstmt.setLong(8, channelId);
        pstmt.executeUpdate();
        obtSourceCon.close();

    }
    public static boolean verifySourceStatusExists(HikariDataSource ds, String artist) throws SQLException {
        String journalSql = SQLManager.grab_sql("status_source_exists");
        Connection journalConn = ds.getConnection();
        PreparedStatement pstmt = journalConn.prepareStatement(journalSql, ResultSet.TYPE_SCROLL_SENSITIVE,
                ResultSet.CONCUR_UPDATABLE);
        pstmt.setString(1,artist.toUpperCase(Locale.ROOT));
        ResultSet obtSource = pstmt.executeQuery();
        return mis.InvertBoolean(DBUtils.resultSetEmpty(obtSource));
    }

    public static boolean verifyListenerStatusExists(HikariDataSource ds, String artist) throws SQLException{
        String journalSql = SQLManager.grab_sql("status_listener_exists");
        Connection journalConn = ds.getConnection();
        PreparedStatement pstmt = journalConn.prepareStatement(journalSql, ResultSet.TYPE_SCROLL_SENSITIVE,
                ResultSet.CONCUR_UPDATABLE);
        pstmt.setString(1,artist.toUpperCase(Locale.ROOT));
        ResultSet obtSource = pstmt.executeQuery();
        return mis.InvertBoolean(DBUtils.resultSetEmpty(obtSource));
    }
}
