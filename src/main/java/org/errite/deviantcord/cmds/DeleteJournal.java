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

public class DeleteJournal{

        public static void deletejournal(SlashCommandInteraction sci, HikariDataSource ds,
                                        JedisPool redis_pool, DiscordApi api) throws SQLException{
                sci.respondLater();
                L1CheckObject checkObject = L1Check.checkL1(sci,ds, redis_pool);
                TextChannel used_channel = sci.getChannel().orElse(null);
                if(checkObject.isFailedCheck())
                {
                        sci.createFollowupMessageBuilder()
                                .setContent(checkObject.getFailureReason())
                                .send();
                        return;
                }
                Connection sql_conn = ds.getConnection();
                String channel_sql = SQLManager.grab_sql("get_journals_by_server");
                PreparedStatement pstmt = sql_conn.prepareStatement(channel_sql);
                pstmt.setLong(1, checkObject.getServerId());
                //TODO check what happens what the size is when invalid artist is sent
                ResultSet rs = pstmt.executeQuery();
                MessageBuilder mb = new MessageBuilder();
                int current_index = 0;
                ArrayList<HashMap<String, String>> obt_listeners = new ArrayList<HashMap<String, String>>();
                mb.setContent("Please select the listener you want to delete");
                int index = 0;
                HashMap<String, String> temp_hmap = new HashMap<String, String>();
                //TODO This current implementation will work for most people. If they have a lot of listeners then,
                // We need to figure out a way to show the listeners without hitting the character limit
                // https://stackoverflow.com/questions/47062813/how-to-get-the-size-of-a-resultset
                while(rs.next()) {
                        //Declare the temporary hashmap that we will put into obt_listeners
                        //Grab information from the resultset
                        long obt_id = rs.getLong("channelid");
                        String artist = rs.getString("artist");
                        //Put necessary information into the Hashmap
                        temp_hmap.put("artist", artist);
                        TextChannel obt_tc = api.getTextChannelById(obt_id).orElse(null);
                        ServerTextChannel channel_name = obt_tc.asServerTextChannel().orElse(null);
                        temp_hmap.put("channelname", channel_name.getName());
                        temp_hmap.put("channelid", String.valueOf(obt_id));
                        mb.addComponents(ActionRow.of(Button.primary(String.valueOf(index), artist + " in " +
                                channel_name.getName())));
                        obt_listeners.add(temp_hmap);
                }
                if(temp_hmap.size() == 0)
                {
                        sci.createFollowupMessageBuilder().
                                setContent("This server has no journals :(, if you feel this is in error contact DeviantCord on the support server!").send();
                        return;
                }
                mb.send(used_channel);
                api.addMessageComponentCreateListener(event ->{

                        MessageComponentInteraction mci = event.getMessageComponentInteraction();
                        String responseId = mci.getCustomId();
                        HashMap<String, String> obt_listener = obt_listeners.get(Integer.valueOf(responseId));
                        String delete_sql = SQLManager.grab_sql("delete_journal");
                        try {
                                PreparedStatement deletestmt = sql_conn.prepareStatement(delete_sql);
                                deletestmt.setLong(1, checkObject.getObtServer().getId());
                                deletestmt.setString(2, obt_listener.get("artist"));
                                deletestmt.setLong(3, Long.valueOf(obt_listener.get("channelid")));
                                deletestmt.executeUpdate();
                                mci.createFollowupMessageBuilder()
                                        .setContent("Journal Listener in this channel deleted for " +
                                                obt_listener.get("artist")).send();
                                sci.createFollowupMessageBuilder().setContent("Listener deleted!").send();
                        } catch (SQLException e) {
                                throw new RuntimeException(e);
                        }

                });

        }
}
