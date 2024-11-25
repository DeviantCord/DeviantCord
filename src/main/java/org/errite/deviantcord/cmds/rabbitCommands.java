package org.errite.deviantcord.cmds;

import java.io.IOException;
import java.net.URL;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import javax.imageio.ImageIO;

import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.ServerTextChannel;
import org.javacord.api.entity.message.embed.EmbedBuilder;
import org.json.simple.JSONObject;

import java.awt.image.BufferedImage;
public class rabbitCommands {

    private static ExecutorService imageProcessingExecutor = Executors.newFixedThreadPool(2);
    private static CompletableFuture<BufferedImage> urlToBufferedImageAsync(String imageUrl) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                URL url = new URL(imageUrl);
                return ImageIO.read(url);
            } catch (IOException e) {
                throw new CompletionException(e);
            }
        }, imageProcessingExecutor);
    }


    public static void sendDeviation(String message, DiscordApi api, JSONObject jsonObject) {
        long channelId = (Long) jsonObject.get("channelid");
        ServerTextChannel channel = api.getServerTextChannelById(channelId).orElse(null);
        if (channel != null) {
            boolean matureDeviation = (boolean) jsonObject.get("mature_devi");
            if(matureDeviation) {
                if (!channel.isNsfw()) {
                    System.out.println("Mature deviation in non-NSFW channel");
                    return;
                }
            }
            EmbedBuilder embed = new EmbedBuilder();
            String artist_pp_url = (String) jsonObject.get("pp_url");
            if (artist_pp_url != "")
            {
                urlToBufferedImageAsync(artist_pp_url).thenAccept(image -> {
                    embed.setThumbnail(image);
                });
            }
            embed.setTitle("New Deviation");
            embed.setAuthor( "by " + (String) jsonObject.get("artist"), "https://www.deviantart.com/" + (String) jsonObject.get("artist"), (String)null);
            embed.setDescription("A new deviation has been posted in " + jsonObject.get("folder"));
            embed.setUrl((String) jsonObject.get("devi_url"));
            embed.setImage((String) jsonObject.get("devi_img_url"));
            channel.sendMessage(embed);
        }
    }

    public static void sendJournal(String message, DiscordApi api, JSONObject jsonObject) {
        long channelId = (Long) jsonObject.get("channelid");
        ServerTextChannel channel = api.getServerTextChannelById(channelId).orElse(null);
        if (channel != null) {
            boolean matureJournal = Boolean.parseBoolean((String) jsonObject.get("mature_journal"));
            if(matureJournal) {
                if (!channel.isNsfw()) {
                    System.out.println("Mature journal in non-NSFW channel");
                    return;
                }
            }
            EmbedBuilder embed = new EmbedBuilder();
            String artist_pp_url = (String) jsonObject.get("pp_url");
            
            if (artist_pp_url != "")
            {
                urlToBufferedImageAsync(artist_pp_url).thenAccept(image -> {
                    embed.setAuthor((String) jsonObject.get("artist"), null, image);
                });
            }
            embed.setTitle("New post from " + jsonObject.get("artist") + "!");
            embed.setDescription((String) jsonObject.get("title"));
            embed.setUrl((String) jsonObject.get("url"));
            channel.sendMessage(embed);
        }
    }

    public static void shutdown() {
        imageProcessingExecutor.shutdown();
        try {
            if (!imageProcessingExecutor.awaitTermination(60, TimeUnit.SECONDS)) {
                imageProcessingExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            imageProcessingExecutor.shutdownNow();
        }
    }
    



    
}
