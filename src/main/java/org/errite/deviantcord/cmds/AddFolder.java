package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import io.restassured.response.Response;
import io.sentry.Sentry;
import org.errite.deviantcord.cache.cacheManager;
import org.errite.deviantcord.cache.cacheStatusManager;
import org.errite.deviantcord.checks.L2Check;
import org.errite.deviantcord.dls.DlsParser;
import org.errite.deviantcord.psql.SourceManager;
import org.errite.deviantcord.da.daParser;
import org.errite.deviantcord.psql.TaskManager;
import org.errite.deviantcord.sd.commandIdParser;
import org.errite.deviantcord.serialization.redisSerialization;
import org.errite.deviantcord.util.sharding;
import org.errite.deviantcord.types.L2CheckObject;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.ChannelType;
import org.javacord.api.entity.channel.ServerChannel;
import org.javacord.api.entity.channel.ServerTextChannel;
import org.javacord.api.entity.message.MessageBuilder;
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

import java.io.IOException;
import java.sql.*;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;


public class AddFolder {
    public static boolean useInverse = false;
    public static void setInverse(boolean inverse){useInverse = inverse;}

    public static void addfolder(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds, JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException {
        slashCommandInteraction.respondLater(true);
        Optional<SlashCommandInteractionOption> optionalArtist = slashCommandInteraction.getOptionByName("Artist");
        Optional<SlashCommandInteractionOption> optionalChannel = slashCommandInteraction.getOptionByName("Channel");
        Optional<SlashCommandInteractionOption> optionalFolderName = slashCommandInteraction.getOptionByName("Foldername");
        Optional<SlashCommandInteractionOption> optionalMature = slashCommandInteraction.getOptionByName("mature");
        String artist = "";
        ServerChannel channel = null;
        String folder_name = "";
        boolean mature = false;
        if(optionalArtist.isPresent() && optionalChannel.isPresent() && optionalFolderName.isPresent() && optionalMature.isPresent()){
            artist = optionalArtist.get().getStringValue().orElse("");
            channel = optionalChannel.get().getChannelValue().orElse(null);
            folder_name = optionalFolderName.get().getStringValue().orElse("");
            mature = optionalMature.get().getBooleanValue().orElse(false);
            if (!(channel.getType() == ChannelType.SERVER_TEXT_CHANNEL)) {
                slashCommandInteraction.createFollowupMessageBuilder()
                        .setContent("Invalid channel provided. A text channel needs to be provided")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .send();
            }
        }
        else{
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent("Missing required parameters")
                    .send();
                    return;
        }

        AtomicReference<HashMap<String, Boolean>> redisMature = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashMap<String, Boolean>> redisInverse = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashMap<String, List<String>>> redisFolders = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashMap<String, List<Long>>> redisChannels = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashSet<String>> redisArtists = new AtomicReference<>(new HashSet<>());
        L2CheckObject checkObject = L2Check.checkL2(slashCommandInteraction,ds, redis_pool, mature,
                channel, false);
        if(checkObject.isFailedCheck())
        {
            slashCommandInteraction.createImmediateResponder()
                    .setContent(checkObject.getFailureReason())
                    .setFlags(MessageFlag.EPHEMERAL)
                    .respond();
            return;
        }

        String matureKey = "";
        if(mature)
            matureKey = "M";
        else if(!(mature))
            matureKey = "S";

        String idKey = "FI-:-" + channel.getIdAsString() + "FI-:-" + artist.toUpperCase() + "FI-:-" + folder_name.toUpperCase();
        slashCommandInteraction.createFollowupMessageBuilder()
                .setFlags(MessageFlag.EPHEMERAL)
                .setContent("Should DeviantCord check for new posts at the top of the folder or the bottom of the folder?")
                .addComponents(
                        ActionRow.of(Button.success("aft" + matureKey + idKey, "Top"),
                                Button.secondary("afb" + matureKey + idKey, "Bottom")))
                .send();
        System.out.print("Reached after edit. REMOVE THIS");
    }


    public static void addFolderAction(MessageComponentInteraction messageComponentInteraction, HikariDataSource ds,
                                       JedisPool redis_pool, String da_token, 
                                       DiscordApi api)
    {
        String customId = messageComponentInteraction.getCustomId();
        HashMap<String, String> responseProperties = commandIdParser.parseNewListenerString(customId);
        String artist = responseProperties.get("artist").toUpperCase();
        String folder_name = responseProperties.get("folder").toUpperCase();
        boolean useInverse = commandIdParser.parseInverseField(responseProperties.get("inverse"));
        boolean mature = commandIdParser.parseMatureField(responseProperties.get("mature"));
        ServerTextChannel channelObj = api.getServerTextChannelById(Long.parseLong(responseProperties.get("channel"))).orElse(null);
        HashMap<String, Boolean> redisMature = new HashMap<>();
        HashMap<String, Boolean> redisInverse = new HashMap<>();
        HashMap<String, List<String>> redisFolders = new HashMap<>();
        HashMap<String, List<Long>> redisChannels = new HashMap<>();
        HashSet<String> redisArtists = new HashSet<>();


            try {
                boolean source_exists = SourceManager.verifySourceExistance(artist.toUpperCase(Locale.ROOT), folder_name.toUpperCase(Locale.ROOT),useInverse, true, mature,ds);
                String folder_uuid = daParser.getFolderUUID(artist.toUpperCase(Locale.ROOT), folder_name.toUpperCase(Locale.ROOT), da_token, mature);
                if(source_exists){
                    
                    if (mature && !channelObj.isNsfw()) {
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("This channel is not marked as NSFW, so mature content cannot be included.")
                            .setFlags(MessageFlag.EPHEMERAL)
                            .send();
                    return;
                }

                Server obtChannelServer= channelObj.getServer();
                if (messageComponentInteraction.getServer().orElse(null).getId() != obtChannelServer.getId()) {
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("The channel you selected is not in the same server as the one you used to run this command.")
                            .setFlags(MessageFlag.EPHEMERAL)
                            .send();
                    return;
                }

                List<cacheStatusManager.CacheMonitorType> missingKeys = cacheStatusManager
                            .getMissingHKeys(redis_pool, messageComponentInteraction.getServer().orElse(null).getIdAsString());
                    if(!(cacheStatusManager.needsCacheReimport(missingKeys)))
                    {
                        Jedis redis_con = redis_pool.getResource();
                        String redisKey = messageComponentInteraction.getServer().orElse(null).getIdAsString() + "-cache";
                        byte[] obt_byte_channels = redis_con.hget(redisKey.getBytes(), "channels".getBytes());
                        byte[] obt_byte_folders = redis_con.hget(redisKey.getBytes(), "folders".getBytes());
                        byte[] obt_byte_artists = redis_con.hget(redisKey.getBytes(), "artists".getBytes());
                        byte[] obt_byte_inverse = redis_con.hget(redisKey.getBytes(), "inverses".getBytes());
                        byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
                        redisChannels = redisSerialization.returnHashMapLong(obt_byte_channels);
                        redisFolders = redisSerialization.returnHashMapString(obt_byte_folders);
                        redisArtists = redisSerialization.returnHashSetString(obt_byte_artists);
                        redisInverse = redisSerialization.returnHashMapBoolean(obt_byte_inverse);
                        redisMature = redisSerialization.returnHashMapBoolean(obt_byte_mature);
                        if(!(redisArtists.contains(artist)))
                        {
                            redisArtists.add(artist);
                        }
                        if(!(redisFolders.containsKey(artist)))
                        {
                            List<String> temp_folders = new ArrayList<>();
                            temp_folders.add(folder_name);
                            redisFolders.put(artist, temp_folders);
                        }
                        else if(redisFolders.containsKey(artist))
                        {
                            List<String> temp_folders = new ArrayList<>();
                            temp_folders = redisFolders.get(artist);
                            if(!(temp_folders.contains(folder_name)))
                            {
                                temp_folders.add(folder_name);
                                redisFolders.put(artist, temp_folders);
                            }

                        }
                        String inverseKey = responseProperties.get("channel") + "FI-:-" + artist + "FI-:-" + folder_name;
                        redisInverse.put(inverseKey, useInverse);
                        redisMature.put(inverseKey, mature);

                        cacheManager.addChannelHash(redis_pool, redisChannels, redisKey);
                        cacheManager.addFolderHash(redis_pool, redisFolders,redisKey);
                        cacheManager.addArtistHash(redis_pool, redisArtists, redisKey);
                        cacheManager.addInverseHash(redis_pool, redisInverse, redisKey);
                        cacheManager.addMatureHash(redis_pool, redisMature, redisKey);
                        redis_con.close();
                    }
                    int shard_data = sharding.getNextShardId("listeners");
                    TaskManager.AddTask(messageComponentInteraction.getServer().orElse(null).getId(),
                            Long.parseLong(responseProperties.get("channel")),
                            artist.toUpperCase(Locale.ROOT),folder_uuid,folder_name,useInverse,
                            true, mature, ds, shard_data);

                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("Listener for folder " + folder_name + " from " + artist + " has been created.")
                            .send();
                    return;
                }
                else{
                    if(folder_uuid.toLowerCase().equals("none"))
                    {
                        messageComponentInteraction.createFollowupMessageBuilder()
                                .setContent("Could not find folder, is the foldername correct?")
                                .setFlags(MessageFlag.EPHEMERAL)
                                .send();
                        return;
                    }
                    List<cacheStatusManager.CacheMonitorType> missingKeys = cacheStatusManager
                            .getMissingHKeys(redis_pool, messageComponentInteraction.getServer().orElse(null).getIdAsString());
                    if(!(cacheStatusManager.needsCacheReimport(missingKeys)))
                    {
                        Jedis redis_con = redis_pool.getResource();
                        String redisKey = messageComponentInteraction.getServer().orElse(null).getIdAsString() + "-cache";
                        byte[] obt_byte_channels = redis_con.hget(redisKey.getBytes(), "channels".getBytes());
                        byte[] obt_byte_folders = redis_con.hget(redisKey.getBytes(), "folders".getBytes());
                        byte[] obt_byte_artists = redis_con.hget(redisKey.getBytes(), "artists".getBytes());
                        byte[] obt_byte_inverse = redis_con.hget(redisKey.getBytes(), "inverses".getBytes());
                        byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
                        if(obt_byte_channels != null && obt_byte_folders != null && obt_byte_artists != null && obt_byte_inverse != null && obt_byte_mature != null)
                        {
                            redisChannels = redisSerialization.returnHashMapLong(obt_byte_channels);
                            redisFolders = redisSerialization.returnHashMapString(obt_byte_folders);
                            redisArtists = redisSerialization.returnHashSetString(obt_byte_artists);
                            redisInverse = redisSerialization.returnHashMapBoolean(obt_byte_inverse);
                            redisMature = redisSerialization.returnHashMapBoolean(obt_byte_mature);
                            if(!(redisArtists.contains(artist)))
                            {
                                redisArtists.add(artist);
                            }
                            if(!(redisFolders.containsKey(artist)))
                            {
                                List<String> temp_folders = new ArrayList<>();
                                temp_folders.add(folder_name);
                                redisFolders.put(artist, temp_folders);
                            }
                            else if(redisFolders.containsKey(artist))
                            {
                                List<String> temp_folders = new ArrayList<>();
                                temp_folders = redisFolders.get(artist);
                                if(!(temp_folders.contains(folder_name)))
                                {
                                    temp_folders.add(folder_name);
                                    redisFolders.put(artist, temp_folders);
                                }

                            }
                        }
                        
                        String inverseKey = responseProperties.get("channel") + "FI-:-" + artist + "FI-:-" + folder_name;
                        redisInverse.put(inverseKey, useInverse);
                        redisMature.put(inverseKey, mature);

                        cacheManager.addChannelHash(redis_pool, redisChannels, redisKey);
                        cacheManager.addFolderHash(redis_pool, redisFolders,redisKey);
                        cacheManager.addArtistHash(redis_pool, redisArtists, redisKey);
                        cacheManager.addInverseHash(redis_pool, redisInverse, redisKey);
                        cacheManager.addMatureHash(redis_pool, redisMature, redisKey);
                        redis_con.close();
                    }
                    int shard_data = sharding.getNextShardId("sources");
                    UUID uuid = UUID.randomUUID();
                    HashMap<String, ArrayList<String>> new_source = SourceManager.addsource(artist,folder_name, folder_uuid,useInverse,true, da_token,ds,mature, shard_data, uuid.toString());
                    TaskManager.AddTask(messageComponentInteraction.getServer().orElse(null).getId(),
                            Long.parseLong(responseProperties.get("channel")), artist.toUpperCase(Locale.ROOT),folder_uuid,folder_name,useInverse, true, mature, ds, shard_data);
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("Listener for folder " + folder_name + " from " + artist + " has been created.")
                            .send();
                }
            } catch (Exception e) {
                Sentry.captureException(e);
                e.printStackTrace();
            }
    }
}
