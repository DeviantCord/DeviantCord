package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.sd.commandIdParser;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.TextChannel;
import org.javacord.api.entity.message.MessageBuilder;
import org.javacord.api.entity.message.component.ActionRow;
import org.javacord.api.entity.message.component.Button;
import org.javacord.api.entity.permission.Role;
import org.javacord.api.entity.server.Server;
import org.javacord.api.interaction.MessageComponentInteraction;
import org.javacord.api.interaction.SlashCommandInteraction;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import org.javacord.api.entity.message.MessageFlag;
import org.javacord.api.interaction.callback.InteractionImmediateResponseBuilder;
import org.javacord.api.entity.message.embed.EmbedBuilder;
import org.javacord.api.interaction.SlashCommandInteractionOption;
import io.sentry.Sentry;
import java.util.Optional;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.List;


public class setupRole {

    public static void setuprole(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds, JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException{
        Server obt_server = slashCommandInteraction.getServer().orElse(null);
        TextChannel used_channel = slashCommandInteraction.getChannel().orElse(null);
        Optional<SlashCommandInteractionOption> optionalRole = slashCommandInteraction.getOptionByName("Role");
        if(obt_server.isAdmin(slashCommandInteraction.getUser()))
        {
            List<Role> obt_roles = obt_server.getRoles();
            if(obt_roles.size() == 0)
            {
                slashCommandInteraction.createImmediateResponder()
                    .setContent("There are no roles on this server!")
                    .setFlags(MessageFlag.EPHEMERAL)
                    .respond();
                return;
            }

            if(!(optionalRole.get().getRoleValue().orElse(null).equals(null)))
            {
                slashCommandInteraction.respondLater();
                long roleId = optionalRole.get().getRoleValue().orElse(null).getId();
                long roleIdServer = optionalRole.get().getRoleValue().orElse(null).getServer().getId();
                long slashCommandServerId = slashCommandInteraction.getServer().orElse(null).getId();
                Connection srConnection = ds.getConnection();
                if(roleIdServer == slashCommandServerId)
                {
                    try {
                        Jedis redis = redis_pool.getResource();
                        redis.set(String.valueOf(slashCommandServerId)+ "-role", String.valueOf(roleId));
                        long time = 3600;
                        //Using a int instead of a long is deprecated.
                        redis.expire(String.valueOf(slashCommandServerId)+ "-role", time);
                        redis.close();
                        String sql = SQLManager.grab_sql("update_rank");
                        PreparedStatement pstmt = srConnection.prepareStatement(sql);
                        pstmt.setLong(1, roleId);
                        Timestamp timestamp = new Timestamp(System.currentTimeMillis());
                        pstmt.setTimestamp(2, timestamp);
                        pstmt.setLong(3,slashCommandServerId);
                        pstmt.executeUpdate();
                        srConnection.commit();
                        srConnection.close();
                        slashCommandInteraction.createFollowupMessageBuilder()
                            .setContent("DeviantCord rank has been setup! You can now use DeviantCord fully!")
                            .send();
                    } catch (SQLException e) {
                        Sentry.captureException(e);
                        srConnection.rollback();
                        throw new RuntimeException(e);
                    }
                }
                else
                {
                    slashCommandInteraction.createFollowupMessageBuilder()
                        .setContent("The role you selected is not on this server!")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .send();
                }
            }
            // Create the response builder
            InteractionImmediateResponseBuilder response = slashCommandInteraction.createImmediateResponder()
                .setContent("Please select the required rank to access DeviantCord commands!")
                .setFlags(MessageFlag.EPHEMERAL);
            
            // Add buttons
            for(Role entry: obt_roles) {
                String key = "srFI-:-" + entry.getIdAsString();
                response.addComponents(ActionRow.of(Button.primary(key, entry.getName())));
            }

            // Send the response
            response.respond();
        } else {
            slashCommandInteraction.createImmediateResponder()
                .setContent("You need to be an admin to use this command!")
                .setFlags(MessageFlag.EPHEMERAL)
                .respond();
        }
    }
    public static void setupRoleAction(MessageComponentInteraction messageComponentInteraction, HikariDataSource ds,
                                       JedisPool redis_pool, String da_token, 
                                       DiscordApi api)
    {
        String responseId = messageComponentInteraction.getCustomId();
        HashMap<String, String> responseProperties = commandIdParser.parseRoleUpdateString(responseId);
        long obtRoleId = Long.valueOf(responseProperties.get("role"));
        long serverId = messageComponentInteraction.getServer().orElse(null).getId();
        Jedis redis = redis_pool.getResource();
        redis.set(String.valueOf(serverId)+ "-role", String.valueOf(obtRoleId));
        long time = 3600;
        //Using a int instead of a long is deprecated.
        redis.expire(String.valueOf(serverId)+ "-role", time);
        redis.close();
        String sql = SQLManager.grab_sql("update_rank");
        try(Connection srConnection = ds.getConnection();)
        {
            srConnection.setAutoCommit(false);
            try {
                
            PreparedStatement pstmt = srConnection.prepareStatement(sql);
            pstmt.setLong(1, obtRoleId);
            Timestamp timestamp = new Timestamp(System.currentTimeMillis());
            pstmt.setTimestamp(2, timestamp);
            pstmt.setLong(3,serverId);
            pstmt.executeUpdate();
            srConnection.commit();
            srConnection.close();
        } catch (SQLException e) {
            Sentry.captureException(e);
            srConnection.rollback();
            throw new RuntimeException(e);
        }
        messageComponentInteraction.createFollowupMessageBuilder()
                .setContent("DeviantCord rank has been setup! You can now use DeviantCord fully!").send();
        }
        catch(SQLException e){
            Sentry.captureException(e);
            throw new RuntimeException(e);
        }
    }
}
