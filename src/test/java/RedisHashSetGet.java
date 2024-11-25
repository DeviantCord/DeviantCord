import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.serialization.redisSerialization;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Properties;

public class RedisHashSetGet {

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
    public static void main(String[] args) throws IOException, ParseException, ClassNotFoundException {
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
        final JedisPoolConfig poolConfig = buildPoolConfig();
        System.out.println("Connecting to datasource at " + host + " on DB " + database_name);
        pool = new JedisPool(poolConfig, redis_host, realRedisPort, redis_username, redis_password);
        Jedis redis_con = pool.getResource();
        byte[] obt_byte_channels = redis_con.hget("575459125232795652-cache".getBytes(), "channels".getBytes());
        byte[] obt_byte_folders = redis_con.hget("575459125232795652-cache".getBytes(), "folders".getBytes());
        byte[] obt_byte_artists = redis_con.hget("575459125232795652-cache".getBytes(), "artists".getBytes());
        byte[] obt_byte_inverse = redis_con.hget("575459125232795652-cache".getBytes(), "inverses".getBytes());
        HashMap<String, List<Long>> obt_channels = redisSerialization.returnHashMapLong(obt_byte_channels);
        HashMap<String, List<String>> obt_folders = redisSerialization.returnHashMapString(obt_byte_folders);
        HashMap<String, Boolean> inverses = redisSerialization.returnHashMapBoolean(obt_byte_inverse);
        HashSet<String> obt_artists = redisSerialization.returnHashSetString(obt_byte_artists);

        System.out.println("Test Breakpoint!");
        redis_con.close();
        pool.close();

    }
}
