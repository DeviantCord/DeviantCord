package org.errite.deviantcord.cache;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

public class cacheManager {


    public static void addMatureHash(JedisPool given_pool, HashMap<String, Boolean> givenChannels, String givenKey){
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream out = null;
        Jedis redis = null;
        try{
            out = new ObjectOutputStream(bos);
            out.writeObject(givenChannels);
            out.flush();
            byte[] obt_bytes = bos.toByteArray();
            redis = given_pool.getResource();
            redis.hset(givenKey.getBytes(), "mature".getBytes(), obt_bytes);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        finally {
            try {
                redis.close();
                bos.close();
                out.close();

            } catch (IOException e) {
                // Lol
            }
        }
    }
    public static void addInverseHash(JedisPool given_pool, HashMap<String, Boolean> givenChannels, String givenKey){
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream out = null;
        Jedis redis = null;
        try{
            out = new ObjectOutputStream(bos);
            out.writeObject(givenChannels);
            out.flush();
            byte[] obt_bytes = bos.toByteArray();
            redis = given_pool.getResource();
            redis.hset(givenKey.getBytes(), "inverses".getBytes(), obt_bytes);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        finally {
            try {
                redis.close();
                bos.close();
                out.close();

            } catch (IOException e) {
                // Lol
            }
        }
    }
    public static void addChannelHash(JedisPool given_pool, HashMap<String, List<Long>> givenChannels, String givenKey){
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream out = null;
        Jedis redis = null;
        try{
            out = new ObjectOutputStream(bos);
            out.writeObject(givenChannels);
            out.flush();
            byte[] obt_bytes = bos.toByteArray();
            redis = given_pool.getResource();
            redis.hset(givenKey.getBytes(), "channels".getBytes(), obt_bytes);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        finally {
            try {
                redis.close();
                bos.close();
                out.close();

            } catch (IOException e) {
                // Lol
            }
        }
    }

    public static void addFolderHash(JedisPool given_pool, HashMap<String, List<String>> givenFolders, String givenKey){
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream out = null;
        Jedis redis = null;
        try{
            out = new ObjectOutputStream(bos);
            out.writeObject(givenFolders);
            out.flush();
            byte[] obt_bytes = bos.toByteArray();
            redis = given_pool.getResource();
            redis.hset(givenKey.toUpperCase().getBytes(), "folders".getBytes(), obt_bytes);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        finally {
            try {
                redis.close();
                bos.close();
                out.close();

            } catch (IOException e) {
                // Lol
            }
        }
    }
    public static void addArtistHash(JedisPool given_pool, HashSet<String> givenFolders, String givenKey){
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream out = null;
        Jedis redis = null;
        try{
            out = new ObjectOutputStream(bos);
            out.writeObject(givenFolders);
            out.flush();
            byte[] obt_bytes = bos.toByteArray();
            redis = given_pool.getResource();
            redis.hset(givenKey.toUpperCase().getBytes(), "artists".getBytes(), obt_bytes);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
        finally {
            try {
                redis.close();
                bos.close();
                out.close();

            } catch (IOException e) {
                // Lol
            }
        }
    }
}
