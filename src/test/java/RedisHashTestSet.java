import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.cache.cacheManager;
import org.errite.deviantcord.psql.DBUtils;
import org.javacord.api.entity.message.MessageBuilder;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Duration;
import java.util.*;

public class RedisHashTestSet {

    private static JedisPoolConfig buildPoolConfig() {
        final JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(128);
        poolConfig.setMaxIdle(128);
        poolConfig.setMinIdle(1);
        poolConfig.setTestOnBorrow(true);
        poolConfig.setTestOnReturn(true);
        poolConfig.setTestWhileIdle(true);
        poolConfig.setMinEvictableIdleTimeMillis(Duration.ofSeconds(60).toMillis());
        poolConfig.setTimeBetweenEvictionRunsMillis(Duration.ofSeconds(30).toMillis());
        poolConfig.setNumTestsPerEvictionRun(3);
        poolConfig.setBlockWhenExhausted(true);
        return poolConfig;
    }

    public static void main(String[] args) throws IOException, ParseException, SQLException {

        JedisPool pool;
        HikariDataSource ds;
        Path currentPath = Paths.get(System.getProperty("user.dir"));
        Path dbConfigPath = Paths.get(currentPath.toString(), "db.json");
        JSONParser configparser = new JSONParser();
        Object obj = configparser.parse(new FileReader(dbConfigPath.toString()));
        JSONObject jsonObject = (JSONObject) obj;
        String host = (String) jsonObject.get("database-host");
        String username = (String) jsonObject.get("database-username");
        String password = (String) jsonObject.get("database-password");
        String port = String.valueOf(jsonObject.get("database-port"));
        String database_name = (String) jsonObject.get("database-name");
        String redis_host = (String) jsonObject.get("redis_host");
        String redis_password = (String) jsonObject.get("redis_password");
        String redis_username = (String) jsonObject.get("redis_username");
        String redis_port = (String) jsonObject.get("redis_port");
        int realRedisPort = Integer.valueOf(redis_port);
        String clusterName = (String) jsonObject.get("database-cluster");
        Properties props = new Properties();

        props.setProperty("dataSourceClassName", "org.postgresql.ds.PGSimpleDataSource");
        String url = "jdbc:postgresql://" + host + "FI-:-" + port + "/" + database_name + "?options=--cluster%3D" + clusterName
                + "&sslmode=verify-full&sslrootcert=.postgresql/root.crt";

        props.setProperty("dataSource.url", url);
        props.setProperty("dataSource.user", username);
        props.setProperty("dataSource.password", password);
        HikariConfig config = new HikariConfig(props);
        System.out.println("Connecting to datasource at " + host + " on DB " + database_name);
        ds = new HikariDataSource(config);
        final JedisPoolConfig poolConfig = buildPoolConfig();
        pool = new JedisPool(poolConfig, redis_host, realRedisPort, redis_username, redis_password);
        String channel_sql = "SELECT artist, foldername, channelid, mature  from deviantcord.deviation_listeners WHERE serverid = 575459125232795652";
        Connection testcon = ds.getConnection();
        PreparedStatement pstmt = testcon.prepareStatement(channel_sql, ResultSet.TYPE_SCROLL_SENSITIVE,
                ResultSet.CONCUR_UPDATABLE);
        long test_server = 575459125232795652L;
        //TODO check what happens what the size is when invalid artist is sent
        ResultSet rs = pstmt.executeQuery();
        //Use Redis Sets and Hashes
        HashMap<String, List<String>> folders = new HashMap<>();
        HashMap<String, List<Long>> channels = new HashMap<>();
        HashSet<String> artists = new HashSet<>();
        if (DBUtils.resultSetEmpty(rs)) {
            System.out.println("Normally this would send a Discord message, saying that nothing was found " +
                    "but this is a test!");
        }

        MessageBuilder mb = new MessageBuilder();
        int mb_len = 0;
        String selectButtonText = "Please select a listener to update";
        mb_len = mb_len + selectButtonText.length();

        while (rs.next()) {
            String obt_artist = rs.getString("artist");
            String obt_folder = rs.getString("foldername");
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
            if (channels.containsKey(obt_artist + "-" + obt_folder)) {
                List<Long> temp_entry = channels.get(obt_artist + "-" + obt_folder);
                temp_entry.add(obt_channel);
                channels.put(obt_artist + "-" + obt_folder, temp_entry);
            }
            else if(!(channels.containsKey(obt_artist + "-" + obt_folder)))
            {
                List<Long> temp_entry = new ArrayList<>();
                temp_entry.add(obt_channel);
                channels.put(obt_artist + "-" + obt_folder, temp_entry);
            }


        }
        String key = String.valueOf(test_server) + "-cache";
        cacheManager.addChannelHash(pool, channels, key);
        cacheManager.addFolderHash(pool, folders,key);
        cacheManager.addArtistHash(pool, artists, key);
        testcon.close();
    }
}
