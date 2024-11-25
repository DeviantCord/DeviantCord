package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import io.sentry.Sentry;
import org.errite.deviantcord.cmds.*;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.message.MessageFlag;
import org.javacord.api.interaction.SlashCommandInteraction;
import redis.clients.jedis.JedisPool;

import java.io.IOException;
import java.sql.SQLException;
import java.util.Locale;
import java.util.concurrent.atomic.AtomicReference;
import org.errite.deviantcord.threading.ExecutorManager;

/*
    CommandHandler is responsible for handling the slash command interactions and handling them to the correct function.
     It does not handle message component interactions.
    SlashCommandInteractions are only created when a user runs a slash command. Not when they press a button or something.
 */

public class CommandHandler {
    private final ExecutorManager executorManager;
    private final HikariDataSource ds;
    private final JedisPool pool;
    private final AtomicReference<String> da_token;
    private final DiscordApi api;

    public CommandHandler(ExecutorManager executorManager, HikariDataSource ds, JedisPool pool, 
                         AtomicReference<String> da_token, DiscordApi api) {
        this.executorManager = executorManager;
        this.ds = ds;
        this.pool = pool;
        this.da_token = da_token;
        this.api = api;
    }

    public void handleCommand(SlashCommandInteraction csi) {
        String ran_cmd = csi.getCommandName().toLowerCase(Locale.ROOT);
        
        switch (ran_cmd) {
            case "addfolder":
                handleAddFolder(csi);
                break;
            case "setuprole":
                handleSetupRole(csi);
                break;
            case "addpost":
                handleAddPost(csi);
                break;
            case "deletejournal":
                handleDeleteJournal(csi);
                break;
            case "updatechannel":
                break;
            case "updateinverse":
                handleUpdateInverse(csi);
                break;
            case "addallfolder":
                handleAddAllFolder(csi);
                break;
            case "deletefolder":
                handleDeleteFolder(csi);
                break;
            case "help":
                handleHelp(csi);
                break;
            default:
                // Handle unknown command
                break;
        }
    }

    private void handleHelp(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            Help.help(csi);
        });
    }

    private void handleAddAllFolder(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            try {
                AddAllFolder.addallfolder(csi, ds, pool, da_token.get(), api);
            } catch (SQLException e) {
                handleError(csi, e, "Database");
            }
        });
    }

    private void handleDeleteFolder(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            try {
                DeleteFolder.deletefolder(csi, ds, pool, api);
            } catch (SQLException e) {
                handleError(csi, e, "Database");
            }
        });
    }

    private void handleUpdateInverse(SlashCommandInteraction csi){
        executorManager.getCommandExecutor().submit(() -> {
            try{
                UpdateInverse.updateinverse(csi, ds, pool, da_token.get(), api);
            } catch (SQLException e){
                handleError(csi, e, "Database");
            } catch (IOException e) {
                handleError(csi, e, "IO");
            } catch (ClassNotFoundException e) {
                handleError(csi, e, "ClassNotFound");
            }
        });
    }

    //This has been put on hold for now. 
    private void handleUpdateChannel(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            try {
                UpdateChannel.updatechannel(csi, ds, pool, da_token.get(), api);
            } catch (SQLException e) {
                handleError(csi, e, "Database");
            }catch (IOException e) {
                handleError(csi, e, "IO");
            } catch (ClassNotFoundException e) {
                handleError(csi, e, "ClassNotFound");
            }
        });
    }

    private void handleAddPost(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            try {
                AddPost.addJournal(csi, ds, pool, da_token.get(), api);
            } catch (SQLException e) {
                handleError(csi, e, "Database");
            }
        });
    }


    private void handleDeleteJournal(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            try {
                AddPost.addJournal(csi, ds, pool, da_token.get(), api);
            } catch (SQLException e) {
                handleError(csi, e, "Database");
            }
        });
    }


    private void handleAddFolder(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            try {
                AddFolder.addfolder(csi, ds, pool, da_token.get(), api);
            } catch (SQLException e) {
                handleError(csi, e, "Database");
            }
        });
    }

    private void handleSetupRole(SlashCommandInteraction csi) {
        executorManager.getCommandExecutor().submit(() -> {
            try {
                setupRole.setuprole(csi, ds, pool, da_token.get(), api);
            } catch (SQLException e) {
                handleError(csi, e, "Database");
            }
        });
    }


    private void handleError(SlashCommandInteraction csi, Exception e, String errorType) {
        String eventId = Sentry.captureException(e).toString();
        System.out.println(errorType + " error logged with ID: " + eventId);
        csi.createImmediateResponder()
            .setContent("An error occurred processing your request. Event ID: " + eventId)
            .setFlags(MessageFlag.EPHEMERAL)
            .respond();
    }
}