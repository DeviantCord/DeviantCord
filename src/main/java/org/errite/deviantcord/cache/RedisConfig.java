package org.errite.deviantcord.cache;

import java.time.Duration;

import org.json.JSONObject;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

public class RedisConfig {
    private final JedisPool pool;
    
    public RedisConfig(JSONObject config) {
        String redisHost = (String) config.get("redis_host");
        String redisPassword = (String) config.get("redis_password");
        String redisUsername = (String) config.get("redis_username");
        int redisPort = ((Long) config.get("redis_port")).intValue();

        JedisPoolConfig poolConfig = buildPoolConfig();
        this.pool = new JedisPool(poolConfig, redisHost, redisPort, redisUsername, redisPassword);
    }
    
    public static JedisPoolConfig buildPoolConfig() {
        final JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(128);
        poolConfig.setMaxIdle(128);
        poolConfig.setMinIdle(1);
        poolConfig.setTestOnBorrow(true);
        poolConfig.setTestOnReturn(true);
        poolConfig.setTestWhileIdle(true);
        poolConfig.setMinEvictableIdleTime(Duration.ofSeconds(60));
        poolConfig.setTimeBetweenEvictionRuns(Duration.ofSeconds(30));
        poolConfig.setNumTestsPerEvictionRun(3);
        poolConfig.setBlockWhenExhausted(true);
        return poolConfig;
    }
    
    public JedisPool getPool() {
        return pool;
    }
}