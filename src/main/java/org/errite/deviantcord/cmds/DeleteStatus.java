package org.errite.deviantcord.cmds;

import com.zaxxer.hikari.HikariDataSource;
import org.errite.deviantcord.checks.L1Check;
import org.errite.deviantcord.psql.SQLManager;
import org.errite.deviantcord.types.L1CheckObject;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.channel.ServerTextChannel;
import org.javacord.api.entity.channel.TextChannel;
import org.javacord.api.entity.message.MessageBuilder;
import org.javacord.api.entity.message.component.ActionRow;
import org.javacord.api.entity.message.component.Button;
import org.javacord.api.interaction.MessageComponentInteraction;
import org.javacord.api.interaction.SlashCommandInteraction;
import redis.clients.jedis.JedisPool;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;

public class DeleteStatus {

    public static void deleteStatus(SlashCommandInteraction sci, HikariDataSource ds,
                                     JedisPool redis_pool, DiscordApi api) throws SQLException {
        sci.respondLater();
        L1CheckObject checkObject = L1Check.checkL1(sci,ds, redis_pool);
        TextChannel used_channel = sci.getChannel().orElse(null);
        if(checkObject.isFailedCheck())
        {
            sci.createImmediateResponder()
                    .setContent(checkObject.getFailureReason())
                    .respond();
            return;
        }
        Connection sql_conn = ds.getConnection();
        String channel_sql = SQLManager.grab_sql("get_statuses_by_server");
        PreparedStatement pstmt = sql_conn.prepareStatement(channel_sql);
        pstmt.setLong(1, checkObject.getServerId());
        ResultSet rs = pstmt.executeQuery();
        MessageBuilder mb = new MessageBuilder();
        ArrayList<HashMap<String, String>> obt_listeners = new ArrayList<HashMap<String, String>>();
        mb.setContent("Please select the listener you want to delete");
        int index = 0;
        while(rs.next()) {
            //Declare the temporary hashmap that we will put into obt_listeners
            HashMap<String, String> temp_hmap = new HashMap<String, String>();
            //Grab information from the resultset
            long obt_id = rs.getLong("channelid");
            String artist = rs.getString("artist");
            //Put necessary information into the Hashmap
            temp_hmap.put("artist", artist);
            TextChannel obt_tc = api.getTextChannelById(obt_id).orElse(null);
            ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
            temp_hmap.put("channelname", channel_name.getName());
            temp_hmap.put("channelid", String.valueOf(obt_id));
            mb.addComponents(ActionRow.of(Button.primary(String.valueOf(index), artist.toUpperCase() + " in " +
                    channel_name.getName())));
            obt_listeners.add(temp_hmap);
        }
        mb.send(used_channel);
        api.addMessageComponentCreateListener(event ->{
            MessageComponentInteraction mci = event.getMessageComponentInteraction();
            mci.respondLater();
            String responseId = mci.getCustomId();
            HashMap<String, String> obt_listener = obt_listeners.get(Integer.valueOf(responseId));
            String delete_sql = SQLManager.grab_sql("delete_status");
            try {
                PreparedStatement deletestmt = sql_conn.prepareStatement(delete_sql);
                deletestmt.setLong(1, checkObject.getObtServer().getId());
                deletestmt.setString(2, obt_listener.get("artist"));
                deletestmt.setLong(3, Long.valueOf(obt_listener.get("channelid")));
                deletestmt.executeUpdate();
                mci.createFollowupMessageBuilder()
                        .setContent("Status Listener for artist " + obt_listener.get("artist") +
                                " has been deleted for this channel").send();
                sci.createFollowupMessageBuilder()
                        .setContent("Status listener deleted!").send();

            } catch (SQLException e) {
                throw new RuntimeException(e);
            }

        });

    }
}
