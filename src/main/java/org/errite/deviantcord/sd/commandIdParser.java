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
package org.errite.deviantcord.sd;

import java.util.HashMap;

public class commandIdParser {


    public static String parsePageString(String given_string) { return given_string.substring(3, given_string.length()); }
    public static HashMap<String, String> parseRoleUpdateString(String given_string)
    {
        //uiFI-:-211349864133558272FI-:-Xael-TheArtistFI-:-All FolderFI-:-759461677510557726FI-:-292120646337560579
        //command
        //channel
        // artist
        //folder
        //legacy id

        HashMap<String, String> properties = new HashMap<>();
        String commandPrefix = given_string.substring(0, 2);
        properties.put("command", commandPrefix);
        //The length of the divider that indicates a new field is starting
        final int commandPrefixLen = 2;
        final int divLength = 5;
        final String div = "FI-:-";
        int index = given_string.indexOf("FI-:-", 2);
        properties.put("role", given_string.substring(index + divLength, given_string.length()));
        return properties;
    }

    public static HashMap<String, String> parseAddJournalString(String given_string) {
        HashMap<String, String> properties = new HashMap<>();
        String commandPrefix = given_string.substring(0, 2);
        properties.put("command", commandPrefix);
        properties.put("mature", given_string.substring(2,3));
        final int commandPrefixLen = 2;
        final int divLength = 5;
        final String div = "FI-:-";
        //Currently we have the command and mature field at the beginning of the string Now lets get the first
        //divider
        int index = given_string.indexOf("FI-:-", 2 +1);
        //Set the last index to the index of the first divider because now we need the second divider to find
        //where the channel field ends
        int lastIndex = index;
        index = given_string.indexOf(div, lastIndex +1);
        properties.put("channel", given_string.substring(divLength + lastIndex, index));
        lastIndex = index;
        //Now we need the third divider to find where the artist field ends
        index = given_string.indexOf(div, lastIndex +1);
        properties.put("artist", given_string.substring(lastIndex + divLength, index).toUpperCase());
        return properties;
    }

    public static HashMap<String, String> parseNewAllListenerString(String given_string)
    {
        //uiFI-:-211349864133558272FI-:-Xael-TheArtistFI-:-All FolderFI-:-759461677510557726FI-:-292120646337560579
        //command
        //channel
        // artist
        //folder
        //legacy id

        HashMap<String, String> properties = new HashMap<>();
        String commandPrefix = given_string.substring(0, 2);
        properties.put("command", commandPrefix);
        properties.put("mature", given_string.substring(2,3));
        //The length of the divider that indicates a new field is starting
        final int commandPrefixLen = 3;
        final int divLength = 5;
        final String div = "FI-:-";
        int index = given_string.indexOf("FI-:-", 5);
        properties.put("channel", given_string.substring(commandPrefixLen + divLength, index));
        int lastIndex = index;
        index = given_string.indexOf(div, lastIndex);
        properties.put("artist", given_string.substring(index + divLength, given_string.length()).toUpperCase());
        lastIndex = index + divLength;
        index = given_string.indexOf(div, lastIndex);
        properties.put("folder", "ALL FOLDER");
        //Legacy Id
        //String key = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder;
        final String legacyId = properties.get("channel") + div +  properties.get("artist") + div + properties.get("folder");
        properties.put("legacy-id", legacyId);
        return properties;
    }
    public static HashMap<String, String> parseNewListenerString(String given_string)
    {
        //uiFI-:-211349864133558272FI-:-Xael-TheArtistFI-:-All FolderFI-:-759461677510557726FI-:-292120646337560579
        //command
        //channel
        // artist
        //folder
        //legacy id

        HashMap<String, String> properties = new HashMap<>();
        String commandPrefix = given_string.substring(0, 2);
        properties.put("command", commandPrefix);
        properties.put("inverse", given_string.substring(2,3));
        properties.put("mature", given_string.substring(3,4));
        //The length of the divider that indicates a new field is starting
        final int commandPrefixLen = 4;
        final int divLength = 5;
        final String div = "FI-:-";
        int index = given_string.indexOf("FI-:-", 5);
        properties.put("channel", given_string.substring(commandPrefixLen + divLength, index));
        int lastIndex = index + divLength;
        index = given_string.indexOf(div, lastIndex);
        properties.put("artist", given_string.substring(lastIndex,index).toUpperCase());
        lastIndex = index + divLength;
        properties.put("folder", given_string.substring(lastIndex,given_string.length()).toUpperCase());
        //Legacy Id
        //String key = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder;
        final String legacyId = properties.get("channel") + div +  properties.get("artist") + div + properties.get("folder");
        properties.put("legacy-id", legacyId);
        return properties;
    }
    public static HashMap<String, String> parseNonChannelReplaceString(String given_string)
    {
        //uiFI-:-211349864133558272FI-:-Xael-TheArtistFI-:-All FolderFI-:-759461677510557726FI-:-292120646337560579
        //command
        //channel
        // artist
        //folder
        //legacy id

        HashMap<String, String> properties = new HashMap<>();
        String commandPrefix = given_string.substring(0, 2);
        properties.put("command", commandPrefix);
        //The length of the divider that indicates a new field is starting
        final int commandPrefixLen = 2;
        final int divLength = 5;
        final String div = "FI-:-";
        int index = given_string.indexOf("FI-:-", 5);
        properties.put("channel", given_string.substring(commandPrefixLen + divLength, index));
        int lastIndex = index + divLength;
        index = given_string.indexOf(div, lastIndex +1);
        properties.put("artist", given_string.substring(lastIndex,index).toUpperCase());
        lastIndex = index + divLength;
        index = given_string.indexOf(div, lastIndex +1);
        if(index == -1)
        {
            properties.put("folder", given_string.substring(lastIndex, given_string.length()).toUpperCase());
        }
        else{
            properties.put("folder", given_string.substring(lastIndex,index).toUpperCase());
            lastIndex = index;
            index = given_string.indexOf(div, lastIndex);
            //Legacy Id
            //String key = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder;
            final String legacyId = properties.get("channel") + div +  properties.get("artist") + div + properties.get("folder");
            properties.put("legacy-id", legacyId);
        }
        
        return properties;
    }
    public static HashMap<String, String> parseChannelReplaceString(String given_string)
    {
        //uiFI-:-211349864133558272FI-:-Xael-TheArtistFI-:-All FolderFI-:-759461677510557726FI-:-292120646337560579
        //command
        //channel
        // artist
        //folder
        //legacy id

        HashMap<String, String> properties = new HashMap<>();
        String commandPrefix = given_string.substring(0, 2);
        properties.put("command", commandPrefix);
        //The length of the divider that indicates a new field is starting
        final int commandPrefixLen = 2;
        final int divLength = 5;
        final String div = "FI-:-";
        int index = given_string.indexOf("FI-:-", 7);
        properties.put("channel", given_string.substring(commandPrefixLen + divLength, index));
        int lastIndex = index + divLength;
        index = given_string.indexOf(div, lastIndex);
        properties.put("artist", given_string.substring(lastIndex,index).toUpperCase());
        lastIndex = index + divLength;
        index = given_string.indexOf(div, lastIndex);
        properties.put("folder", given_string.substring(lastIndex,index).toUpperCase());
        //Legacy Id
        //String key = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder;
        final String legacyId = properties.get("channel") + div +  properties.get("artist") + div + properties.get("folder");
        properties.put("legacy-id", legacyId);
        index = index + divLength;
        properties.put("newchannel", given_string.substring(index, given_string.length()));
        return properties;
    }
    public static boolean parseInverseField(String inverseField)
    {
        if(inverseField.toUpperCase().equals("T"))
            return true;
        else if(inverseField.toUpperCase().equals("B"))
            return false;
        else
            throw new SecurityException("An invalid inverseField was received from a Discord Interaction!");
    }
    public static boolean parseMatureField(String matureField)
    {
        if(matureField.toUpperCase().equals("M"))
            return true;
        else if(matureField.toUpperCase().equals("S"))
            return false;
        else
            throw new SecurityException("An invalid matureField was received from a Discord Interaction!");
    }


}
