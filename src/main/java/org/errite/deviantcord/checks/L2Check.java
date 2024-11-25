package org.errite.deviantcord.checks;

import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.types.L2CheckObject;
import org.javacord.api.entity.channel.ServerChannel;
import org.javacord.api.entity.permission.Role;
import org.javacord.api.interaction.MessageComponentInteraction;
import org.javacord.api.interaction.SlashCommandInteraction;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.exceptions.JedisConnectionException;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class L2Check {

    public static L2CheckObject checkL2MCI(MessageComponentInteraction slashCommandInteraction, HikariDataSource ds,
                                           JedisPool redisPool, boolean mature,
                                           ServerChannel givenChannel, boolean noMatureProp) throws SQLException {
        slashCommandInteraction.respondLater();
        L2CheckObject checkObject = new L2CheckObject();
        checkObject.setMature(mature);
        checkObject.setInteractedUser(slashCommandInteraction.getUser());
        checkObject.setObtServer(slashCommandInteraction.getServer().orElse(null));
        checkObject.setUserRoles(checkObject.getInteractedUser().getRoles(checkObject.getObtServer()));
        checkObject.setServerId(checkObject.getObtServer().getId());
        checkObject.setServerIdStr(checkObject.getObtServer().getIdAsString());
        Jedis redis = null;
        try {
            boolean foundRole = false;
            redis = redisPool.getResource();
            String obtRole = redis.get(checkObject.getServerIdStr() + "-role");

            if (obtRole != null) {
                long convertRole = Long.parseLong(obtRole);
                for (int i = 0; i < checkObject.getUserRoles().size(); i++) {

                    // Iterate over all roles

                    Role iterRole = checkObject.getUserRoles().get(i);
                    System.out.println("Iter Role Id: " + iterRole.getIdAsString() + " vs " + convertRole);
                    if (iterRole.getId() == convertRole) {
                        foundRole = true;
                        break;
                    }
                }
                if(!(foundRole))
                {
                    checkObject.setFailedCheck(true);
                    checkObject.setFailureReason("You don't have permission to use DeviantCord on this server!");
                    return checkObject;
                }

            }
            else{
                //TODO Grab the RoleId from the database, and then cache it on Redis with an Expire time of 1hour.
                boolean foundServer = false;
                String sql = SQLManager.grab_sql("grab_server_info");
                Connection testcon = ds.getConnection();
                PreparedStatement pstmt = testcon.prepareStatement(sql);
                pstmt.setLong(1, checkObject.getServerId());
                ResultSet rs = pstmt.executeQuery();
                while(rs.next())
                {
                    foundServer = true;
                    long roleId = rs.getLong("required_role");
                    redis.set(checkObject.getServerIdStr() + "-role", String.valueOf(roleId));
                    long time = 3600;
                    //Using a int instead of a long is deprecated.
                    redis.expire(checkObject.getServerIdStr() + "-role", time);
                }
                if(foundServer)
                {
                    System.out.println(obtRole);
                    long convertRole = Long.parseLong(obtRole);
                    for (int i = 0; i < checkObject.getUserRoles().size(); i++) {

                        // Iterate over all roles

                        Role iterRole = checkObject.getUserRoles().get(i);
                        if (iterRole.getId() == convertRole) {
                            foundRole = true;
                            break;
                        }
                    }
                    if(!(foundRole))
                    {
                        checkObject.setFailedCheck(true);
                        checkObject.setFailureReason("Fail to find Role to check. Setup has not yet been run!");
                        return checkObject;
                    }

                }
                else{
                    checkObject.setFailedCheck(true);
                    checkObject.setFailureReason("Fail to find Role to check. Setup has not yet been run!");
                    return checkObject;
                }


            }
            checkObject.setInputServer(givenChannel.getServer());
            checkObject.setGivenTextChannel(givenChannel.asServerTextChannel().orElse(null));
            if(!(checkObject.getServerId() == checkObject.getInputServer().getId()))
            {
                checkObject.setFailedCheck(true);
                checkObject.setFailureReason("Channel given is not on the server the command was called from!");
                return checkObject;
            }
            boolean skipExtMatureCheck = false;
            if(!(noMatureProp))
            {
                if(checkObject.getGivenTextChannel().isNsfw() && (!(checkObject.isMature())))
                    skipExtMatureCheck = true;
                if(!(skipExtMatureCheck))
                {
                    if(!(checkObject.isMature() == checkObject.getGivenTextChannel().isNsfw()))
                    {
                        checkObject.setFailedCheck(true);
                        checkObject.setFailureReason("Channel given failed NSFW check!");
                        return checkObject;
                    }
                }
            }

        }

        catch (JedisConnectionException | SQLException e)
        {
            if (redis != null)
            {
                redisPool.returnBrokenResource(redis);
                redis = null;
            }
            throw e;
        }
        finally
        {
            if (redis != null)
            {
                redisPool.returnResource(redis);
            }
        }
        return checkObject;
    }
    public static L2CheckObject checkL2(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds,
                                        JedisPool redisPool, boolean mature,
                                        ServerChannel givenChannel, boolean noMatureProp) throws SQLException {
        slashCommandInteraction.respondLater();
        L2CheckObject checkObject = new L2CheckObject();
        checkObject.setMature(mature);
        checkObject.setInteractedUser(slashCommandInteraction.getUser());
        checkObject.setObtServer(slashCommandInteraction.getServer().orElse(null));
        checkObject.setUserRoles(checkObject.getInteractedUser().getRoles(checkObject.getObtServer()));
        checkObject.setServerId(checkObject.getObtServer().getId());
        checkObject.setServerIdStr(checkObject.getObtServer().getIdAsString());
        Jedis redis = null;
        try {
            boolean foundRole = false;
            redis = redisPool.getResource();
            String obtRole = redis.get(checkObject.getServerIdStr() + "-role");

            if (obtRole != null) {
                long convertRole = Long.parseLong(obtRole);
                for (int i = 0; i < checkObject.getUserRoles().size(); i++) {

                    // Iterate over all roles

                    Role iterRole = checkObject.getUserRoles().get(i);
                    System.out.println("Iter Role Id: " + iterRole.getIdAsString() + " vs " + convertRole);
                    if (iterRole.getId() == convertRole) {
                        foundRole = true;
                        break;
                    }
                }
                if(!(foundRole))
                {
                    checkObject.setFailedCheck(true);
                    checkObject.setFailureReason("You don't have permission to use DeviantCord on this server!");
                    return checkObject;
                }

            }
            else{
                //TODO Grab the RoleId from the database, and then cache it on Redis with an Expire time of 1hour.
                boolean foundServer = false;
                String sql = SQLManager.grab_sql("grab_server_info");
                Connection testcon = ds.getConnection();
                PreparedStatement pstmt = testcon.prepareStatement(sql);
                pstmt.setLong(1, checkObject.getServerId());
                ResultSet rs = pstmt.executeQuery();
                while(rs.next())
                {
                    foundServer = true;
                    long roleId = rs.getLong("required_role");
                    obtRole = String.valueOf(roleId);
                    redis.set(checkObject.getServerIdStr() + "-role", String.valueOf(roleId));
                    long time = 3600;
                    //Using a int instead of a long is deprecated.
                    redis.expire(checkObject.getServerIdStr() + "-role", time);
                }
                if(foundServer)
                {
                    System.out.println(obtRole);
                    long convertRole = Long.parseLong(obtRole);
                    for (int i = 0; i < checkObject.getUserRoles().size(); i++) {

                        // Iterate over all roles

                        Role iterRole = checkObject.getUserRoles().get(i);
                        if (iterRole.getId() == convertRole) {
                            foundRole = true;
                            break;
                        }
                    }
                    if(!(foundRole))
                    {
                        checkObject.setFailedCheck(true);
                        checkObject.setFailureReason("Fail to find Role to check. Setup has not yet been run!");
                        return checkObject;
                    }

                }
                else{
                    checkObject.setFailedCheck(true);
                    checkObject.setFailureReason("Fail to find Role to check. Setup has not yet been run!");
                    return checkObject;
                }


            }
            checkObject.setInputServer(givenChannel.getServer());
            checkObject.setGivenTextChannel(givenChannel.asServerTextChannel().orElse(null));
            if(!(checkObject.getServerId() == checkObject.getInputServer().getId()))
            {
                checkObject.setFailedCheck(true);
                checkObject.setFailureReason("Channel given is not on the server the command was called from!");
                return checkObject;
            }
            boolean skipExtMatureCheck = false;
            if(!(noMatureProp))
            {
                if(checkObject.getGivenTextChannel().isNsfw() && (!(checkObject.isMature())))
                    skipExtMatureCheck = true;
                if(!(skipExtMatureCheck))
                {
                    if(!(checkObject.isMature() == checkObject.getGivenTextChannel().isNsfw()))
                    {
                        checkObject.setFailedCheck(true);
                        checkObject.setFailureReason("Channel given failed NSFW check!");
                        return checkObject;
                    }
                }
            }

        }

        catch (JedisConnectionException | SQLException e)
        {
            if (redis != null)
            {
                redisPool.returnBrokenResource(redis);
                redis = null;
            }
            throw e;
        }
        finally
        {
            if (redis != null)
            {
                redisPool.returnResource(redis);
            }
        }
        return checkObject;
    }
}
