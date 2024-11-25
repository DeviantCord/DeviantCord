/*
 * DeviantCord 4
 * Copyright (C) 2020-2024  Errite Softworks LLC/ ErriteEpticRikez
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */
package org.errite.deviantcord.notifications;

import com.zaxxer.hikari.HikariDataSource;
import org.javacord.api.DiscordApi;
import org.javacord.api.entity.message.embed.EmbedBuilder;

import java.sql.ResultSet;
import java.sql.SQLException;

public class notificationManager {

    public static void sendDeviations(HikariDataSource given_ds, DiscordApi api, ResultSet rs) throws SQLException {
        while (rs.next()){
            boolean passed = false;
            boolean useExternal = false;
            long channel_id = rs.getLong("channelid");
            String artist = rs.getString("artist");
            String foldername= rs.getString("foldername");
            String deviation_link = rs.getString("deviation_link");
            String img_url = rs.getString("img_url");
            String pp_url = rs.getString("pp_url");
            boolean mature = rs.getBoolean("mature_only");
            int id = rs.getInt("id");
            if (!(img_url.contains("IGNORETHISDEVIATION")))
                passed = true;
            else if(!(img_url.contains("DEVIANTCORDENDINGUSENONPREVIEW")))
                useExternal = true;
            if(passed)
            {
                if(useExternal)
                {
                    EmbedBuilder embed = new EmbedBuilder()
                            .setTitle("New External Deviation (Can't be previewed via Discord)")
                            .setAuthor(artist, "https://deviantart.com/" + artist, pp_url)
                            .setThumbnail(pp_url)
                            .setUrl(deviation_link);
                    api.getTextChannelById(channel_id).ifPresent(channel -> channel.sendMessage(embed));

                }
                else if(!(useExternal)){
                    EmbedBuilder embed = new EmbedBuilder()
                            .setTitle("New Deviation")
                            .setAuthor(artist, "https://deviantart.com/" + artist, pp_url)
                            .setImage(img_url)
                            .setThumbnail(pp_url)
                            .setUrl(deviation_link);
                    api.getTextChannelById(channel_id).ifPresent(channel -> channel.sendMessage(embed));
                }

            }
            System.out.println(channel_id);

        }
    }
}
