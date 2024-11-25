package org.errite.deviantcord.cmds;

import org.javacord.api.DiscordApi;
import org.javacord.api.interaction.SlashCommand;
import org.javacord.api.interaction.SlashCommandOption;
import org.javacord.api.interaction.SlashCommandOptionType;
import io.sentry.Sentry;
import java.util.Arrays;

public class SlashCommandRegistrar {
    private final DiscordApi api;

    public SlashCommandRegistrar(DiscordApi api) {
        this.api = api;
    }

    public void registerCommands() {
        registerAddFolder();
        registerSetupRole();
        registerAddPost();
        registerHelp();
        registerDeletePost();
        registerAddAllFolder();
        registerUpdateInverse();
        registerDeleteFolder();
    }

    private void registerAddFolder() {
        SlashCommand.with("addfolder", "Create's a folder.",
                Arrays.asList(
                        SlashCommandOption.createWithOptions(SlashCommandOptionType.STRING, "Artist", "The name of the artist, exactly as it appears on DeviantArt"),
                        SlashCommandOption.createWithOptions(SlashCommandOptionType.STRING, "FolderName", "Name of the folder exactly as it appears on DeviantArt"),
                        SlashCommandOption.createWithOptions(SlashCommandOptionType.CHANNEL, "Channel", "The channel the bot should post to"),
                        SlashCommandOption.createWithOptions(SlashCommandOptionType.BOOLEAN, "Mature", "Does this feature NSFW content?"))
        ).createGlobal(api)
         .thenAccept(useless -> System.out.println("Adding addfolder!"))
         .exceptionally(this::handleException);
    }

    private void registerSetupRole() {
    
        SlashCommand.with("setuprole", "Designates the required role to access DeviantCord Commands",
        Arrays.asList(
                SlashCommandOption.createWithOptions(SlashCommandOptionType.ROLE, "Role",
                        "The Role that should be required for someone to interact with DeviantCord")
        )).createGlobal(api).thenAccept(useless -> System.out.println("Adding setup role"))
                .exceptionally(e -> {
                    e.printStackTrace();
                    String eventId = Sentry.captureException(e).toString();
                    System.out.println("Slash command creation error logged with ID: " + eventId);
                    return null;
                });
    }

    private void registerAddPost() {

                    SlashCommand.with("addpost", "Adds a post Listener (Journal and Status)",
                            Arrays.asList(
                                    SlashCommandOption.createWithOptions(SlashCommandOptionType.STRING, "Artist",
                                            "The name of the artist you want to receive status updates from"),
                                    SlashCommandOption.createWithOptions(SlashCommandOptionType.CHANNEL, "Channel",
                                            "The channel that status update notifications should be posted to")
                            )).createGlobal(api).thenAccept(useless -> System.out.println("Adding addjournal"))
                    .exceptionally(e -> {
                        e.printStackTrace();
                        String eventId = Sentry.captureException(e).toString();
                        System.out.println("Slash command creation error logged with ID: " + eventId);
                        return null;
                    });
    }

    private void registerHelp() {
        SlashCommand.with("help", "Displays the DeviantCord Help Page",
        Arrays.asList()).createGlobal(api).thenAccept(useless -> System.out.println("Adding help"))
        .exceptionally(e -> {
            e.printStackTrace();
            String eventId = Sentry.captureException(e).toString();
            System.out.println("Slash command creation error logged with ID: " + eventId);
            return null;
        });
    }

    private void registerDeletePost() {
        SlashCommand.with("deletepost", "Deletes a post listener (Journal and Status)")
        .createGlobal(api).thenAccept(useless -> System.out.println("Adding deletepost"))
        .exceptionally(e -> {
            e.printStackTrace();
            String eventId = Sentry.captureException(e).toString();
            System.out.println("Slash command creation error logged with ID: " + eventId);
            return null;
        });
    }

    private void registerAddAllFolder() {
        
        SlashCommand.with("addallfolder", "Creates an allfolder listener",
        Arrays.asList(
                SlashCommandOption.createWithOptions(SlashCommandOptionType.STRING, "artist",
                        "The artist that you want to create an allfolder listener for."),
                SlashCommandOption.createWithOptions(SlashCommandOptionType.CHANNEL, "channel",
                        "The channel that notifications should be posted to. ")
        )).createGlobal(api).thenAccept(useless -> System.out.println("Adding allfolder"))
                .exceptionally(e -> {
                    e.printStackTrace();
                    String eventId = Sentry.captureException(e).toString();
                    System.out.println("Slash command creation error logged with ID: " + eventId);
                    return null;
                });

    }

    private void registerUpdateInverse() {

        SlashCommand.with("updateinverse", "Updates inverse property for a folder listener")
        .createGlobal(api).thenAccept(useless -> System.out.println("Adding updateinverse"))
        .exceptionally( e -> {
            e.printStackTrace();
            String eventId = Sentry.captureException(e).toString();
            System.out.println("Slash command creation error logged with ID: " + eventId);
            return null;
        });
    }

    private void registerDeleteFolder() {
        
        SlashCommand.with("deletefolder", "Delete a folder listener.")
        .createGlobal(api).thenAccept(useless -> System.out.println("Adding deletefolder"))
        .exceptionally( e -> {
            e.printStackTrace();
            String eventId = Sentry.captureException(e).toString();
            System.out.println("Slash command creation error logged with ID: " + eventId);
            return null;
        });

    }


    private Void handleException(Throwable e) {
        e.printStackTrace();
        String eventId = Sentry.captureException(e).toString();
        System.out.println("Slash command creation error logged with ID: " + eventId);
        return null;
    }
}