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
package org.errite.deviantcord.serialization;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.ObjectInput;
import java.io.ObjectInputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

public class redisSerialization {

    public static HashMap<String, Boolean> returnHashMapBoolean(byte[] givenData) throws IOException, ClassNotFoundException{
        ByteArrayInputStream bis = new ByteArrayInputStream(givenData);
        ObjectInput in = null;
        try {
            in = new ObjectInputStream(bis);
            Object o = in.readObject();
            HashMap<String, Boolean> test = (HashMap<String, Boolean>) o;
            return test;
        } finally {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (IOException ex) {
                // ignore close exception
            }
        }
    }
    public static HashMap<String, List<Long>> returnHashMapLong(byte[] givenData) throws IOException, ClassNotFoundException {
        ByteArrayInputStream bis = new ByteArrayInputStream(givenData);
        ObjectInput in = null;
        try {
            in = new ObjectInputStream(bis);
            Object o = in.readObject();
            HashMap<String, List<Long>> test = (HashMap<String, List<Long>>) o;
            return test;
        } finally {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (IOException ex) {
                // ignore close exception
            }
        }
    }

    public static HashMap<String, List<String>> returnHashMapString(byte[] givenData) throws IOException, ClassNotFoundException {
        ByteArrayInputStream bis = new ByteArrayInputStream(givenData);
        ObjectInput in = null;
        try {
            in = new ObjectInputStream(bis);
            Object o = in.readObject();
            HashMap<String, List<String>> test = (HashMap<String, List<String>>) o;
            return test;
        } finally {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (IOException ex) {
                // ignore close exception
            }
        }
    }
    public static HashSet<String> returnHashSetString(byte[] givenData) throws IOException, ClassNotFoundException {
        ByteArrayInputStream bis = new ByteArrayInputStream(givenData);
        ObjectInput in = null;
        try {
            in = new ObjectInputStream(bis);
            Object o = in.readObject();
            HashSet<String> test = (HashSet<String>) o;
            return test;
        } finally {
            try {
                if (in != null) {
                    in.close();
                }
            } catch (IOException ex) {
                // ignore close exception
            }
        }
    }
}
