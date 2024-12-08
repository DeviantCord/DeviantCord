package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import io.sentry.Sentry;
import org.errite.deviantcord.cache.cacheManager;
import org.errite.deviantcord.cache.cacheStatusManager;
import org.errite.deviantcord.checks.L1Check;
import org.errite.deviantcord.psql.DBUtils;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.serialization.redisSerialization;
import org.errite.deviantcord.types.L1CheckObject;
import org.errite.deviantcord.util.actionRandomizer;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.*;
import org.javacord.api.entity.message.MessageFlag;
import org.javacord.api.entity.message.component.ActionRow;
import org.javacord.api.entity.message.component.Button;
import org.javacord.api.entity.server.Server;
import org.javacord.api.interaction.MessageComponentInteraction;
import org.javacord.api.interaction.SlashCommandInteraction;
import org.javacord.api.interaction.SlashCommandInteractionOption;
import org.javacord.api.interaction.callback.InteractionMessageBuilder;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.exceptions.JedisConnectionException;
import org.errite.deviantcord.sd.commandIdParser;

import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.*;

public class UpdateChannel {

    public static void updatechannel(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds, JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException, IOException, ClassNotFoundException {
        //Acknowledge the bot that the message was received
        slashCommandInteraction.respondLater(true);
        //Get needed variables
        L1CheckObject checkObject = L1Check.checkL1(slashCommandInteraction, ds, redis_pool);
        if (checkObject.isFailedCheck()) {
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent(checkObject.getFailureReason())
                    .send();
            return;
        }
        Optional<SlashCommandInteractionOption> optionalChannelOption = slashCommandInteraction.getOptionByName("channel");
        //Initialize newChannel
        ServerChannel newChannel = null;
        if (optionalChannelOption.isPresent()) {
            newChannel = optionalChannelOption.get().getChannelValue().orElse(null);
            if (!(newChannel.getType() == ChannelType.SERVER_TEXT_CHANNEL)) {
                slashCommandInteraction.createFollowupMessageBuilder()
                        .setContent("Invalid channel provided. A text channel needs to be provided")
                        .send();
                return;
            }
            ServerTextChannel channelObj = api.getServerTextChannelById(newChannel.getId()).orElse(null);

            Server obtChannelServer= channelObj.getServer();
            if (slashCommandInteraction.getServer().orElse(null).getId() != obtChannelServer.getId()) {
                slashCommandInteraction.createFollowupMessageBuilder()
                        .setContent("The channel you selected is not in the same server as the one you used to run this command.")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .send();
                return;
            }
        }
            Jedis redis_check = redis_pool.getResource();
            //This Mature list hashmap tracks, which folder/listeners have mature content. This will be referenced while
            // checking whether the channel requires a NSFW enabled channel
            HashMap<String, Boolean> mature_list = new HashMap<>();
            HashMap<String, Boolean> folder_inverse = new HashMap<>();
            HashMap<String, List<String>> folders = new HashMap<>();
            HashMap<String, List<Long>> channels = new HashMap<>();
            HashSet<String> artists = new HashSet<>();
            boolean redisDown = false;
            List<cacheStatusManager.CacheMonitorType> missingKeys = new ArrayList<>();
            try {
                missingKeys = cacheStatusManager.getMissingHKeys(redis_pool, checkObject.getServerIdStr());
            } catch (JedisConnectionException ex) {
                Sentry.captureException(ex);
                redisDown = true;
            }
            InteractionMessageBuilder mb = new InteractionMessageBuilder();
            int mb_len = 0;
            mb.setContent("Please select a listener to update");
            if (cacheStatusManager.needsCacheReimport(missingKeys) || redisDown) {
                Connection testcon = ds.getConnection();
                //TODO Update get_channels to grab the artist, foldername, channelid, and the current inverse option.
                String channel_sql = SQLManager.grab_sql("grab_update_listeners");
                PreparedStatement pstmt = testcon.prepareStatement(channel_sql, ResultSet.TYPE_SCROLL_SENSITIVE,
                        ResultSet.CONCUR_UPDATABLE);
                pstmt.setLong(1, checkObject.getObtServer().getId());
                //TODO check what happens what the size is when invalid artist is sent
                ResultSet rs = pstmt.executeQuery();
                //Use Redis Sets and Hashes
                if (DBUtils.resultSetEmpty(rs)) {
                    slashCommandInteraction.createFollowupMessageBuilder()
                            .setContent("You don't have any folder listeners on this server :(")
                            .send();
                    return;
                }
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
                    String actionKey = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder + "FI-:-" + newChannel.getIdAsString();
                    String key = String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder;
                    folder_inverse.put(key, obt_inverse);


                    //TODO Have this include the artist, and folder name. As well as Current Inverse (If it doesnt look
                    // nice then omit the Inverse. Maybe use a certain color for the button and have that indicated
                    // in the message.
                    boolean obt_mature = rs.getBoolean("mature");
                    TextChannel obt_tc = api.getTextChannelById(obt_id).orElse(null);
                    ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
                    if (!(obt_tc.equals(""))) {
                        String buttonKey = obt_artist + "FI-:-" + obt_folder + " in " + channel_name.getName();
                        //Testing may be required if too many listeners exist. There is an int
                        // above that if hooked into here can be used to track the length of the buttons and the
                        // message content.
                        if (obt_mature)
                            mb.addComponents(ActionRow.of(Button.danger(actionKey, buttonKey)));
                        else
                            mb.addComponents(ActionRow.of(Button.primary(actionKey, buttonKey)));
                        mature_list.put(String.valueOf(key), obt_mature);
                    }
                }
                String key = String.valueOf(checkObject.getServerId()) + "-cache";
                if (!(redisDown)) {
                    cacheManager.addChannelHash(redis_pool, channels, key);
                    cacheManager.addFolderHash(redis_pool, folders, key);
                    cacheManager.addArtistHash(redis_pool, artists, key);
                    cacheManager.addInverseHash(redis_pool, folder_inverse, key);
                    cacheManager.addMatureHash(redis_pool, mature_list, key);
                    System.out.println("Done");
                }
                mb.editOriginalResponse(slashCommandInteraction);
                testcon.close();

            } else {
                Jedis redis_con = redis_pool.getResource();
                String redisKey = checkObject.getServerIdStr() + "-cache";
                byte[] obt_byte_channels = redis_con.hget(redisKey.getBytes(), "channels".getBytes());
                byte[] obt_byte_folders = redis_con.hget(redisKey.getBytes(), "folders".getBytes());
                byte[] obt_byte_artists = redis_con.hget(redisKey.getBytes(), "artists".getBytes());
                byte[] obt_byte_inverse = redis_con.hget(redisKey.getBytes(), "inverses".getBytes());
                byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
                if (obt_byte_channels != null && obt_byte_folders != null && obt_byte_artists != null && obt_byte_inverse != null && obt_byte_mature != null) {
                    channels = redisSerialization.returnHashMapLong(obt_byte_channels);
                    folders = redisSerialization.returnHashMapString(obt_byte_folders);
                    artists = redisSerialization.returnHashSetString(obt_byte_artists);
                    folder_inverse = redisSerialization.returnHashMapBoolean(obt_byte_inverse);
                    mature_list = redisSerialization.returnHashMapBoolean(obt_byte_mature);
                }
                HashMap<String, String> alt_properties = new HashMap<>();
                Iterator folderIterator = folders.entrySet().iterator();
                while (folderIterator.hasNext()) {
                    Map.Entry mapElement
                            = (Map.Entry) folderIterator.next();
                    List<String> obtFolders = (List<String>) mapElement.getValue();
                    for (int i = 0; i < obtFolders.size(); i++) {
                        String obtFolderName = obtFolders.get(i);
                        String obtArtist = (String) mapElement.getKey();
                        String channelKey = obtArtist + "FI-:-" + obtFolderName;
                        List<Long> obtChannels = channels.get(channelKey);
                        for (int index = 0; index < obtChannels.size(); index++) {
                            long obtId = obtChannels.get(index);
                            //String.valueOf(obt_id) + "FI-:-" + obt_artist + "FI-:-" + obt_folder + "FI-:-" + newChannel.getIdAsString();
                            String actionKey = "ucFI-:-" + String.valueOf(obtId) + "FI-:-" + obtArtist + "FI-:-" +
                                    obtFolderName + "FI-:-" + newChannel.getIdAsString();
                            String key = String.valueOf(obtId) + "FI-:-" + obtArtist + "FI-:-" + obtFolderName;
                            TextChannel obt_tc = api.getTextChannelById(obtId).orElse(null);
                            ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
                            String buttonKey = obtArtist + "-" + obtFolderName + " in " + channel_name.getName();
                            boolean obtMature = mature_list.get(key);
                            //Testing may be required if too many listeners exist. There is an int
                            // above that if hooked into here can be used to track the length of the buttons and the
                            // message content.
                            System.out.println("For UpdateChannel: Chose Action Id: " + actionKey);
                            if (obtMature)
                                mb.addComponents(ActionRow.of(Button.danger(actionKey, buttonKey)));
                            else
                                mb.addComponents(ActionRow.of(Button.primary(actionKey, buttonKey)));
                        }


                    }

                }
                mb.editOriginalResponse(slashCommandInteraction);
                redis_con.close();

            }
            HashMap<String, Boolean> finalMature_list1 = mature_list;
            HashMap<String, List<Long>> finalChannels = channels;
            HashMap<String, Boolean> finalFolder_inverse = folder_inverse;
        /*api.addMessageComponentCreateListener(event -> {
            event.

        });

         */

        }

    public static void updateChannelAction(MessageComponentInteraction messageComponentInteraction, HikariDataSource ds, JedisPool redis_pool, String da_token, DiscordApi api ) throws SQLException, IOException, ClassNotFoundException {
        messageComponentInteraction.respondLater();
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
            if (obt_byte_channels != null && obt_byte_folders != null && obt_byte_artists != null && obt_byte_inverse != null && obt_byte_mature != null) {
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
        String responseId = messageComponentInteraction.getCustomId();
        HashMap<String, String> responseProperties = new HashMap<>();
        responseProperties = commandIdParser.parseChannelReplaceString(responseId);
        String matureKey = responseProperties.get("legacy-id");
        ServerTextChannel channel = api.getTextChannelById(responseProperties.get("newchannel")).orElse(null).asServerTextChannel()
                .orElse(null);
        if(mature_list.get(matureKey))
        {
            if(!(channel.asServerTextChannel().orElse(null).isNsfw()))
            {
                messageComponentInteraction.createFollowupMessageBuilder()
                        .setContent("You can't set a mature listener to a non-nsfw channel!")
                        .send();
                return;
            }
        }
        TextChannel used_channel = messageComponentInteraction.getChannel().orElse(null);
        Connection commitcon = ds.getConnection();
        try {
            ServerTextChannel stc = used_channel.asServerTextChannel().orElse(null);
            String commit_sql = SQLManager.grab_sql("update_channel");
            PreparedStatement commit_pstmt = commitcon.prepareStatement(commit_sql);
            long testId = channel.asServerTextChannel().orElse(null).getId();
            commit_pstmt.setLong(1,channel.asServerTextChannel().orElse(null).getId());
            commit_pstmt.setLong(2, Long.valueOf(responseProperties.get("channel")));
            commit_pstmt.setString(3, responseProperties.get("folder"));
            commit_pstmt.setString(4, responseProperties.get("artist"));
            commit_pstmt.setLong(5, messageComponentInteraction.getServer().orElse(null).getId());
            commit_pstmt.executeUpdate();
            commitcon.commit();
            List<cacheStatusManager.CacheMonitorType> currentCacheStatus = cacheStatusManager.getMissingHKeys(redis_pool,
                    messageComponentInteraction.getServer().orElse(null).getIdAsString());
            if(!(cacheStatusManager.needsCacheReimport(currentCacheStatus)))
            {
                String redisKey = messageComponentInteraction.getServer().orElse(null).getIdAsString() + "-cache";
                String updateKey = responseProperties.get("artist") + "FI-:-" + responseProperties.get("folder");
                long replacedKey = Long.parseLong(responseProperties.get("channel"));
                List<Long> replaceList = channels.get(updateKey);
                int replaceIndex = replaceList.indexOf(replacedKey);
                replaceList.remove(replaceIndex);
                replaceList.add(channel.asServerTextChannel().orElse(null).getId());
                channels.put(updateKey, replaceList);
                //TODO Move this to commit the sametime as the other keys
                cacheManager.addChannelHash(redis_pool,channels, redisKey);
                String remKey = responseProperties.get("channel") + "FI-:-" + responseProperties.get("artist")
                        + "FI-:-" + responseProperties.get("folder");
                String newKey = channel.asServerTextChannel().orElse(null).getIdAsString() + "FI-:-" + responseProperties.get("artist")
                        + "FI-:-" + responseProperties.get("folder");
                boolean oldValue = mature_list.get(remKey);
                mature_list.put(newKey, oldValue);
                mature_list.remove(remKey);
                boolean oldInverse = folder_inverse.get(remKey);
                folder_inverse.remove(remKey);
                folder_inverse.put(newKey, oldInverse);
                cacheManager.addInverseHash(redis_pool, folder_inverse, redisKey);
                cacheManager.addMatureHash(redis_pool, mature_list,redisKey);
                HashMap<String, Boolean> testMatureList = new HashMap<>();
                Jedis redis_con = redis_pool.getResource();
                byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
                testMatureList = redisSerialization.returnHashMapBoolean(obt_byte_mature);
                System.out.println("Breakpoint");

            }

            messageComponentInteraction.createFollowupMessageBuilder()
                    .setContent("Listener has been updated successfully.")
                    .send();
        } catch (SQLException e) {
            commitcon.rollback();
            e.printStackTrace();
        } catch (IOException e) {
            Sentry.captureException(e);
            throw new RuntimeException(e);
        } catch (ClassNotFoundException e) {
            throw new RuntimeException(e);
        }

    }



}
