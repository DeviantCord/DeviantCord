package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import io.restassured.response.Response;
import org.errite.deviantcord.checks.L2Check;
import org.errite.deviantcord.da.daParser;
import org.errite.deviantcord.psql.StatusManager;
import org.errite.deviantcord.types.L2CheckObject;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.ServerChannel;
import org.javacord.api.interaction.SlashCommandInteraction;
import org.javacord.api.interaction.SlashCommandInteractionOption;
import redis.clients.jedis.JedisPool;

import java.sql.SQLException;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;


public class AddStatus {

    public static void addStatus(SlashCommandInteraction slashCommandInteraction, HikariDataSource ds,
                                  JedisPool redis_pool, String da_token, DiscordApi api) throws SQLException {
        slashCommandInteraction.respondLater();
        Optional<SlashCommandInteractionOption> optionalArtist = slashCommandInteraction.getOptionByName("artist");
        Optional<SlashCommandInteractionOption> optionalChannel = slashCommandInteraction.getOptionByName("channel");
        AtomicReference<String> artist = new AtomicReference<>("");
        AtomicReference<ServerChannel> channel = new AtomicReference<>();
        if (optionalArtist.isPresent()) {
            artist.set(optionalArtist.get().getStringValue().orElse(""));
        } else {
            slashCommandInteraction.createImmediateResponder()
                    .setContent("Please provide an artist name.")
                    .respond();
            return;
        }

        if (optionalChannel.isPresent()) {
            channel.set(optionalChannel.get().getChannelValue().orElse(null));
        } else {
            slashCommandInteraction.createImmediateResponder()
                    .setContent("Please provide a channel.")
                    .respond();
            return;
        }
        L2CheckObject checkObject = L2Check.checkL2(slashCommandInteraction, ds, redis_pool, false,
                channel.get(), false);
        if (checkObject.isFailedCheck()) {
            slashCommandInteraction.createImmediateResponder()
                    .setContent(checkObject.getFailureReason())
                    .respond();
            return;
        }
        boolean sourceExists = StatusManager.verifySourceStatusExists(ds, artist.get().toUpperCase(Locale.ROOT));
        boolean listenerExists = StatusManager.verifyListenerStatusExists(ds, artist.get().toUpperCase(Locale.ROOT));
        if (!(sourceExists)){
            Response statusResponse = daParser.getStatuses(artist.get(), da_token, 0);
            if(statusResponse.getStatusCode() == 400)
            {
                slashCommandInteraction.createFollowupMessageBuilder()
                        .setContent("Could not find a DeviantArt user with the given username.")
                        .send();
                return;
            }
            StatusManager.addStatusSource(statusResponse,artist.get().toUpperCase(Locale.ROOT),ds);
        }
        if(listenerExists){
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent("A status listener for this artist already exists!")
                    .send();
            return;
        }
        else{
            StatusManager.addStatusTask(ds, artist.get().toUpperCase(Locale.ROOT),checkObject.getServerId(),
                    checkObject.getGivenTextChannel().getId());
            slashCommandInteraction.createFollowupMessageBuilder()
                    .setContent("A status listener for this artist has been created!").send();
            return;
        }



    }
}
