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
import org.errite.deviantcord.da.daParser;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.util.mis;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.errite.deviantcord.psql.DBUtils;

import java.sql.*;
import java.util.*;

public class SourceManager {

    public static boolean verifySourceExistance(String artist, String folder, boolean inverse, boolean hybrid, boolean mature, HikariDataSource ds) throws SQLException {
        String sql = SQLManager.grab_sql("verify_source_exists");
        Connection verify_con = ds.getConnection();
        PreparedStatement pstmt = verify_con.prepareStatement(sql);
        pstmt.setString(1, artist);
        pstmt.setString(2, folder);
        pstmt.setBoolean(3, inverse);
        pstmt.setBoolean(4, hybrid);
        pstmt.setBoolean(5, mature);
        ResultSet rs = pstmt.executeQuery();
        int index = 0;
        while(rs.next() && index != 1)
        {
            index++;
        }
        if(index == 1){return true;}
        else{return false;}

    }

    public static boolean verifySourceExistanceAll(String artist, boolean mature, HikariDataSource ds) throws SQLException {
        Connection obt_conn = ds.getConnection();
        String sql = SQLManager.grab_sql("verify_all_source_exists");
        PreparedStatement pstmt = obt_conn.prepareStatement(sql, ResultSet.TYPE_SCROLL_SENSITIVE,
                ResultSet.CONCUR_UPDATABLE);
        pstmt.setString(1, artist);
        pstmt.setBoolean(2,mature);
        ResultSet rs = pstmt.executeQuery();
        return mis.InvertBoolean(DBUtils.resultSetEmpty(rs));
    }


    public static HashMap<String, ArrayList<String>> addallsource(String artist, String folderid, String client_token,
                                                                  HikariDataSource ds, boolean mature,
                                                               int shard_id, String dcuuid) throws SQLException{
        HashMap<String, ArrayList<String>> source_information = new HashMap<>();
        Response allData = null;
        String p_Picture = "";
        String new_Url = "";
        allData = daParser.getAllFolder(artist, mature, client_token, 0);
        String sql = SQLManager.grab_sql("new_all_source");
        Connection all_Folder_Con = ds.getConnection();
        HashMap<String, ArrayList<String>> gathered_resources = mis.gatherGalleryFolderResources(allData);
        ArrayList<LinkedHashMap> node = allData.jsonPath().getJsonObject("results");
        Iterator<LinkedHashMap> result = node.iterator();
        source_information.put("normal-ids", new ArrayList<String>());
        boolean resultsFound = true;

        if (!(result.hasNext())) {
            resultsFound = false;
            p_Picture = "none";
        } else {
            LinkedHashMap temp_p = (LinkedHashMap) result.next();
            LinkedHashMap author = (LinkedHashMap) temp_p.get("author");
            p_Picture = (String) author.get("usericon");

        }
        if (p_Picture.equals("")) {
            p_Picture = "none";
        }
        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
        try{

        
        PreparedStatement pstmt = all_Folder_Con.prepareStatement(sql);

        pstmt.setString(1, artist);
        pstmt.setString(2,dcuuid);
        pstmt.setTimestamp(3, timestamp);
        pstmt.setTimestamp(4, timestamp);
        String img_temp_array [] = gathered_resources.get("img-urls").toArray(new String[0]);
        pstmt.setArray(5, all_Folder_Con.createArrayOf("TEXT", img_temp_array));

        if(resultsFound)
            pstmt.setString(6, "none");
        else
            pstmt.setString(6, p_Picture);

        if(resultsFound || gathered_resources.size() == 0)
            pstmt.setString(7, "none");
        else
            pstmt.setString(7, gathered_resources.get("deviation-urls").get(0));
        pstmt.setBoolean(8, mature);
        String url_temp_array [] = gathered_resources.get("deviation-urls").toArray(new String[0]);
        pstmt.setArray(9, all_Folder_Con.createArrayOf("TEXT", url_temp_array));
        String id_temp_array [] = gathered_resources.get("deviation-ids").toArray(new String[0]);
        pstmt.setArray(10, all_Folder_Con.createArrayOf("TEXT", id_temp_array));
        pstmt.setInt(11, shard_id);
        pstmt.executeUpdate();
        all_Folder_Con.commit();
        
        return source_information;
        }
        catch(SQLException e){
            all_Folder_Con.rollback();
            throw e;
        }


    }
    public static HashMap<String, ArrayList<String>> addsource(String artist, String folder, String folderid, boolean inverse, boolean hybrid, String client_token, HikariDataSource ds, boolean mature,
                                 int shard_id, String dcuuid) throws SQLException {
        HashMap<String, ArrayList<String>> source_information = new HashMap<>();
        HashMap<String, ArrayList<String>> gathered_hybrids = new HashMap<>();
        HashMap<String, ArrayList<String>> gathered_resources = new HashMap<>();
        source_information.put("normal-ids", new ArrayList<String>());
        source_information.put("hybrid-ids", new ArrayList<String>());
        Response current_data = null;
        Response hybrid_data = null;
        String new_url = "";
        String p_picture = "";
        Connection folder_con = ds.getConnection();
        //TO Add a new ID use the following below.
        //source_information.put("normal-ids", source_information.get("normal-ids").add("new id"))

        //HOW TO GET NESTED OBJECTS
        //https://stackoverflow.com/questions/14898768/how-to-access-nested-elements-of-json-object-using-getjsonarray-method
        try{
            if(inverse == false) {
                int offset = 0;
                boolean has_more = true;
                while (has_more) {
                    current_data = daParser.getGalleryFolder(artist, mature, folderid, client_token, offset);
                    has_more = current_data.jsonPath().getBoolean("has_more");
                    //This might be questionable
                    if (!(has_more))
                        break;
                    else
                        offset = current_data.jsonPath().getInt("next_offset");

                }
                if (hybrid) {
                    hybrid_data = daParser.getGalleryFolder(artist, mature, folderid, client_token, 0);
                    gathered_hybrids = mis.gatherGalleryFolderResources(hybrid_data);

                }
                String sql = SQLManager.grab_sql("new_source");
                gathered_resources = mis.gatherGalleryFolderResources(current_data);
                ArrayList<LinkedHashMap> node = current_data.jsonPath().getJsonObject("results");
                Iterator<LinkedHashMap> iterator = node.iterator();
                LinkedHashMap entry = new LinkedHashMap<>();
                if(!(iterator.hasNext())) {
                    p_picture = "none";
                } else {
                    entry = iterator.next();
                    LinkedHashMap author = (LinkedHashMap) entry.get("author");
                    p_picture = (String) author.get("usericon");

                }
                if (p_picture.equals("")) {
                    p_picture = "none";
                }
                Timestamp timestamp = new Timestamp(System.currentTimeMillis());
                if (gathered_resources.get("deviation-urls").size() == 0) {
                    new_url = null;
                } else {
                    ArrayList<String> temp_urls = gathered_resources.get("deviation-urls");
                    new_url = temp_urls.get(temp_urls.size() - 1);

                }
                
                if (hybrid){
                    PreparedStatement pstmt = folder_con.prepareStatement(sql);
                    pstmt.setString(1, artist);
                    pstmt.setString(2, folder);
                    pstmt.setString(3, folderid);
                    pstmt.setBoolean(4, inverse);
                    pstmt.setString(5,dcuuid);
                    pstmt.setTimestamp(6, timestamp);
                    pstmt.setTimestamp(7, timestamp);
                    String temp_array[] = gathered_resources.get("img-urls").toArray(new String[0]);
                    pstmt.setArray(8, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setString(9, new_url);
                    pstmt.setString(10, p_picture);
                    pstmt.setBoolean(11, mature);
                    temp_array = gathered_resources.get("deviation-urls").toArray(new String[0]);
                    pstmt.setArray(12, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_resources.get("deviation-ids").toArray(new String[0]);
                    pstmt.setArray(13, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_hybrids.get("deviation-ids").toArray(new String[0]);
                    pstmt.setArray(14, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setBoolean(15, hybrid);
                    pstmt.setInt(16, offset);
                    temp_array = gathered_hybrids.get("deviation-urls").toArray(new String[0]);
                    pstmt.setArray(17, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_hybrids.get("img-urls").toArray(new String[0]);
                    pstmt.setArray(18, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setInt(19, shard_id);
                    pstmt.executeUpdate();
                    folder_con.commit();


                }
                else{
                    PreparedStatement pstmt = folder_con.prepareStatement(sql);
                    pstmt.setString(1, artist);
                    pstmt.setString(2, folder);
                    pstmt.setString(3, folderid);
                    pstmt.setBoolean(4, inverse);
                    pstmt.setString(5,dcuuid);
                    pstmt.setTimestamp(6, timestamp);
                    pstmt.setTimestamp(7, timestamp);
                    String temp_array[] = gathered_resources.get("img-urls").toArray(new String[0]);
                    pstmt.setArray(8, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setString(9, new_url);
                    pstmt.setString(10, p_picture);
                    pstmt.setBoolean(11, mature);
                    temp_array = gathered_resources.get("deviation-urls").toArray(new String[0]);
                    pstmt.setArray(12, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_resources.get("deviation-ids").toArray(new String[0]);
                    pstmt.setArray(13, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setBoolean(14, hybrid);
                    pstmt.setInt(15, offset);
                    pstmt.setInt(16, shard_id);
                    pstmt.executeUpdate();
                }

            }
            else if(inverse)
            {
                int offset = 0;
                current_data = daParser.getGalleryFolder(artist, mature, folderid, client_token, 0);
                if(hybrid)
                {
                    boolean has_more = true;
                    while(has_more)
                    {
                        hybrid_data = daParser.getGalleryFolder(artist, mature, folderid, client_token, offset);
                        if(!(hybrid_data.jsonPath().getBoolean("has_more")))
                            break;
                        else
                            offset = hybrid_data.jsonPath().getInt("next_offset");
                    }
                    gathered_hybrids = mis.gatherGalleryFolderResources(hybrid_data);
                }
                String sql = SQLManager.grab_sql("new_source");
                gathered_resources = mis.gatherGalleryFolderResources(current_data);
                ArrayList<LinkedHashMap> node = current_data.jsonPath().getJsonObject("results");
                Iterator<LinkedHashMap> iterator = node.iterator();
                LinkedHashMap entry = new LinkedHashMap<>();
                if(!(iterator.hasNext()))  {
                    p_picture = "none";
                } else {
                    entry = iterator.next();
                    LinkedHashMap author = (LinkedHashMap) entry.get("author");
                    p_picture = (String) author.get("usericon");
                }
                if (p_picture.equals("")) {
                    p_picture = "none";
                }
                Timestamp timestamp = new Timestamp(System.currentTimeMillis());
                if (gathered_resources.get("deviation-urls").size() == 0) {
                    new_url = null;
                } else {
                    ArrayList<String> temp_urls = gathered_resources.get("deviation-urls");
                    new_url = temp_urls.get(temp_urls.size() - 1);

                }
                if (hybrid){
                    PreparedStatement pstmt = folder_con.prepareStatement(sql);
                    pstmt.setString(1, artist);
                    pstmt.setString(2, folder);
                    pstmt.setString(3, folderid);
                    pstmt.setBoolean(4, inverse);
                    pstmt.setString(5,dcuuid);
                    pstmt.setTimestamp(6, timestamp);
                    pstmt.setTimestamp(7, timestamp);
                    String temp_array[] = gathered_resources.get("img-urls").toArray(new String[0]);
                    pstmt.setArray(8, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setString(9, new_url);
                    pstmt.setString(10, p_picture);
                    pstmt.setBoolean(11, mature);
                    temp_array = gathered_resources.get("deviation-urls").toArray(new String[0]);
                    pstmt.setArray(12, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_resources.get("deviation-ids").toArray(new String[0]);
                    pstmt.setArray(13, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_hybrids.get("deviation-ids").toArray(new String[0]);
                    pstmt.setArray(14, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setBoolean(15, hybrid);
                    pstmt.setInt(16, offset);
                    temp_array = gathered_hybrids.get("deviation-urls").toArray(new String[0]);
                    pstmt.setArray(17, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_hybrids.get("img-urls").toArray(new String[0]);
                    pstmt.setArray(18, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setInt(19, shard_id);
                    pstmt.executeUpdate();
                    folder_con.commit();


                }
                else{
                    PreparedStatement pstmt = folder_con.prepareStatement(sql);
                    pstmt.setString(1, artist);
                    pstmt.setString(2, folder);
                    pstmt.setString(3, folderid);
                    pstmt.setBoolean(4, inverse);
                    pstmt.setString(5,dcuuid);
                    pstmt.setTimestamp(6, timestamp);
                    pstmt.setTimestamp(7, timestamp);
                    String temp_array[] = gathered_resources.get("img-urls").toArray(new String[0]);
                    pstmt.setArray(8, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setString(9, current_data.jsonPath().get().toString());
                    pstmt.setString(10, new_url);
                    pstmt.setString(11, p_picture);
                    pstmt.setBoolean(12, mature);
                    temp_array = gathered_resources.get("deviation-urls").toArray(new String[0]);
                    pstmt.setArray(13, folder_con.createArrayOf("TEXT", temp_array));
                    temp_array = gathered_resources.get("deviation-ids").toArray(new String[0]);
                    pstmt.setArray(14, folder_con.createArrayOf("TEXT", temp_array));
                    pstmt.setBoolean(15, hybrid);
                    pstmt.setInt(16, 0);
                    pstmt.setInt(17, shard_id);
                    pstmt.executeUpdate();
                    folder_con.commit();
                }

            }
        }
        catch(SQLException e){
            folder_con.rollback();
            throw e;
        }

        return source_information;
    }


}
