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
package org.errite.deviantcord.types;

import java.util.ArrayList;

public class StatusObject {

    public StatusObject(){
        profilePic = "";
        statusIds = new ArrayList<>();
        thumbnailIds = new ArrayList<>();
        thumbnailImgUrls = new ArrayList<>();
        statusUrls = new ArrayList<>();
        excerpts = new ArrayList<>();
    }
    private String profilePic;
    private ArrayList<String> statusIds;
    private ArrayList<String> thumbnailImgUrls;
    private ArrayList<String> thumbnailIds;
    private ArrayList<String> statusUrls;
    private ArrayList<String> excerpts;

    public void setProfilePic(String url){profilePic = url;}

    public void appendStatusId(String item){statusIds.add(item);}
    public void clearStatusIds(){statusIds.clear();}
    public void appendThumbnailIds(String item){thumbnailIds.add(item);}
    public void clearThumbnailIds(){thumbnailIds.clear();}
    public void appendThumbnailImgUrls(String item){thumbnailImgUrls.add(item);}
    public void clearThumbnailUrls(){thumbnailImgUrls.clear();}
    public void appendStatusUrls(String item){statusUrls.add(item);}
    public void clearStatusUrls(){statusUrls.clear();}
    public void appendExcerpts(String item){excerpts.add(item);}
    public void clearExcerpts(){excerpts.clear();}

    public String getProfilePic(){return profilePic;}
    public ArrayList<String> getStatusIds() {
        return statusUrls;
    }


    public ArrayList<String> getExcerpts() {
        return excerpts;
    }

    public ArrayList<String> getStatusUrls() {
        return statusUrls;
    }

    public ArrayList<String> getThumbnailIds() {
        return thumbnailIds;
    }

    public ArrayList<String> getThumbnailImgUrls() {
        return thumbnailImgUrls;
    }
}
