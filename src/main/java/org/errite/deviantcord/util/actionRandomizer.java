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

import java.util.Random;

public class actionRandomizer {

    public static String generateString()
    {
        Random rand = new Random();
        char[] chars = new char[16];
        for(int i=0;i<chars.length;i++) {
            chars[i] = (char) rand.nextInt(65536);
            if (!Character.isValidCodePoint(chars[i]))
                i--;
        }
        String s = new String(chars);
        return s;
    }
}
