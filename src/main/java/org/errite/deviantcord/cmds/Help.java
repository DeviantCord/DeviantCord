package org.errite.deviantcord.cmds;

import org.javacord.api.entity.message.MessageFlag;
import org.javacord.api.interaction.SlashCommandInteraction;

public class Help {

    public static void help(SlashCommandInteraction slashCommandInteraction) {
        slashCommandInteraction.respondLater();
        slashCommandInteraction.createFollowupMessageBuilder()
        .setContent("Here is the DeviantCord Command Page: https://deviantcord.com/docs/commands/command-list")
        .setFlags(MessageFlag.EPHEMERAL)
        .send();
    }
    
}
