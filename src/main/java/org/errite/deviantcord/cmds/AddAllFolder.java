package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import io.restassured.response.Response;
import org.errite.deviantcord.cache.cacheManager;
import org.errite.deviantcord.checks.L1Check;
import org.errite.deviantcord.checks.L2Check;
import org.errite.deviantcord.da.daParser;
import org.errite.deviantcord.dls.DlsParser;
import org.errite.deviantcord.psql.SourceManager;
import org.errite.deviantcord.psql.TaskManager;
import org.errite.deviantcord.sd.commandIdParser;
import org.errite.deviantcord.serialization.redisSerialization;
import org.errite.deviantcord.types.L1CheckObject;
import org.errite.deviantcord.types.L2CheckObject;
import org.errite.deviantcord.util.sharding;
import org.javacord.api.DiscordApi;
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
import io.sentry.Sentry;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.io.IOException;
import java.sql.SQLException;
import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

import static org.errite.deviantcord.util.mis.StringToBoolean;

public class AddAllFolder {

    public static boolean useInverse = false;
    public static void addallfolder(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds, JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException
    {
        slashCommandInteraction.respondLater();
        Optional<SlashCommandInteractionOption> optionalArtist = slashCommandInteraction.getOptionByName("artist");
        Optional<SlashCommandInteractionOption> optionalChannel = slashCommandInteraction.getOptionByName("channel");
        String artist = "";
        ServerChannel channel = null;
        if (!(optionalArtist.isPresent()) && !(optionalChannel.isPresent())) {
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent("Please provide an artist name and a channel.")
                    .setFlags(MessageFlag.EPHEMERAL)
                    .send();
        }
        else if (!(optionalArtist.isPresent()) && optionalChannel.isPresent()) {
            artist = optionalArtist.get().getStringValue().orElse("");
            channel = optionalChannel.get().getChannelValue().orElse(null);
            if (artist == "")
            {
                slashCommandInteraction.createFollowupMessageBuilder()
                        .setContent("Please provide an artist name.")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .send();
            }
        }
        else if (!(optionalArtist.isPresent())) {
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent("Please provide an artist name.")
                    .setFlags(MessageFlag.EPHEMERAL)
                    .send();
        }
        else if (!(optionalChannel.isPresent())) {
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent("Please provide a channel.")
                    .setFlags(MessageFlag.EPHEMERAL)
                    .send();
        }
        L1CheckObject checkObject = L1Check.checkL1(slashCommandInteraction,ds, redis_pool);
        if(checkObject.isFailedCheck())
        {
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent(checkObject.getFailureReason())
                    .setFlags(MessageFlag.EPHEMERAL)
                    .send();
        }
        String idKey = "FI-:-" + optionalChannel.get().getChannelValue().orElse(null).getIdAsString() + 
        "FI-:-" + optionalArtist.get().getStringValue().orElse(null).toUpperCase();
        slashCommandInteraction.createFollowupMessageBuilder()
                .setContent("Should DeviantCord include content marked as mature with this listener?")
                .addComponents(
                        ActionRow.of(Button.success("aaM" + idKey, "Yes"),
                                Button.secondary("aaS" + idKey, "No")))
                .setFlags(MessageFlag.EPHEMERAL)
                .send();

            }
        public static void addAllFolderAction(MessageComponentInteraction messageComponentInteraction, HikariDataSource ds,
                                              JedisPool redis_pool, String da_token, 
                                              DiscordApi api)
        {
            String responseId = messageComponentInteraction.getCustomId();
            HashMap<String, String> responseProperties = commandIdParser.parseNewAllListenerString(responseId);
            HashMap<String, Boolean> redisMature = new HashMap<>();
            HashMap<String, Boolean> redisInverse = new HashMap<>();
            HashMap<String, List<String>> redisFolders = new HashMap<>();
            HashMap<String, List<Long>> redisChannels = new HashMap<>();
            HashSet<String> redisArtists = new HashSet<>();
            String artist = responseProperties.get("artist");
            String folder = responseProperties.get("folder");
            ServerChannel channel = api.getServerChannelById(Long.parseLong(responseProperties.get("channel"))).orElse(null);
            boolean mature = commandIdParser.parseMatureField(responseProperties.get("mature"));
            boolean source_exists = false;
            ServerTextChannel channelObj = api.getServerTextChannelById(Long.parseLong(responseProperties.get("channel"))).orElse(null);
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
            try {
                L2CheckObject afterCheckObject = L2Check.checkL2MCI(messageComponentInteraction,ds, redis_pool, mature,
                        channel,false);
                if(afterCheckObject.isFailedCheck())
                {
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent(afterCheckObject.getFailureReason())
                            .setFlags(MessageFlag.EPHEMERAL)
                            .send();
                    return;
                }
                source_exists = SourceManager.verifySourceExistanceAll(artist.toUpperCase(Locale.ROOT), mature, ds);

                if (source_exists) {
                    if (!(TaskManager.verifyAllTaskDuplicate(artist.toUpperCase(Locale.ROOT),
                            afterCheckObject.getInputServer().getId(), afterCheckObject.getGivenTextChannel().getId(), ds))) {
                        int shard_data = sharding.getNextShardId("listeners");
                        TaskManager.addAllTask(messageComponentInteraction.getServer().orElse(null).getId(),
                                Long.parseLong(responseProperties.get("channel")), artist.toUpperCase(Locale.ROOT),
                                "none", mature, ds, shard_data);
                        Jedis redis_con = redis_pool.getResource();
                        String redisKey = messageComponentInteraction.getServer().orElse(null).getIdAsString() + "-cache";
                        String folder_name = "All Folder";
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
                        String inverseKey = Long.parseLong(responseProperties.get("channel")) + "FI-:-" + artist + "FI-:-" + folder_name;
                        redisInverse.put(inverseKey, useInverse);
                        redisMature.put(inverseKey, mature);

                        cacheManager.addChannelHash(redis_pool, redisChannels, redisKey);
                        cacheManager.addFolderHash(redis_pool, redisFolders,redisKey);
                        cacheManager.addArtistHash(redis_pool, redisArtists, redisKey);
                        cacheManager.addInverseHash(redis_pool, redisInverse, redisKey);
                        cacheManager.addMatureHash(redis_pool, redisMature, redisKey);
                        redis_con.close();
                        messageComponentInteraction.createFollowupMessageBuilder()
                                .setContent("AllFolder listener has been created.")
                                .send();
                    } else {
                        messageComponentInteraction.createFollowupMessageBuilder()
                                .setContent("You already have a AllFolder listener for this channel!")
                                .setFlags(MessageFlag.EPHEMERAL)
                                .send();
                    }
                } else {
                    //If the source does not exist
                    int shard_data = sharding.getNextShardId( "sources");
                    UUID uuid = UUID.randomUUID();
                    SourceManager.addallsource(artist.toUpperCase(Locale.ROOT), "none", da_token, ds, mature,
                            shard_data, uuid.toString());
                    int listener_shard = sharding.getNextShardId("listeners");
                    TaskManager.addAllTask(afterCheckObject.getServerId(), afterCheckObject.getGivenTextChannel().getId(),
                            artist.toUpperCase(Locale.ROOT), "none", mature, ds, listener_shard);
                    Jedis redis_con = redis_pool.getResource();
                    String redisKey = messageComponentInteraction.getServer().orElse(null).getIdAsString() + "-cache";
                    String folder_name = "All Folder";
                    byte[] obt_byte_channels = redis_con.hget(redisKey.getBytes(), "channels".getBytes());
                    byte[] obt_byte_folders = redis_con.hget(redisKey.getBytes(), "folders".getBytes());
                    byte[] obt_byte_artists = redis_con.hget(redisKey.getBytes(), "artists".getBytes());
                    byte[] obt_byte_inverse = redis_con.hget(redisKey.getBytes(), "inverses".getBytes());
                    byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
                    
                    boolean found_redis_data = false;
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
                    
                    messageComponentInteraction.createFollowupMessageBuilder()
                    .setContent("AllFolder listener has been created for artist " + artist.toUpperCase(Locale.ROOT) + ".")
                    .send();
                    String inverseKey = Long.parseLong(responseProperties.get("channel")) + "FI-:-" + artist + "FI-:-" + folder_name;
                    redisInverse.put(inverseKey, useInverse);
                    redisMature.put(inverseKey, mature);

                    cacheManager.addChannelHash(redis_pool, redisChannels, redisKey);
                    cacheManager.addFolderHash(redis_pool, redisFolders,redisKey);
                    cacheManager.addArtistHash(redis_pool, redisArtists, redisKey);
                    cacheManager.addInverseHash(redis_pool, redisInverse, redisKey);
                    cacheManager.addMatureHash(redis_pool, redisMature, redisKey);
                    redis_con.close();
                }
            }
            catch (SQLException e) {
                Sentry.captureException(e);
            } catch (IOException e) {
                Sentry.captureException(e);
            } catch (ClassNotFoundException e) {
                Sentry.captureException(e);
            }
            catch (Exception e)
            {
                Sentry.captureException(e);
                messageComponentInteraction.createFollowupMessageBuilder()
                        .setContent("An error occurred while creating the AllFolder listener. It may have not been created. Use deletefolder to verify this and try again later if the issue persists.")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .send();
            }
        }
}

