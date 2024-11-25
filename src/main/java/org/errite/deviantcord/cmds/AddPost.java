package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import io.restassured.response.Response;
import io.sentry.Sentry;
import org.errite.deviantcord.psql.JournalManager;
import org.errite.deviantcord.da.daParser;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.message.MessageBuilder;
import org.javacord.api.entity.message.MessageFlag;
import org.javacord.api.entity.message.component.ActionRow;
import org.javacord.api.entity.message.component.Button;
import org.javacord.api.entity.server.Server;
import org.javacord.api.interaction.MessageComponentInteraction;
import org.javacord.api.interaction.SlashCommandInteraction;
import org.javacord.api.interaction.SlashCommandInteractionOption;
import redis.clients.jedis.JedisPool;
import org.javacord.api.entity.channel.ServerTextChannel;
import org.errite.deviantcord.sd.commandIdParser;


import java.sql.SQLException;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;

public class AddPost {

    //TODO this needs to have its commands go through the CommandRouter
    public static void addJournal(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds,
                                 JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException {
        slashCommandInteraction.respondLater();
        Optional<SlashCommandInteractionOption> optionalArtist = slashCommandInteraction.getOptionByName("artist");
        Optional<SlashCommandInteractionOption> optionalChannel = slashCommandInteraction.getOptionByName("channel");
        AtomicReference<String> artist = new AtomicReference<>("");
        if (optionalArtist.isPresent() && optionalChannel.isPresent()) {
            if (artist.get() == "") {
                slashCommandInteraction.createImmediateResponder()
                        .setContent("Please provide an artist name.")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .respond();
            }

            Response testJournal = daParser.getJournals(optionalArtist.get().getStringValue().orElse(""), da_token, false, false, 0);
            if (testJournal.getStatusCode() != 200) {
                slashCommandInteraction.createImmediateResponder()
                        .setContent("This artist does not exist on DeviantArt.")
                        .setFlags(MessageFlag.EPHEMERAL)
                        .respond();
            }
            //TODO We need to check if 
            ServerTextChannel channel = optionalChannel.get().getChannelValue().orElse(null).asServerTextChannel().orElse(null);
            //Add Journal's ID is aj
            String genCustomID = "FI-:-" + channel.getId() + "FI-:-" + optionalArtist.get().getStringValue().orElse("") + "FI-:-";
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent("Should this journal contain entries that are classified as mature?")
                    .addComponents(
                            ActionRow.of(Button.success("ajm" + genCustomID, "Yes"),
                                    Button.secondary("ajs" + genCustomID, "No")))
                    .send();
        }
    }

    public static void addJournalAction(MessageComponentInteraction messageComponentInteraction, HikariDataSource ds,
                                 JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException {
        String customId = messageComponentInteraction.getCustomId();
        HashMap<String, String> responseProperties = commandIdParser.parseAddJournalString(customId);
        String artist = responseProperties.get("artist");
        String channel = responseProperties.get("channel");
        ServerTextChannel channelObj = api.getServerTextChannelById(Long.parseLong(channel)).orElse(null);
        String mature = responseProperties.get("mature");
        HashSet<String> redisArtists = new HashSet<>();
        HashMap<String, Boolean> redisMature = new HashMap<>();
        HashMap<String, List<String>> redisFolders = new HashMap<>();
        HashMap<String, List<Long>> redisChannels = new HashMap<>();

        try {
            boolean sourceExists = JournalManager.verifySourceJournalExists(ds, artist.toUpperCase(Locale.ROOT),
                    Boolean.parseBoolean(mature));
            Response journalResponse = null;
            if (sourceExists) {
                if (Boolean.parseBoolean(mature) && !(channelObj.isNsfw())) {
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("This channel is not marked as NSFW, so mature content cannot be included.")
                            .send();
                    return;
                }

                Server obtChannelServer= channelObj.getServer();
                if (messageComponentInteraction.getServer().orElse(null).getId() != obtChannelServer.getId()) {
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("The channel you selected is not in the same server as the one you used to run this command.")
                            .setFlags(MessageFlag.EPHEMERAL)
                            .send();
                    return;
                }

                boolean listenerExists = JournalManager.verifyListenerJournalExists(ds,
                        artist.toUpperCase(Locale.ROOT), Boolean.parseBoolean(mature));
                if (listenerExists) {
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("This channel already has a journal listener for this artist!")
                            .send();
                    return;
                } else if (!(listenerExists)) {
                    JournalManager.addJournalTask(ds, artist.toUpperCase(Locale.ROOT), Boolean.parseBoolean(mature),
                            messageComponentInteraction.getServer().orElse(null).getId(), messageComponentInteraction.getChannel().orElse(null).getId());
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("Journal listener has been added!")
                            .send();
                    return;
                }
            } else if (!(sourceExists)) {
                Server obtChannelServer= channelObj.getServer();
                if (messageComponentInteraction.getServer().orElse(null).getId() != obtChannelServer.getId()) {
                    messageComponentInteraction.createFollowupMessageBuilder()
                            .setContent("The channel you selected is not in the same server as the one you used to run this command.")
                            .setFlags(MessageFlag.EPHEMERAL)
                            .send();
                    return;
                }
                journalResponse = daParser.getJournals(artist, da_token, Boolean.parseBoolean(mature), false, 0);
                JournalManager.addJournalSource(journalResponse, artist.toUpperCase(Locale.ROOT), ds, Boolean.parseBoolean(mature));
                JournalManager.addJournalTask(ds, artist.toUpperCase(Locale.ROOT), Boolean.parseBoolean(mature),
                        messageComponentInteraction.getServer().orElse(null).getId(), messageComponentInteraction.getChannel().orElse(null).getId());
                messageComponentInteraction.createFollowupMessageBuilder()
                        .setContent("Journal listener has been added!")
                        .send();
                messageComponentInteraction.createFollowupMessageBuilder().
                        setContent("Journal Listener has been added!").send();

                return;
            }
        } catch (SQLException e) {
            Sentry.captureException(e);
            throw new RuntimeException(e);
        }
    }
}
