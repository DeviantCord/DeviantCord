package org.errite.deviantcord.cache;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.util.ArrayList;
import java.util.List;

public class cacheStatusManager {

    public enum CacheMonitorType{
        ARTISTS,
        FOLDERS,
        CHANNELS,
        INVERSES,
        MATURE
    }
    public static List<CacheMonitorType> getMissingHKeys(JedisPool given_pool, String givenServerId)
    {
        List<CacheMonitorType> missing_hkeys = new ArrayList<>();
        Jedis redisCon = given_pool.getResource();
        String key = givenServerId + "-cache";
        if(redisCon.hget(key.getBytes(), "artists".getBytes()) == null)
            missing_hkeys.add(CacheMonitorType.ARTISTS);
        if(redisCon.hget(key.getBytes(), "folders".getBytes()) == null)
            missing_hkeys.add(CacheMonitorType.FOLDERS);
        if(redisCon.hget(key.getBytes(), "channels".getBytes()) == null)
            missing_hkeys.add(CacheMonitorType.CHANNELS);
        if(redisCon.hget(key.getBytes(), "inverses".getBytes()) == null)
            missing_hkeys.add(CacheMonitorType.INVERSES);
        if(redisCon.hget(key.getBytes(), "mature".getBytes()) == null)
            missing_hkeys.add(CacheMonitorType.MATURE);
        return missing_hkeys;
    }
    public static boolean needsCacheReimport(List<CacheMonitorType> missingKeys)
    {
        if(missingKeys.size() == 0)
            return false;
        else
            return true;

    }
}
