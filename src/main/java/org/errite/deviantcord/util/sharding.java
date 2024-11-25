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

import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.FileReader;
import java.io.IOException;
import java.io.FileWriter;
import java.nio.channels.FileLock;
import java.nio.channels.FileChannel;
import java.nio.file.StandardOpenOption;
import java.nio.file.Path;
import java.nio.file.Paths;



public class sharding {

    public static JsonObject readShardData()
    {
        try {
            JsonObject shard_data = JsonParser.parseReader(new FileReader("shard.json")).getAsJsonObject();
            return shard_data;
        }
        catch(IOException e){
            e.printStackTrace();
            return null;
        }
        

    }

    private static synchronized void updateShardData(String category, int shard_id, int number) {
        Path path = Paths.get("shard.json");
        try (FileChannel channel = FileChannel.open(path, StandardOpenOption.READ, StandardOpenOption.WRITE);
             FileLock lock = channel.lock()) {
            
            JsonObject shard_data = readShardData();
            JsonObject category_data = shard_data.get(category).getAsJsonObject();
            category_data.addProperty(category + "-" + shard_id, shard_id);
            shard_data.add(category, category_data);

            channel.truncate(0);
            channel.position(0);
            channel.write(java.nio.ByteBuffer.wrap(shard_data.toString().getBytes()));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static int getNextShardId(String category)
    {
        JsonObject shard_data = readShardData();
        JsonObject category_data = shard_data.get(category).getAsJsonObject();
        int category_max = category_data.get(category + "-max").getAsInt();
        int least_number = category_data.get(category + "-1").getAsInt();
        int least_shared = 1;

        for(int i = 1; i <= category_max; i++)
        {
            if(category_data.get(category + "-" + i).getAsInt() < least_number)
            {
                least_number = category_data.get(category + "-" + i).getAsInt();
                least_shared = i;
            }
        }
        updateShardData(category, least_shared, least_number + 1);
        return least_shared;
    }

    
}
