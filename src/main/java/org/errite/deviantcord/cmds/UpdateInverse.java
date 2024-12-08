package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import io.restassured.response.Response;
import io.sentry.Sentry;
import org.errite.deviantcord.cache.cacheManager;
import org.errite.deviantcord.cache.cacheStatusManager;
import org.errite.deviantcord.checks.L1Check;
import org.errite.deviantcord.dls.DlsParser;
import org.errite.deviantcord.psql.DBUtils;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.psql.SourceManager;
import org.errite.deviantcord.psql.TaskManager;
import org.errite.deviantcord.sd.commandIdParser;
import org.errite.deviantcord.serialization.redisSerialization;
import org.errite.deviantcord.types.L1CheckObject;
import org.errite.deviantcord.util.actionRandomizer;
import org.errite.deviantcord.util.mis;
import org.errite.deviantcord.util.sharding;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.ServerTextChannel;
import org.javacord.api.entity.channel.TextChannel;
import org.javacord.api.entity.message.MessageFlag;
import org.javacord.api.entity.message.component.ActionRow;
import org.javacord.api.entity.message.component.Button;
import org.javacord.api.interaction.MessageComponentInteraction;
import org.javacord.api.interaction.SlashCommandInteraction;
import org.javacord.api.interaction.callback.InteractionMessageBuilder;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.exceptions.JedisConnectionException;
import org.errite.deviantcord.sd.redisStringParser;
import java.io.IOException;
import java.sql.*;
import java.util.*;

public class UpdateInverse {

    public static void updateinverse(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds, JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException, IOException, ClassNotFoundException {
        //Acknowledge the bot that the message was received
        slashCommandInteraction.respondLater(true);
        //Get needed variables
        L1CheckObject checkObject = L1Check.checkL1(slashCommandInteraction,ds, redis_pool);
        if(checkObject.isFailedCheck())
        {
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent(checkObject.getFailureReason())
                    .send();
            return;
        }
        Jedis redis_check = redis_pool.getResource();
        //TODO Figure out deprecation
        //This Mature list hashmap tracks, which folder/listeners have mature content. This will be referenced while
        // checking whether the channel requires a NSFW enabled channel
        HashMap<String, Boolean> mature_list = new HashMap<>();
        HashMap<String, Boolean> folder_inverse = new HashMap<>();
        HashMap<String, List<String>> folders = new HashMap<>();
        HashMap<String, List<Long>> channels = new HashMap<>();
        HashSet<String> artists = new HashSet<>();
        boolean redisDown = false;
        List<cacheStatusManager.CacheMonitorType> missingKeys = new ArrayList<>();
        try{
            missingKeys = cacheStatusManager.getMissingHKeys(redis_pool, checkObject.getServerIdStr());
        }
        catch(JedisConnectionException ex)
        {
            Sentry.captureException(ex);
            redisDown = true;
        }
        InteractionMessageBuilder mb = new InteractionMessageBuilder();
        int mb_len = 0;
        mb.setContent("Please select a listener to update");
        if(cacheStatusManager.needsCacheReimport(missingKeys) || redisDown)
        {
            Connection testcon = ds.getConnection();
            //TODO Update get_channels to grab the artist, foldername, channelid, and the current inverse option.
            String channel_sql = SQLManager.grab_sql("grab_update_listeners");
            PreparedStatement pstmt = testcon.prepareStatement(channel_sql, ResultSet.TYPE_SCROLL_SENSITIVE,
                    ResultSet.CONCUR_UPDATABLE);
            pstmt.setLong(1, checkObject.getObtServer().getId());
            //TODO check what happens what the size is when invalid artist is sent
            ResultSet rs = pstmt.executeQuery();
            //Use Redis Sets and Hashes
            if(DBUtils.resultSetEmpty(rs))
            {
                slashCommandInteraction.createFollowupMessageBuilder()
                        .setContent("You don't have any folder listeners on this server :(")
                        .send();
                return;
            }
            while(rs.next())
            {
                String obt_artist = rs.getString("artist");
                String obt_folder = rs.getString("foldername").toUpperCase();
                boolean obt_inverse = rs.getBoolean("inverse");
                long obt_channel = rs.getLong("channelid");
                if(!(artists.contains(obt_artist)))
                    artists.add(obt_artist);
                if(!(obt_folder.contains(obt_artist)))
                {
                    List<String> temp_folders = new ArrayList<>();
                    temp_folders.add(obt_folder);
                    folders.put(obt_artist, temp_folders);
                }
                else if(obt_folder.contains(obt_artist))
                {
                    List<String> temp_folders = new ArrayList<>();
                    temp_folders = folders.get(obt_folder);
                    if(!(temp_folders.contains(obt_folder)))
                    {
                        temp_folders.add(obt_folder);
                        folders.put(obt_folder, temp_folders);
                    }

                }
                if(channels.containsKey(obt_artist + "FI-:-" + obt_folder))
                {
                    List<Long> temp_entry = channels.get(obt_artist + "FI-:-" + obt_folder);
                    temp_entry.add(obt_channel);
                    channels.put(obt_artist + "FI-:-" + obt_folder, temp_entry);
                }
                else if(!(channels.containsKey(obt_artist + "FI-:-" + obt_folder)))
                {
                    List<Long> temp_entry = new ArrayList<>();
                    temp_entry.add(obt_channel);
                    channels.put(obt_artist + "FI-:-" + obt_folder, temp_entry);
                }
                long obt_id = rs.getLong("channelid");
                String actionKey = "uiFI-:-" + String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder + "FI-:-";
                String key = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder;
                folder_inverse.put(key, obt_inverse);

                //TODO Have this include the artist, and folder name. As well as Current Inverse (If it doesnt look
                // nice then omit the Inverse. Maybe use a certain color for the button and have that indicated
                // in the message.
                boolean obt_mature = rs.getBoolean("mature");
                TextChannel obt_tc = api.getTextChannelById(obt_id).orElse(null);
                ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
                if(!(obt_tc.equals("")))
                {
                    String buttonKey = obt_artist + "FI-:-" + obt_folder + " in " + channel_name.getName();
                    //Testing may be required if too many listeners exist. There is an int
                    // above that if hooked into here can be used to track the length of the buttons and the
                    // message content.
                    System.out.println("For UpdateInverse: Chose Action Id: " + actionKey);
                    if(obt_mature)
                        mb.addComponents(ActionRow.of(Button.danger(actionKey, buttonKey)));
                    else
                        mb.addComponents(ActionRow.of(Button.primary(actionKey, buttonKey)));
                    mature_list.put(String.valueOf(key), obt_mature);
                }
            }
            String key = String.valueOf(checkObject.getServerId()) + "-cache";
            if(!(redisDown))
            {
                cacheManager.addChannelHash(redis_pool, channels, key);
                cacheManager.addFolderHash(redis_pool, folders,key);
                cacheManager.addArtistHash(redis_pool, artists, key);
                cacheManager.addInverseHash(redis_pool, folder_inverse, key);
                cacheManager.addMatureHash(redis_pool, mature_list, key);
            }
            mb.setFlags(MessageFlag.EPHEMERAL);
            mb.editOriginalResponse(slashCommandInteraction);
            testcon.close();

        }
        else{
            Jedis redis_con = redis_pool.getResource();
            String redisKey = checkObject.getServerIdStr() + "-cache";
            byte[] obt_byte_channels = redis_con.hget(redisKey.getBytes(), "channels".getBytes());
            byte[] obt_byte_folders = redis_con.hget(redisKey.getBytes(), "folders".getBytes());
            byte[] obt_byte_artists = redis_con.hget(redisKey.getBytes(), "artists".getBytes());
            byte[] obt_byte_inverse = redis_con.hget(redisKey.getBytes(), "inverses".getBytes());
            byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
            channels = redisSerialization.returnHashMapLong(obt_byte_channels);
            folders = redisSerialization.returnHashMapString(obt_byte_folders);
            artists = redisSerialization.returnHashSetString(obt_byte_artists);
            folder_inverse = redisSerialization.returnHashMapBoolean(obt_byte_inverse);
            mature_list = redisSerialization.returnHashMapBoolean(obt_byte_mature);
            HashMap<String, String> alt_properties = new HashMap<>();
            Iterator folderIterator = folders.entrySet().iterator();
            while(folderIterator.hasNext())
            {
                Map.Entry mapElement
                        = (Map.Entry)folderIterator.next();
                List<String> obtFolders = (List<String>) mapElement.getValue();
                for(int i = 0; i < obtFolders.size(); i++)
                {
                    String obtFolderName = obtFolders.get(i);
                    String obtArtist = (String)mapElement.getKey();
                    String channelKey = obtArtist + "FI-:-" + obtFolderName;
                    List<Long> obtChannels = channels.get(channelKey);
                    for(int index = 0; index < obtChannels.size(); index++)
                    {
                        long obtId = obtChannels.get(index);
                        String actionKey = "uiFI-:-" + String.valueOf(obtId) + "FI-:-" + obtArtist + "FI-:-" + obtFolderName
                                + "FI-:-";
                        String key = String.valueOf(obtId) + "FI-:-" + obtArtist + "FI-:-" + obtFolderName;
                        TextChannel obt_tc = api.getTextChannelById(obtId).orElse(null);
                        ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
                        String buttonKey = obtArtist + "FI-:-" + obtFolderName + " in " + channel_name.getName();
                        boolean obtMature =mature_list.get(key);
                        System.out.println("For UpdateInverse: Chose Action Id: " + actionKey);
                        //Testing may be required if too many listeners exist. There is an int
                        // above that if hooked into here can be used to track the length of the buttons and the
                        // message content.
                        if(obtMature)
                            mb.addComponents(ActionRow.of(Button.danger(actionKey, buttonKey)));
                        else
                            mb.addComponents(ActionRow.of(Button.primary(actionKey, buttonKey)));
                    }



                }

            }
            TextChannel used_channel = slashCommandInteraction.getChannel().orElse(null);
            mb.setFlags(MessageFlag.EPHEMERAL);
            mb.editOriginalResponse(slashCommandInteraction);
            redis_con.close();

        }



    }
    public static void updateInverseAction(MessageComponentInteraction messageComponentInteraction, HikariDataSource ds,
                                           JedisPool redis_pool, String da_token, 
                                           DiscordApi api) throws IOException, ClassNotFoundException, SQLException {
        HashMap<String, Boolean> mature_list = new HashMap<>();
        HashMap<String, Boolean> folder_inverse = new HashMap<>();
        HashMap<String, List<String>> folders = new HashMap<>();
        HashMap<String, List<Long>> channels = new HashMap<>();
        HashSet<String> artists = new HashSet<>();
        boolean redisDown = false;
        List<cacheStatusManager.CacheMonitorType> missingKeys = new ArrayList<>();
        try{
            missingKeys = cacheStatusManager.getMissingHKeys(redis_pool, messageComponentInteraction.getServer().orElse(null)
                    .getIdAsString());
        }
        catch(JedisConnectionException ex)
        {
            Sentry.captureException(ex);
            redisDown = true;
        }
        if(cacheStatusManager.needsCacheReimport(missingKeys) || redisDown) {
            Connection testcon = ds.getConnection();
            //TODO Update get_channels to grab the artist, foldername, channelid, and the current inverse option.
            String channel_sql = SQLManager.grab_sql("grab_update_listeners");
            PreparedStatement pstmt = testcon.prepareStatement(channel_sql, ResultSet.TYPE_SCROLL_SENSITIVE,
                    ResultSet.CONCUR_UPDATABLE);
            pstmt.setLong(1, messageComponentInteraction.getServer().orElse(null).getId());
            //TODO check what happens what the size is when invalid artist is sent
            ResultSet rs = pstmt.executeQuery();
            //Use Redis Sets and Hashes
            while (rs.next()) {
                String obt_artist = rs.getString("artist");
                String obt_folder = rs.getString("foldername");
                boolean obt_inverse = rs.getBoolean("inverse");
                long obt_channel = rs.getLong("channelid");
                if (!(artists.contains(obt_artist)))
                    artists.add(obt_artist);
                if (!(obt_folder.contains(obt_artist))) {
                    List<String> temp_folders = new ArrayList<>();
                    temp_folders.add(obt_folder);
                    folders.put(obt_artist, temp_folders);
                } else if (obt_folder.contains(obt_artist)) {
                    List<String> temp_folders = new ArrayList<>();
                    temp_folders = folders.get(obt_folder);
                    if (!(temp_folders.contains(obt_folder))) {
                        temp_folders.add(obt_folder);
                        folders.put(obt_folder, temp_folders);
                    }

                }
                if (channels.containsKey(obt_artist + "FI-:-" + obt_folder)) {
                    List<Long> temp_entry = channels.get(obt_artist + "FI-:-" + obt_folder);
                    temp_entry.add(obt_channel);
                    channels.put(obt_artist + "FI-:-" + obt_folder, temp_entry);
                } else if (!(channels.containsKey(obt_artist + "FI-:-" + obt_folder))) {
                    List<Long> temp_entry = new ArrayList<>();
                    temp_entry.add(obt_channel);
                    channels.put(obt_artist + "FI-:-" + obt_folder, temp_entry);
                }
                long obt_id = rs.getLong("channelid");
                String uuid = "FI-:-" + actionRandomizer.generateString();
                String actionKey = "ucFI-:-" + String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder +
                        "FI-:-";
                String key = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder;
                folder_inverse.put(key, obt_inverse);


                //TODO Have this include the artist, and folder name. As well as Current Inverse (If it doesnt look
                // nice then omit the Inverse. Maybe use a certain color for the button and have that indicated
                // in the message.
                boolean obt_mature = rs.getBoolean("mature");
                TextChannel obt_tc = api.getTextChannelById(obt_id).orElse(null);
                ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
                mature_list.put(String.valueOf(key), obt_mature);
            }
            String key = String.valueOf(messageComponentInteraction.getServer().orElse(null).getIdAsString()) + "-cache";
            if (!(redisDown)) {
                cacheManager.addChannelHash(redis_pool, channels, key);
                cacheManager.addFolderHash(redis_pool, folders, key);
                cacheManager.addArtistHash(redis_pool, artists, key);
                cacheManager.addInverseHash(redis_pool, folder_inverse, key);
                cacheManager.addMatureHash(redis_pool, mature_list, key);
                System.out.println("Done");
            }
        }
        else{
            Jedis redis_con = redis_pool.getResource();
            String redisKey = messageComponentInteraction.getServer().orElse(null).getIdAsString() + "-cache";
            byte[] obt_byte_channels = redis_con.hget(redisKey.getBytes(), "channels".getBytes());
            byte[] obt_byte_folders = redis_con.hget(redisKey.getBytes(), "folders".getBytes());
            byte[] obt_byte_artists = redis_con.hget(redisKey.getBytes(), "artists".getBytes());
            byte[] obt_byte_inverse = redis_con.hget(redisKey.getBytes(), "inverses".getBytes());
            byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
            if(obt_byte_channels != null && obt_byte_folders != null && obt_byte_artists != null && obt_byte_inverse != null && obt_byte_mature != null )
            {
                channels = redisSerialization.returnHashMapLong(obt_byte_channels);
                folders = redisSerialization.returnHashMapString(obt_byte_folders);
                artists = redisSerialization.returnHashSetString(obt_byte_artists);
                folder_inverse = redisSerialization.returnHashMapBoolean(obt_byte_inverse);
                mature_list = redisSerialization.returnHashMapBoolean(obt_byte_mature);
            }
            HashMap<String, String> alt_properties = new HashMap<>();
            Iterator folderIterator = folders.entrySet().iterator();
            while(folderIterator.hasNext())
            {
                Map.Entry mapElement
                        = (Map.Entry)folderIterator.next();
                List<String> obtFolders = (List<String>) mapElement.getValue();

            }
            redis_con.close();

        }
        TextChannel used_channel = messageComponentInteraction.getChannel().orElse(null);
        String responseId = messageComponentInteraction.getCustomId();
        HashMap<String, String> responseProperties = commandIdParser.parseNonChannelReplaceString(responseId);
        String inverseKey = responseProperties.get("legacy-id");
        boolean obtInverse = false;
        if(folder_inverse == null)
        {
            Connection  inverseConnection = ds.getConnection();
            String inverse_sql = SQLManager.grab_sql("grab_inverse");
            PreparedStatement inverseStatement = inverseConnection.prepareStatement(inverse_sql);
            inverseStatement.setString(1, responseProperties.get("artist"));
            inverseStatement.setString(2, responseProperties.get("folder"));
            inverseStatement.setLong(3, Long.parseLong(responseProperties.get("channel")));
            inverseStatement.setLong(4, messageComponentInteraction.getServer().orElse(null).getId());
            ResultSet inverse_rs = inverseStatement.executeQuery();
            inverse_rs.next();
            obtInverse = inverse_rs.getBoolean(1);
        }
        else{
            obtInverse = folder_inverse.get(inverseKey);
        }
        Connection commitcon = ds.getConnection();
        try{
            
            //inverse key has the same value that maturelist would need
            boolean given_inverse_exists = SourceManager.verifySourceExistance(
                    responseProperties.get("artist"), responseProperties.get("folder"), mis.InvertBoolean(obtInverse), true,
                    mature_list.get(inverseKey),ds);
            if(responseProperties.get("folder").toUpperCase().equals("ALL FOLDER"))
            {
                messageComponentInteraction.createFollowupMessageBuilder()
                        .setContent("All Folders inverse cannot be updated!")
                        .send();
                return;
            }
            if (given_inverse_exists)
            {

                String obt_sql = SQLManager.grab_sql("grab_source_dcuuid");
                PreparedStatement ReadInverseStatement = commitcon.prepareStatement(obt_sql);
                String testRemove = responseProperties.get("artist");
                ReadInverseStatement.setString(1, responseProperties.get("artist"));
                ReadInverseStatement.setString(2, responseProperties.get("folder"));
                ReadInverseStatement.setBoolean(3, obtInverse);
                //This is for the old hybrid parameter.
                ReadInverseStatement.setBoolean(4, true);
                ResultSet inverse_rs = ReadInverseStatement.executeQuery();
                inverse_rs.next();
                String dc_uuid = inverse_rs.getString(1);
                Array obt_last_ids = inverse_rs.getArray(2);
                Array obt_hybrid_ids = inverse_rs.getArray(3);
                String obt_folderid = inverse_rs.getString(4);
                String commit_sql = SQLManager.grab_sql("update_inverse");
                PreparedStatement inverseStatement = commitcon.prepareStatement(commit_sql);
                inverseStatement.setBoolean(1, mis.InvertBoolean(obtInverse));
                inverseStatement.setString(2, dc_uuid);
                inverseStatement.setArray(3, obt_last_ids);
                inverseStatement.setArray(4, obt_hybrid_ids);
                Timestamp timestamp = new Timestamp(System.currentTimeMillis());
                inverseStatement.setTimestamp(5, timestamp);
                inverseStatement.setLong(6, messageComponentInteraction.getServer().orElse(null).getId());
                inverseStatement.setLong(7, Long.parseLong(responseProperties.get("channel")));
                inverseStatement.setString(8, obt_folderid);
                inverseStatement.setString(9, "regular");
                inverseStatement.executeUpdate();
                commitcon.commit();
                List<cacheStatusManager.CacheMonitorType> currentCacheStatus = cacheStatusManager.getMissingHKeys(redis_pool,
                        messageComponentInteraction.getServer().orElse(null).getIdAsString());
                if(!(cacheStatusManager.needsCacheReimport(currentCacheStatus)))
                {
                    String hmKey = responseProperties.get("channel") + "FI-:-" + responseProperties.get("artist") +
                            "FI-:-" + responseProperties.get("folder");
                    String redisKey = messageComponentInteraction.getServer().orElse(null).getIdAsString() + "-cache";
                    folder_inverse.put(hmKey, mis.InvertBoolean(folder_inverse.get(hmKey)));
                    cacheManager.addInverseHash(redis_pool, folder_inverse, redisKey);
                }

                messageComponentInteraction.createFollowupMessageBuilder()
                        .setContent("Inverse for Listener " + responseProperties.get("folder") + " for artist "
                                + responseProperties.get("artist") + " was updated!")
                        .send();
            }
            else
            {
                int shard_data_source = sharding.getNextShardId("sources");
                int shard_data = sharding.getNextShardId("listeners");
                ServerTextChannel stc = used_channel.asServerTextChannel().orElse(null);
                String folderuuid_sql = SQLManager.grab_sql("grab_folder_uuid");
                PreparedStatement folderuuid_stmt = commitcon.prepareStatement(folderuuid_sql);
                folderuuid_stmt.setString(1, responseProperties.get("artist"));
                folderuuid_stmt.setString(2, responseProperties.get("folder"));
                ResultSet folder_rs = folderuuid_stmt.executeQuery();
                folder_rs.next();
                boolean debugBeforeFirst = folder_rs.isBeforeFirst();
                boolean debugIsFirst = folder_rs.isFirst();
                String folder_uuid = folder_rs.getString(1);
                UUID uuid = UUID.randomUUID();
                SourceManager.addsource(responseProperties.get("artist"), responseProperties.get("folder"),
                        folder_uuid, mis.InvertBoolean(obtInverse), true, da_token, ds,
                        mature_list.get(responseProperties.get("channel") + "FI-:-" + responseProperties.get("artist")
                                + "FI-:-" + responseProperties.get("folder")), shard_data_source, uuid.toString());
                TaskManager.DeleteTask(messageComponentInteraction.getServer().orElse(null).getId(), used_channel.getId(),
                        responseProperties.get("artist"),folder_uuid,
                        responseProperties.get("folder"), mature_list.get(responseProperties.get("channel") + "FI-:-" + responseProperties.get("artist")
                                + "FI-:-" + responseProperties.get("folder")), ds);
                TaskManager.AddTask(messageComponentInteraction.getServer().orElse(null).getId(), used_channel.getId(),
                        responseProperties.get("artist"), folder_uuid,
                        responseProperties.get("folder"), mis.InvertBoolean(obtInverse), true,
                        mature_list.get(responseProperties.get("channel") + "FI-:-" + responseProperties.get("artist")
                                + "FI-:-" + responseProperties.get("folder")), ds,
                        shard_data);
                //Checks to see if the keys were evicted after button is pressed. If it was evicted. Don't bother
                // pushing changes to Redis.
                List<cacheStatusManager.CacheMonitorType> currentCacheStatus = cacheStatusManager.getMissingHKeys(redis_pool,
                        messageComponentInteraction.getServer().orElse(null).getIdAsString());
                if(!(cacheStatusManager.needsCacheReimport(currentCacheStatus)))
                {
                    String hmKey = responseProperties.get("channel") + "FI-:-" + responseProperties.get("artist") +
                            "FI-:-" + responseProperties.get("folder");
                    String redisKey = String.valueOf(messageComponentInteraction.getServer().orElse(null).getId()) + "-cache";
                    folder_inverse.put(hmKey, mis.InvertBoolean(folder_inverse.get(hmKey)));
                    cacheManager.addInverseHash(redis_pool, folder_inverse, redisKey);
                }
                messageComponentInteraction.createFollowupMessageBuilder()
                        .setContent("Inverse for Listener " + responseProperties.get("folder") + " for artist "
                                + responseProperties.get("artist") + " was updated!")
                        .send();
            }

        }
        catch (SQLException e) {
            e.printStackTrace();
            commitcon.rollback();
            Sentry.captureException(e);
            messageComponentInteraction.createFollowupMessageBuilder()
                    .setContent("An error has occurred, contact DeviantCord support if this issue persists. Reference errorcode db-ui-01")
                    .send();
        }
    }
}
