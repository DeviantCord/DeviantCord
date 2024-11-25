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

public class redisStringParser {

    @Deprecated
    public static HashMap<String, String> parseRedisString(String given_string)
    {
        HashMap<String, String> properties = new HashMap<>();
        int index = given_string.indexOf("FI-:-");
        properties.put("channel", given_string.substring(0, index));
        int lastIndex = index;
        index = given_string.indexOf("FI-:-",index + 8);
        properties.put("artist", given_string.substring(lastIndex +8, index).toUpperCase());
        int idIndex = given_string.indexOf("FI-:-");
        properties.put("folder", given_string.substring(index + 8, idIndex).toUpperCase());
        properties.put("legacy-id", given_string.substring(0, idIndex));
        return properties;
    }
}
