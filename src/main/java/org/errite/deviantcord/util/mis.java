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
package org.errite.deviantcord.util;

import io.restassured.response.Response;
import org.errite.deviantcord.types.JournalObject;
import org.errite.deviantcord.types.StatusObject;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import java.sql.ResultSet;
import java.util.*;

public class mis {


    public static StatusObject gatherStatuses(Response data){
        StatusObject obtStatuses = new StatusObject();
        ArrayList<LinkedHashMap> node = data.jsonPath().getJsonObject("results");
        Iterator<LinkedHashMap> iterator = node.iterator();
        int currentIndex = 0;
        while(iterator.hasNext()){
            LinkedHashMap entry = iterator.next();
            if(currentIndex == 0){
                LinkedHashMap author = (LinkedHashMap) entry.get("author");
                String userIcon = (String)author.get("usericon");
                if(!(Objects.isNull(userIcon)))
                    obtStatuses.setProfilePic(userIcon);
                else
                    obtStatuses.setProfilePic("none");
            }
            boolean foundThumb = false;
            obtStatuses.appendStatusId((String) entry.get("statusid"));
            obtStatuses.appendStatusUrls((String) entry.get("url"));
            obtStatuses.appendExcerpts((String) entry.get("body"));
            ArrayList items = (ArrayList) entry.get("items") ;
            //TODO put back type variable, if needed
            //LinkedHashMap check_var = (LinkedHashMap) entry.get("type");
            if(!(items.size() == 0)) {
                System.out.println("This is a breakpoint used to check what is going on");
                /*
                LinkedHashMap preview = (LinkedHashMap) items.get("preview");
                LinkedHashMap deviation = (LinkedHashMap) items.get("deviation");
                obtStatuses.appendThumbnailIds((String) deviation.get("deviationid"));
                obtStatuses.appendThumbnailImgUrls((String) preview.get("src"));

                 */
            }
            else{
                obtStatuses.appendThumbnailIds("none");
                obtStatuses.appendThumbnailImgUrls("none");
            }
            ++currentIndex;
        }
        return obtStatuses;
    }
    public static JournalObject gatherJournals(Response data){
        JournalObject obtJournals = new JournalObject();
        ArrayList<LinkedHashMap> node = data.jsonPath().getJsonObject("results");
        Iterator<LinkedHashMap> iterator = node.iterator();
        int currentIndex = 0;
        while(iterator.hasNext()){
            LinkedHashMap entry = iterator.next();
            if(currentIndex == 0)
            {
                obtJournals.setLatestTitle((String) entry.get("title"));
                LinkedHashMap author = (LinkedHashMap) entry.get("author");
                String userIcon = (String)author.get("usericon");
                if(!(Objects.isNull(userIcon)))
                    obtJournals.setProfilePicture(userIcon);
                else
                    obtJournals.setProfilePicture("none");
            }
            
            boolean foundThumb = false;
            obtJournals.appendExcerpts((String)entry.get("excerpt"));
            obtJournals.appendDeviationId((String)entry.get("deviationid"));
            obtJournals.appendJournalUrls((String)entry.get("url"));
            obtJournals.appendTitle((String) entry.get("title"));
            //TODO TEST HERE
            ArrayList<LinkedHashMap> check_var = (ArrayList<LinkedHashMap>) entry.get("thumbs");
            //TODO CHANGE THIS to check for SIZE
            if(!(check_var.size() == 0))
            {
                LinkedHashMap cont = check_var.get(0);
                UUID uuid = UUID.randomUUID();
                obtJournals.appendThumbnailIds(uuid.toString());
                obtJournals.appendThumbnailImgUrls((String)cont.get("src"));

            }
            else{
                obtJournals.appendThumbnailIds("none");
                obtJournals.appendThumbnailImgUrls("none");
            }
            currentIndex++;
        }
        return obtJournals;
    }
    public static HashMap<String, ArrayList<String>> gatherGalleryFolderResources(Response data){
        HashMap<String, ArrayList<String>> data_resources = new HashMap<>();
        data_resources.put("deviation-ids", new ArrayList<String>());
        data_resources.put("deviation-urls", new ArrayList<String>());
        data_resources.put("img-urls", new ArrayList<String>());
        data.jsonPath().getJsonObject("results");
        ArrayList<LinkedHashMap> msg =  data.jsonPath().getJsonObject("results");
        Iterator<LinkedHashMap> iterator = msg.iterator();
        while(iterator.hasNext())
        {
            LinkedHashMap entry = iterator.next();
            String check_var = (String) entry.get("excerpt");
            ArrayList<String> ids = data_resources.get("deviation-ids");
            ArrayList<String> dev_urls = data_resources.get("deviation-urls");
            dev_urls.add((String)entry.get("url"));
            ids.add((String)entry.get("deviationid"));

            if(Objects.isNull(check_var)) {
                    LinkedHashMap cont = (LinkedHashMap) entry.get("content");
                    String src = (String) cont.get("src");
                    ArrayList<String> urls = data_resources.get("img-urls");
                    urls.add(src);
                    data_resources.put("img-urls", urls);
                 if(Objects.isNull(cont)) {
                    cont = (LinkedHashMap) entry.get("flash");
                    src = (String) cont.get("src");
                    urls = data_resources.get("img-urls");
                    urls.add(src + "DEVIANTCORDENDINGUSENONPREVIEW");
                    data_resources.put("img-urls", urls);
                     if (Objects.isNull(cont)) {
                        LinkedHashMap videos = (LinkedHashMap) entry.get("videos");
                        src = (String) videos.get("src");
                        urls = data_resources.get("img-urls");
                        urls.add(src + "DEVIANTCORDENDINGUSENONPREVIEW");
                        data_resources.put("img-urls", urls);
                        if (Objects.isNull(videos)) {
                            cont = (LinkedHashMap) entry.get("thumbs");
                            src = (String) cont.get("src");
                            urls = data_resources.get("img-urls");
                            urls.add(src);
                            data_resources.put("img-urls", urls);
                             if(Objects.isNull(cont)) {
                                urls = data_resources.get("img-urls");
                                urls.add("IGNORETHISDEVIATION");
                                data_resources.put("img-urls", urls);
                            }

                        }

                    }

                }
            }


        }
        return data_resources;
    }

    public static boolean InvertBoolean(boolean given_boolean){
        if(given_boolean == true)
            return false;
        else
            return true;
    }
    public static boolean StringToBoolean(String input)
    {
        if(input.toUpperCase().equals("TRUE"))
            return true;
        else if (input.toUpperCase().equals("FALSE"))
            return false;
        else
            return false;
    }
}
