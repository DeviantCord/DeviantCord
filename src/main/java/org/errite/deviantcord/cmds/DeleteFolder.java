package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.cache.cacheManager;
import org.errite.deviantcord.checks.L1Check;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.sd.commandIdParser;
import org.errite.deviantcord.serialization.redisSerialization;
import org.errite.deviantcord.types.L1CheckObject;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.ServerTextChannel;
import org.javacord.api.entity.channel.TextChannel;
import org.javacord.api.entity.message.MessageFlag;
import org.javacord.api.entity.message.component.ActionRow;
import org.javacord.api.entity.message.component.Button;
import org.javacord.api.entity.message.embed.EmbedBuilder;
import org.javacord.api.entity.server.Server;
import org.javacord.api.interaction.MessageComponentInteraction;
import org.javacord.api.interaction.SlashCommandInteraction;
import org.javacord.api.interaction.callback.InteractionMessageBuilder;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import java.io.IOException;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;
import java.util.UUID;

public class DeleteFolder {

    public static void deletefolder(SlashCommandInteraction sci, HikariDataSource ds,
                                     JedisPool redis_pool, DiscordApi api) throws SQLException
    {
        sci.respondLater(true);
        L1CheckObject checkObject = L1Check.checkL1(sci,ds, redis_pool);
        TextChannel used_channel = sci.getChannel().orElse(null);
        if(checkObject.isFailedCheck())
        {
            sci.createFollowupMessageBuilder()
                    .setContent(checkObject.getFailureReason())
                    .send();
            return;
        }
        //Redis
        AtomicReference<HashMap<String, String>> redisKeyDirectory = new AtomicReference<>(new HashMap<>());
        ArrayList<String> redisFolders = new ArrayList<>();
        ArrayList<String> redisChannels = new ArrayList<>();
        ArrayList<String> redisArtists = new ArrayList<>();
        Connection sql_conn = ds.getConnection();
        String channel_sql = SQLManager.grab_sql("get_channels_by_server");
        PreparedStatement pstmt = sql_conn.prepareStatement(channel_sql);
        pstmt.setLong(1, checkObject.getServerId());

        ResultSet rs = pstmt.executeQuery();
        InteractionMessageBuilder mb = new InteractionMessageBuilder();
        int current_index = 0;
        ArrayList<HashMap<String, String>> obt_listeners = new ArrayList<HashMap<String, String>>();
        mb.setContent("Please select the listener you want to delete");
        int index = 0;
        UUID uuid = UUID.randomUUID();
        String uuid_string = uuid.toString();
        while(rs.next()) {

            //Declare the temporary hashmap that we will put into obt_listeners
            HashMap<String, String> temp_hmap = new HashMap<String, String>();
            //Grab information from the resultset
            long obt_id = rs.getLong("channelid");
            String artist = rs.getString("artist");
            String foldername = rs.getString("foldername");
            TextChannel obt_tc = api.getTextChannelById(obt_id).orElse(null);
            ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
            redisChannels.add(String.valueOf(obt_id));
            redisFolders.add(foldername);
            redisArtists.add(artist);

            //Put necessary information into the Hashmap
            temp_hmap.put("artist", artist);
            temp_hmap.put("foldername", foldername);
            temp_hmap.put("channelname", channel_name.getName());
            temp_hmap.put("channelid", String.valueOf(obt_id));
            if(index < 4)
            {
                String responseKey = "dfFI-:-" + channel_name.getIdAsString() + "FI-:-" + artist.toUpperCase() + "FI-:-"
                        + foldername.toUpperCase();
                String buttonKey = artist + "-" + foldername + " in " + channel_name.getName();
                mb.addComponents(ActionRow.of(Button.primary(responseKey, buttonKey)));
            }
            obt_listeners.add(temp_hmap);
            index++;
        }
        if(index > 4)
        {
            mb.addComponents(ActionRow.of(Button.primary("npFI-:-" + uuid_string + "FI-:-" +
                    String.valueOf(checkObject.getServerId()), "Next Page")));
        }
        Server obt_server = checkObject.getObtServer();
        String redisKey = obt_server.getId() + "-deletefolder-" + uuid_string + "-";
        redisKeyDirectory.get().put("current-min", redisKey + "current-min");
        redisKeyDirectory.get().put("current-max", redisKey + "current-max");
        redisKeyDirectory.get().put("channels", redisKey + "channels");
        redisKeyDirectory.get().put("folders", redisKey + "folders");
        redisKeyDirectory.get().put("artists", redisKey + "artists");
        redisKeyDirectory.get().put("max", redisKey + "max");

        Jedis redis_conn = redis_pool.getResource();
        redis_conn.setex(redisKeyDirectory.get().get("current-min"), 7200, String.valueOf(0));
        redis_conn.setex(redisKeyDirectory.get().get("current-max"), 7200, String.valueOf(3));
        redis_conn.setex(redisKeyDirectory.get().get("max"), 7200, String.valueOf(index));
        redis_conn.rpush(redisKeyDirectory.get().get("artists"), redisArtists.toArray(new String[0]));
        redis_conn.expire(redisKeyDirectory.get().get("artists"), 7200);
        redis_conn.rpush(redisKeyDirectory.get().get("folders"), redisFolders.toArray(new String[0]));
        redis_conn.expire(redisKeyDirectory.get().get("folders"), 7200);
        redis_conn.rpush(redisKeyDirectory.get().get("channels"), redisChannels.toArray(new String[0]));
        redis_conn.expire(redisKeyDirectory.get().get("channels"), 7200);
        redis_conn.hmset(redisKey + "keys", redisKeyDirectory.get());
        redis_conn.expire(redisKey + "keys", 7200);
        redis_conn.close();

        mb.setFlags(MessageFlag.EPHEMERAL);
        mb.editOriginalResponse(sci);
    }
    //TODO This needs to be implemented and the necessary changes above. The below method should grab the information
    // from Valkey and then update the previously existing message with the appropriate listeners
    // This is due to the limit on components from Discord that I was aware of.
    // Valkey should also track the current index. The command router will need to be updated both in cmds and in sd
    // for the command ID parser
    public static void nextFolderPage(MessageComponentInteraction mci, HikariDataSource ds, JedisPool redis_pool, DiscordApi api)
    {
        //mci.respondLater(true);
        //Grabbing the necessary information to interact with the main Directory Hashmap on Redis
        String responseId = mci.getCustomId();
        HashMap<String, String> obt_properties = commandIdParser.parsePageString(responseId);
        String responseServerId = obt_properties.get("serverid");
        String responseUUID = obt_properties.get("uuid");
        String redisKey = responseServerId + "-deletefolder-" + responseUUID + "-";
        String redisDirectoryKey = responseServerId + "-deletefolder-"+ responseUUID + "-keys";

        //Grab the cached information from Redis/Valkey, and put only the needed information using the current index
        // and max index
        Jedis redis_con = redis_pool.getResource();
        int current_index = Integer.parseInt(redis_con.get(redis_con.hget(redisDirectoryKey, "current-min"))) + 3;
        int max_index = Integer.parseInt(redis_con.get(redis_con.hget(redisDirectoryKey, "current-max"))) + 3;
        List<String> channels = redis_con.lrange(redis_con.hget(redisDirectoryKey, "channels"), current_index, max_index);
        List<String> folders = redis_con.lrange(redis_con.hget(redisDirectoryKey, "folders"), current_index, max_index);
        List<String> artists = redis_con.lrange(redis_con.hget(redisDirectoryKey, "artists"), current_index, max_index);
        InteractionMessageBuilder mb = new InteractionMessageBuilder();
        mb.setContent("Please select the listener you want to delete");
        int index = 0;

        for(String channel : channels)
        {
            //Iterate through the necessary information. and add the required buttons
            String artist = artists.get(index);
            String foldername = folders.get(index);
            long channel_id = Long.valueOf(channel);
            TextChannel obt_tce = api.getTextChannelById(channel_id).orElse(null);
            ServerTextChannel channel_name = obt_tce.asServerTextChannel().orElse(null);

            // We will only adding 3 listeners at a time to account for the previous and next button possibly being
            // present
            if(index < 3)
            {
                String responseKey = "dfFI-:-" + channel_name.getIdAsString() + "FI-:-" + artist.toUpperCase() + "FI-:-"
                        + foldername.toUpperCase();
                String buttonKey = artist + "-" + foldername + " in " + channel_name.getName();
                mb.addComponents(ActionRow.of(Button.primary(responseKey, buttonKey)));
            }
            index++;
        }
        if (!(max_index == Integer.parseInt(redis_con.get(redis_con.hget(redisDirectoryKey, "max")))))
            mb.addComponents(ActionRow.of(Button.primary("npFI-:-" + responseUUID + "FI-:-" + responseServerId, "Next Page")));
        redis_con.set(redis_con.hget(redisDirectoryKey, "current-min"), String.valueOf(current_index));
        redis_con.set(redis_con.hget(redisDirectoryKey, "current-max"), String.valueOf(max_index));
        redis_con.close();


        try {
            mb.addComponents(ActionRow.of(Button.primary("prFI-:-" + responseUUID + "FI-:-" + responseServerId, "Previous Page")));
            mb.setFlags(MessageFlag.EPHEMERAL);
            mb.editOriginalResponse(mci);
            System.out.println("Message sent");
        }
        catch(Exception ex)
        {
            System.out.println(ex);
        }
    }

    public static void previousFolderPage(MessageComponentInteraction mci, HikariDataSource ds, JedisPool redis_pool, DiscordApi api)
    {
        //Grabbing the necessary information to interact with the main Directory Hashmap on Redis
        String responseId = mci.getCustomId();
        HashMap<String, String> obt_properties = commandIdParser.parsePageString(responseId);
        String responseServerId = obt_properties.get("serverid");
        String responseUUID = obt_properties.get("uuid");
        String redisKey = responseServerId + "-deletefolder-" + responseUUID + "-";
        String redisDirectoryKey = responseServerId + "-deletefolder-"+ responseUUID + "-keys";

        //Grab the cached information from Redis/Valkey, and put only the needed information using the current index
        // and max index
        Jedis redis_con = redis_pool.getResource();
        int current_index = Integer.parseInt(redis_con.get(redis_con.hget(redisDirectoryKey, "current-min"))) -3;
        int max_index = Integer.parseInt(redis_con.get(redis_con.hget(redisDirectoryKey, "current-max"))) -3;
        List<String> channels = redis_con.lrange(redis_con.hget(redisDirectoryKey, "channels"), current_index, max_index);
        List<String> folders = redis_con.lrange(redis_con.hget(redisDirectoryKey, "folders"), current_index, max_index);
        List<String> artists = redis_con.lrange(redis_con.hget(redisDirectoryKey, "artists"), current_index, max_index);
        InteractionMessageBuilder mb = new InteractionMessageBuilder();
        mb.setContent("Please select the listener you want to delete");
        int index = 0;
        for(String channel : channels)
        {
            //Iterate through the necessary information. and add the required buttons
            String artist = artists.get(index);
            String foldername = folders.get(index);
            long channel_id = Long.valueOf(channel);
            TextChannel obt_tce = api.getTextChannelById(channel_id).orElse(null);
            ServerTextChannel channel_name = obt_tce.asServerTextChannel().orElse(null);

            // We will only adding 3 listeners at a time to account for the previous and next button possibly being
            // present
            if(index < 3)
            {
                String responseKey = "dfFI-:-" + channel_name.getIdAsString() + "FI-:-" + artist.toUpperCase() + "FI-:-"
                        + foldername.toUpperCase();
                String buttonKey = artist + "-" + foldername + " in " + channel_name.getName();
                mb.addComponents(ActionRow.of(Button.primary(responseKey, buttonKey)));
            }
        }
        //"prFI-:-30b1a925-cbf9-4bd4-abad-d4ae08815db0FI-:-575459125232795652"
        if (!(current_index == 0))
            mb.addComponents(ActionRow.of(Button.primary("prFI-:-" + responseUUID + "FI-:-" + responseServerId,
                    "Previous Page")));
        redis_con.set(redis_con.hget(redisDirectoryKey, "current-min"), String.valueOf(current_index));
        redis_con.set(redis_con.hget(redisDirectoryKey, "current-max"), String.valueOf(max_index));
        redis_con.close();
        mb.addComponents(ActionRow.of(Button.primary("npFI-:-" + responseUUID + "FI-:-" + responseServerId, "Next Page")));
        mb.setFlags(MessageFlag.EPHEMERAL);
        mb.editOriginalResponse(mci);

    }

    public static void deleteFolderAction(MessageComponentInteraction mci, HikariDataSource ds,
                                          JedisPool redis_pool, String da_token, 
                                          DiscordApi api) throws IOException, ClassNotFoundException, SQLException {
        //TODO NEED TO UPDATE BUTTON RESPONSE ID ABOVE

        //TODO: Limit max amount of listeners that can be shown, and add a button to show the next page of listeners
        // The extra listeners can be stored in Redis. Then the responseID can have a UUID with the Redis key to get the remaining listeners
        // This will allow us to keep the listeners in Redis, and not have to query the database for each page.
        HashMap<String, Boolean> redisMature = new HashMap<>();
        HashMap<String, Boolean> redisInverse = new HashMap<>();
        HashMap<String, List<String>> redisFolders = new HashMap<>();
        HashMap<String, List<Long>> redisChannels = new HashMap<>();
        HashSet<String> redisArtists = new HashSet<>();
        String responseId = mci.getCustomId();
        System.out.println(responseId);
        HashMap<String, String> responseProperties = commandIdParser.parseNonChannelReplaceString(responseId);
        String delete_sql = SQLManager.grab_sql("delete_listener");
        try {
            Connection sql_conn = ds.getConnection();
            PreparedStatement deletestmt = sql_conn.prepareStatement(delete_sql);
            long obt_serverid = mci.getServer().orElse(null).getId();
            deletestmt.setLong(1, obt_serverid);
            deletestmt.setString(2, responseProperties.get("artist"));
            deletestmt.setString(3, responseProperties.get("folder"));
            deletestmt.setLong(4, Long.valueOf(responseProperties.get("channel")));
            
            int rows_affected = deletestmt.executeUpdate();
            if(rows_affected == 0)
            {
                mci.createFollowupMessageBuilder()
                        .setContent("Something went wrong while deleting the listener")
                        .send();
                return;
            }
            Jedis redis_con = redis_pool.getResource();
            String redisKey = obt_serverid + "-cache";
            byte[] obt_byte_channels = redis_con.hget(redisKey.getBytes(), "channels".getBytes());
            byte[] obt_byte_folders = redis_con.hget(redisKey.getBytes(), "folders".getBytes());
            byte[] obt_byte_artists = redis_con.hget(redisKey.getBytes(), "artists".getBytes());
            byte[] obt_byte_inverse = redis_con.hget(redisKey.getBytes(), "inverses".getBytes());
            byte[] obt_byte_mature = redis_con.hget(redisKey.getBytes(), "mature".getBytes());
            boolean found_redis_data = false;
            String artist = responseProperties.get("artist");
            String inverseKey = responseProperties.get("channel") + "FI-:-" + artist + "FI-:-" +
                    responseProperties.get("folder");
            if(obt_byte_channels != null && obt_byte_folders != null && obt_byte_artists != null && obt_byte_inverse != null && obt_byte_mature != null)
            {
                redisChannels = redisSerialization.returnHashMapLong(obt_byte_channels);
                redisFolders = redisSerialization.returnHashMapString(obt_byte_folders);
                redisArtists = redisSerialization.returnHashSetString(obt_byte_artists);
                redisInverse = redisSerialization.returnHashMapBoolean(obt_byte_inverse);
                redisMature = redisSerialization.returnHashMapBoolean(obt_byte_mature);
                found_redis_data = true;
                if(redisFolders.get(artist).size() -1 == 0)
                {
                    redisFolders.remove(artist);
                    redisArtists.remove(artist);
                    redisInverse.remove(inverseKey);
                    redisMature.remove(inverseKey);
                }
                else{
                    List<String> tempFolders = redisFolders.get(artist);
                    int folderIndex = tempFolders.indexOf(responseProperties.get("folder"));
                    tempFolders.remove(folderIndex);
                    redisFolders.put(artist, tempFolders);
                    redisInverse.remove(inverseKey);
                    redisMature.remove(inverseKey);


                }
            }
            
            cacheManager.addChannelHash(redis_pool, redisChannels, redisKey);
            cacheManager.addFolderHash(redis_pool, redisFolders,redisKey);
            cacheManager.addArtistHash(redis_pool, redisArtists, redisKey);
            cacheManager.addInverseHash(redis_pool, redisInverse, redisKey);
            cacheManager.addMatureHash(redis_pool, redisMature, redisKey);

            mci.createFollowupMessageBuilder()
                    .setContent("Deleted listener " + responseProperties.get("folder") + " for artist" + artist)
                    .send();

        } catch (SQLException e) {
            throw new RuntimeException(e);
        } catch (IOException e) {
            throw new RuntimeException(e);
        } catch (ClassNotFoundException e) {
            throw new RuntimeException(e);
        }

    }
}
