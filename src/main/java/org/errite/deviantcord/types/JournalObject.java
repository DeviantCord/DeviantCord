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

public class JournalObject {
    public JournalObject(){
        profilePicture = "";
        latestTitle = "";
        titles = new ArrayList<>();
        deviationIds = new ArrayList<>();
        thumbnailIds = new ArrayList<>();
        thumbnailImgUrls = new ArrayList<>();
        journalUrls = new ArrayList<>();
        excerpts = new ArrayList<>();
    }
    private String profilePicture;

    private String latestTitle;
    private ArrayList<String> titles;
    private ArrayList<String> deviationIds;
    private ArrayList<String> thumbnailImgUrls;
    private ArrayList<String> thumbnailIds;
    private ArrayList<String> journalUrls;
    private ArrayList<String> excerpts;

    public void setLatestTitle(String given_title){latestTitle = given_title;}
    public void setProfilePicture(String item){profilePicture = item;}
    public void appendTitle(String item){titles.add(item);}
    public void clearTitles(){titles.clear();}
    public void appendDeviationId(String item){deviationIds.add(item);}
    public void clearDeviationIds(){deviationIds.clear();}
    public void appendThumbnailIds(String item){thumbnailIds.add(item);}
    public void clearThumbnailIds(){thumbnailIds.clear();}
    public void appendThumbnailImgUrls(String item){thumbnailImgUrls.add(item);}
    public void clearThumbnailUrls(){thumbnailImgUrls.clear();}
    public void appendJournalUrls(String item){journalUrls.add(item);}
    public void clearJournalUrls(){journalUrls.clear();}
    public void appendExcerpts(String item){excerpts.add(item);}
    public void clearExcerpts(){excerpts.clear();}

    public String getLatestTitle(){return latestTitle;}
    public String getProfilePicture(){ return profilePicture;}
    public ArrayList<String> getDeviationIds() {
        return deviationIds;
    }

    public ArrayList<String> getTitles() {
        return titles;
    }

    public ArrayList<String> getExcerpts() {
        return excerpts;
    }

    public ArrayList<String> getJournalUrls() {
        return journalUrls;
    }

    public ArrayList<String> getThumbnailIds() {
        return thumbnailIds;
    }

    public ArrayList<String> getThumbnailImgUrls() {
        return thumbnailImgUrls;
    }
}
