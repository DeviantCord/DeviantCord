package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.sd.commandId;
import org.javacord.api.DiscordApi;
import org.javacord.api.interaction.MessageComponentInteraction;
import redis.clients.jedis.JedisPool;

import java.io.IOException;
import java.sql.SQLException;

public class commandRouter {

    public static void routeCommand(String responseId, MessageComponentInteraction messageComponentInteraction,
                                    HikariDataSource ds, JedisPool redis_pool, String da_token,
                                     DiscordApi api) throws SQLException, IOException, ClassNotFoundException {

        Enum<commandId.Command> obtCommand = commandId.parseCommand(responseId);
        if(obtCommand.equals(commandId.Command.UpdateChannel))
            UpdateChannel.updateChannelAction(messageComponentInteraction, ds, redis_pool, da_token, api);
        else if(obtCommand.equals(commandId.Command.UpdateInverse))
            UpdateInverse.updateInverseAction(messageComponentInteraction, ds,redis_pool, da_token,  api);
        else if(obtCommand.equals(commandId.Command.DeleteFolder))
            DeleteFolder.deleteFolderAction(messageComponentInteraction, ds, redis_pool, da_token,  api);
        else if(obtCommand.equals(commandId.Command.AddFolder))
            AddFolder.addFolderAction(messageComponentInteraction, ds, redis_pool, da_token,  api);
        else if(obtCommand.equals(commandId.Command.AddAllFolder))
            AddAllFolder.addAllFolderAction(messageComponentInteraction,ds, redis_pool, da_token,  api);
        else if(obtCommand.equals(commandId.Command.SetupRole))
            setupRole.setupRoleAction(messageComponentInteraction,ds,redis_pool,da_token,api);
        else if(obtCommand.equals(commandId.Command.AddPost))
            AddPost.addJournalAction(messageComponentInteraction,ds,redis_pool,da_token,api);
        else if(obtCommand.equals(commandId.Command.NextFolderPage))
            DeleteFolder.
    }
}
