package org.errite.deviantcord.da;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.parsing.Parser;
import io.restassured.response.Response;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.Locale;

import static io.restassured.RestAssured.given;

public class daParser {

    public static String getToken(String id, String secret) {
        RestAssured.defaultParser = Parser.JSON;
        String url = "https://www.deviantart.com/oauth2/token?grant_type=client_credentials&client_id=" + id +
                "&client_secret=" + secret;
        Response da_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(url).
                then().contentType(ContentType.JSON).extract().response();
        return da_response.jsonPath().getString("access_token");
    }
    @Deprecated
    public static Response getStatuses(String artist, String token, int offset){
        RestAssured.defaultParser = Parser.JSON;
         String url = "https://www.deviantart.com/api/v1/oauth2/user/statuses/" + "?username=" + artist +
                 "&access_token=" + token + "&limit=10" + "&offset=" + String.valueOf(offset) + "&mature=false";

        Response da_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(url).
                then().contentType(ContentType.JSON).extract().response();
        return da_response;
    }

    public static Response getJournals(String artist, String token, boolean mature, boolean featured, int offset){
        RestAssured.defaultParser = Parser.JSON;
        String url = "https://www.deviantart.com/api/v1/oauth2/user/profile/posts?access_token=" + token +
                "&username=" + artist + "&featured=" + String.valueOf(featured) +
                "&mature_content=" + String.valueOf(mature) + "&offset=" + String.valueOf(offset);
        Response da_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(url).
                then().contentType(ContentType.JSON).extract().response();
        return da_response;
    }

    public static Response getGalleryFolder(String artist, boolean mature, String folder_id, String token, int offset) {
        String folderRequestURL = "https://www.deviantart.com/api/v1/oauth2/gallery/" + folder_id + "?username=" + artist
                + "&access_token=" + token + "&limit=10&mature_content=" + String.valueOf(mature) + "&offset=" + String.valueOf(offset);
        RestAssured.defaultParser = Parser.JSON;
        Response da_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(folderRequestURL).
                then().contentType(ContentType.JSON).extract().response();
        return da_response;
    }
    public static Response getFolders(String artist, boolean mature, String token, int offset)
    {
        String FolderRequestUrl = "https://www.deviantart.com/api/v1/oauth2/gallery/folders?access_token=" + token +
                "&username=" + artist + "&calculate_size=false&ext_preload=false&limit=10&mature_content=" + String.valueOf(mature)
                + "&offset=" + String.valueOf(offset);
        RestAssured.defaultParser = Parser.JSON;
        Response da_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(FolderRequestUrl).
                then().contentType(ContentType.JSON).extract().response();
        return da_response;

    }
    public static Response getAllFolder(String artist, boolean mature, String token, int offset){
        String folderRequestUrl = "https://www.deviantart.com/api/v1/oauth2/gallery/all?username=" + artist
                + "&access_token=" + token + "&limit=10&mature_content=" + String.valueOf(mature) + "&offset"
                + String.valueOf(offset);
        System.out.println(folderRequestUrl);
        RestAssured.defaultParser = Parser.JSON;
        Response da_response = given().headers("Content-Type", ContentType.JSON, "Accept", ContentType.JSON).
                when().get(folderRequestUrl).
                then().contentType(ContentType.JSON).extract().response();
        return da_response;
    }
    public static String getFolderUUID(String artist, String folder, String token, boolean mature)
    {
        String found_uuid = "ERROR";
        int provided_offset = 0;
        boolean found = false;
        while(!(found))
        {
            Response folder_response = getFolders(artist,mature,token,provided_offset);
            ArrayList<LinkedHashMap> msg =  folder_response.jsonPath().getJsonObject("results");

            Iterator<LinkedHashMap> iterator = msg.iterator();
            while(iterator.hasNext())
            {
                LinkedHashMap entry = iterator.next();
                String check_var = (String) entry.get("name");
                String test_lower = check_var.toLowerCase();
                if(check_var.toLowerCase().equals(folder.toLowerCase()))
                {
                    found = true;
                    found_uuid = (String) entry.get("folderid");
                    break;
                }

            }
        }
        return found_uuid;
    }

}
