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
        AtomicReference<HashMap<String, Boolean>> redisMature = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashMap<String, Boolean>> redisInverse = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashMap<String, List<String>>> redisFolders = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashMap<String, List<Long>>> redisChannels = new AtomicReference<>(new HashMap<>());
        AtomicReference<HashSet<String>> redisArtists = new AtomicReference<>(new HashSet<>());
        Connection sql_conn = ds.getConnection();
        String channel_sql = SQLManager.grab_sql("get_channels_by_server");
        PreparedStatement pstmt = sql_conn.prepareStatement(channel_sql);
        pstmt.setLong(1, checkObject.getServerId());

        //TODO check what happens what the size is when invalid artist is sent
        ResultSet rs = pstmt.executeQuery();
        InteractionMessageBuilder mb = new InteractionMessageBuilder();
        int current_index = 0;
        ArrayList<HashMap<String, String>> obt_listeners = new ArrayList<HashMap<String, String>>();
        mb.setContent("Please select the listener you want to delete");
        int index = 0;
        //TODO This current implementation will work for most people. If they have a lot of listeners then,
        // We need to figure out a way to show the listeners without hitting the character limit
        // https://stackoverflow.com/questions/47062813/how-to-get-the-size-of-a-resultset
        while(rs.next()) {
            //Declare the temporary hashmap that we will put into obt_listeners
            HashMap<String, String> temp_hmap = new HashMap<String, String>();
            //Grab information from the resultset
            long obt_id = rs.getLong("channelid");
            String artist = rs.getString("artist");
            String foldername = rs.getString("foldername");
            //Put necessary information into the Hashmap
            temp_hmap.put("artist", artist);
            temp_hmap.put("foldername", foldername);
            TextChannel obt_tc = api.getTextChannelById(obt_id).orElse(null);
            ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
            temp_hmap.put("channelname", channel_name.getName());
            temp_hmap.put("channelid", String.valueOf(obt_id));
            String responseKey = "dfFI-:-" + channel_name.getIdAsString() + "FI-:-" + artist.toUpperCase() + "FI-:-"
                    + foldername.toUpperCase();
            String buttonKey = artist + "-" + foldername + " in " + channel_name.getName();
            mb.addComponents(ActionRow.of(Button.primary(responseKey, buttonKey)));
            obt_listeners.add(temp_hmap);
            index++;
        }
        mb.setFlags(MessageFlag.EPHEMERAL);
        mb.editOriginalResponse(sci);
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
        try(Connection sql_conn = ds.getConnection();)
        {
            sql_conn.setAutoCommit(false);      
            try {

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
            sql_conn.commit();

            mci.createFollowupMessageBuilder()
                    .setContent("Deleted listener " + responseProperties.get("folder") + " for artist" + artist)
                    .send();

            }
            catch(SQLException e){
                sql_conn.rollback();
                throw new RuntimeException(e);
            }
            catch (IOException e) {
                throw new RuntimeException(e);
            }
            catch (ClassNotFoundException e) {
                throw new RuntimeException(e);
            }
        }

    }

}
