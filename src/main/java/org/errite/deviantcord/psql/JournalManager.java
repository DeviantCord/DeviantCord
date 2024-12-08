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
import org.errite.deviantcord.types.JournalObject;
import org.errite.deviantcord.util.mis;

import java.sql.*;
import java.util.Locale;
import java.util.UUID;

import static org.errite.deviantcord.util.mis.gatherJournals;

public class JournalManager {
        public static void addJournalSource(Response da_response, String artist, HikariDataSource ds, boolean mature) throws SQLException {
                JournalObject gatheredJournals = gatherJournals(da_response);
                
                try (Connection writeCon = ds.getConnection();
                     PreparedStatement pstmt = writeCon.prepareStatement(SQLManager.grab_sql("new_journal_source"))) {
                    
                    writeCon.setAutoCommit(false);
                    
                    try {
                        pstmt.setString(1, artist.toUpperCase(Locale.ROOT));
                        pstmt.setString(2, UUID.randomUUID().toString());
                        pstmt.setString(3, gatheredJournals.getLatestTitle());
                        pstmt.setString(4, gatheredJournals.getJournalUrls().get(0));
                        pstmt.setString(5, gatheredJournals.getExcerpts().get(0));
                        pstmt.setArray(6, writeCon.createArrayOf("TEXT",
                                gatheredJournals.getDeviationIds().toArray(new String[0])));
                        
                        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
                        pstmt.setTimestamp(7, timestamp);
                        pstmt.setTimestamp(8, timestamp);
                        pstmt.setString(9, gatheredJournals.getProfilePicture());
                        pstmt.setBoolean(10, mature);
                        pstmt.setString(11, gatheredJournals.getThumbnailImgUrls().get(0));
                        
                        // Arrays for journal data
                        pstmt.setArray(12, writeCon.createArrayOf("TEXT",
                                gatheredJournals.getJournalUrls().toArray(new String[0])));
                        pstmt.setArray(13, writeCon.createArrayOf("TEXT",
                                gatheredJournals.getExcerpts().toArray(new String[0])));
                        pstmt.setArray(14, writeCon.createArrayOf("TEXT",
                                gatheredJournals.getTitles().toArray(new String[0])));
                        pstmt.setArray(15, writeCon.createArrayOf("TEXT",
                                gatheredJournals.getThumbnailIds().toArray(new String[0])));
                        
                        pstmt.executeUpdate();
                        writeCon.commit();
                        
                    } catch (SQLException e) {
                        try {
                            writeCon.rollback();
                        } catch (SQLException rollbackEx) {
                            e.addSuppressed(rollbackEx);
                        }
                        throw e;
                    }
                }
            }
            
    public static void addJournalTask(HikariDataSource ds, String artist, boolean mature, long serverId,
                                 long channelId) throws SQLException {
    String obtSourceSQL = SQLManager.grab_sql("grab_journal_source_dcuuid") + " LIMIT 1"; // Added LIMIT 1
    String listenerSQL = SQLManager.grab_sql("new_journal_listener");

    try (Connection obtSourceCon = ds.getConnection();
         PreparedStatement obtSourceStmt = obtSourceCon.prepareStatement(obtSourceSQL)) {
        
        obtSourceCon.setAutoCommit(false);
        
        try {
            // Get source data
            obtSourceStmt.setString(1, artist.toUpperCase());
            obtSourceStmt.setBoolean(2, mature);
            
            try (ResultSet obtSource = obtSourceStmt.executeQuery()) {
                if (!obtSource.next()) {
                    throw new SQLException("No journal source found for artist: " + artist);
                }
                
                String obtDccuid = obtSource.getString(1);
                Timestamp timestamp = new Timestamp(System.currentTimeMillis());

                // Create new journal listener
                try (PreparedStatement pstmt = obtSourceCon.prepareStatement(listenerSQL)) {
                    pstmt.setString(1, artist.toUpperCase());
                    pstmt.setString(2, obtDccuid);
                    pstmt.setArray(3, obtSource.getArray(2));
                    pstmt.setString(4, timestamp.toString());
                    pstmt.setString(5, timestamp.toString());
                    pstmt.setString(6, obtSource.getString(3));
                    pstmt.setBoolean(7, mature);
                    pstmt.setLong(8, serverId);
                    pstmt.setLong(9, channelId);
                    
                    pstmt.executeUpdate();
                }
                
                obtSourceCon.commit();
            }
        } catch (SQLException e) {
            try {
                obtSourceCon.rollback();
            } catch (SQLException rollbackEx) {
                e.addSuppressed(rollbackEx);
            }
            throw e;
        }
    }
}
    public static boolean verifySourceJournalExists(HikariDataSource ds, String artist, boolean mature) throws SQLException {
        String journalSql = SQLManager.grab_sql("journal_exists");
        Connection journalConn = ds.getConnection();
        PreparedStatement pstmt = journalConn.prepareStatement(journalSql, ResultSet.TYPE_SCROLL_SENSITIVE,
                ResultSet.CONCUR_UPDATABLE);
        pstmt.setString(1,artist.toUpperCase(Locale.ROOT));
        pstmt.setBoolean(2, mature);
        ResultSet obtSource = pstmt.executeQuery();
        return mis.InvertBoolean(DBUtils.resultSetEmpty(obtSource));
    }

    public static boolean verifyListenerJournalExists(HikariDataSource ds, String artist, boolean mature) throws SQLException{
        String journalSql = SQLManager.grab_sql("journal_listener_exists");
        Connection journalConn = ds.getConnection();
        PreparedStatement pstmt = journalConn.prepareStatement(journalSql, ResultSet.TYPE_SCROLL_SENSITIVE,
                ResultSet.CONCUR_UPDATABLE);
        pstmt.setString(1,artist.toUpperCase(Locale.ROOT));
        pstmt.setBoolean(2, mature);
        ResultSet obtSource = pstmt.executeQuery();
        return mis.InvertBoolean(DBUtils.resultSetEmpty(obtSource));
    }
}
