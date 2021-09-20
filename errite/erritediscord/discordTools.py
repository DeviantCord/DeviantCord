"""

    DeviantCord 2 Discord Bot
    Copyright (C) 2020  Errite Games LLC/ ErriteEpticRikez

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
from math import ceil

import discord
import traceback
import psycopg2

async def convertChannelID(channelid:str, ctx):
    print("Starting convert role")
    startIndex = channelid.find("#") + 1
    print("After find")
    if startIndex == -1:
        return 0
    else:
        endIndex = channelid.find(">")
        if endIndex == -1:
            return 0
        try:
            int_channelid = int(channelid[startIndex:endIndex])
        except Exception as ex:
            return 0
        convrole = ctx.guild.get_channel(int_channelid)
        print("Conve")
        if convrole is None:
            return 0
        else:
            return int_channelid


async def convertRoleID(roleid:str, ctx):
    print("Starting convert role")
    print(roleid)
    startIndex = roleid.find("&") + 1
    print("After find")
    print(startIndex)
    if startIndex == 0:
        print(str(roleid.isdigit()))
        if roleid.isdigit():
            return roleid
        else:
            return 0
    else:
        endIndex = roleid.find(">")
        if endIndex == -1:
            return 0
        try:
            int_roleid = int(roleid[startIndex:endIndex])
        except Exception as ex:
            return 0
        convrole = ctx.guild.get_role(int_roleid)
        print("Conve")
        if convrole is None:
            return 0
        else:
            return int_roleid



async def sendDeviationNotifications(ctx, obt_notifications):
    sent_ids = []
    incorrect_mature = []
    bot_user = await ctx.fetch_user(ctx.user.id)
    for row in obt_notifications:
        try:
            channel_id = row[0]
            channel_sender = ctx.get_channel(channel_id)
            artist = row[1]
            foldername = row[2]
            deviation_link = row[3]
            img_url = row[4]
            pp_url = row[5]
            id = row[6]
            mature = row[9]
            passed = False
            useExternal = False
            if img_url.find("IGNORETHISDEVIATION") == -1:
                passed = True
            elif not img_url.find("DEVIANTCORDENDINGUSENONPREVIEW") == -1:
                useExternal = True
            if passed:
                if useExternal:
                    notification = discord.Embed(title="New External Deviation (Can't be previewed via Discord)", url=deviation_link)
                if not useExternal:
                    notification = discord.Embed(title="New Deviation", url=deviation_link)
                notification.add_field(name="by " + artist, value="Link above (blue text)")
                notification.set_thumbnail(url=pp_url)
                if not useExternal:
                    notification.set_image(url=img_url)
                notification.set_footer(
                    text="NOTE: DeviantArt serves its content through the Wix Media Platform.\n" +
                         "This is why the image link is wixmp.com and looks weird.")

                if channel_sender is None:
                    raise Exception('Unable to obtain the channelid from Discord!')
                elif mature == channel_sender.is_nsfw():
                    #permissions = bot_user.permissions_in(channel_sender)
                    #permissions = channel_sender.permissions_for(ctx.author)
                    await channel_sender.send(embed=notification)
                    sent_ids.append(id)
                else:
                    if not channel_id in incorrect_mature:
                        await channel_sender.send("The folder I am supposed to post content for is marked as mature, "
                                                  "but this folder is not set as NFSW. As per Discord’s Terms of Service "
                                                  "I am not allowed to post mature content in non NSFW channels. "
                                                  "As a precaution mature folders have been skipped for this channel."
                                                  " To correct this either set the channel back to NSFW or delete the listener"
                                                  " and readd it.")
                        incorrect_mature.append(channel_id)
                        sent_ids.append(id)
        except discord.Forbidden as Forb:
            print("Do not have permission to post in this channel.")
            sent_ids.append(id)
            continue
        except Exception as base_exception:
            print("A notification was skipped!")
            print("Reason: " + str(base_exception))
    return sent_ids


async def sendJournalNotifications(ctx, obt_notifications):
    sent_ids = []
    incorrect_mature = []
    bot_user = await ctx.fetch_user(ctx.user.id)
    for row in obt_notifications:
        try:
            channel_id = row[0]
            channel_sender = ctx.get_channel(channel_id)
            artist = row[1]
            pp_url = row[2]
            title = row[3]
            id = row[4]
            url = row[5]
            thumbnail = row[6]
            notifification_creation = row[7]
            mature = row[8]

            notification = discord.Embed(title="New Journal", url=url)
            notification.add_field(name="by " + artist, value="Link above (blue text)")
            notification.set_thumbnail(url=pp_url)
            if not thumbnail.lower() == "none":
                notification.set_image(url=thumbnail)
            notification.set_footer(
                text="NOTE: DeviantArt serves its content through the Wix Media Platform.\n" +
                     "This is why the image link is wixmp.com and looks weird.")

            if channel_sender is None:
                raise Exception('Unable to obtain the channelid from Discord!')
            elif mature == channel_sender.is_nsfw():
                #permissions = bot_user.permissions_in(channel_sender)
                #permissions = channel_sender.permissions_for(ctx.author)
                await channel_sender.send(embed=notification)
                sent_ids.append(id)
            else:
                if not channel_id in incorrect_mature:
                    await channel_sender.send("The folder I am supposed to post content for is marked as mature, "
                                              "but this folder is not set as NFSW. As per Discord’s Terms of Service "
                                              "I am not allowed to post mature content in non NSFW channels. "
                                              "As a precaution mature folders have been skipped for this channel."
                                              " To correct this either set the channel back to NSFW or delete the listener"
                                              " and readd it.")
                    incorrect_mature.append(channel_id)
                    sent_ids.append(id)
        except discord.Forbidden as Forb:
            print("Do not have permission to post in this channel.")
            sent_ids.append(id)
            continue
        except Exception as base_exception:
            print("A notification was skipped!")
            print("Reason: " + str(base_exception))
    return sent_ids

def createTestLocalDeviationListString(data):
    messages = []
    last_artist = None
    string = ""
    for entry in data:
        artist = entry[1]
        foldername = entry[12]
        channelid = entry[7]
        if last_artist == None:
            string = string + "** " + artist + "'s Listeners: **"
        elif not last_artist == artist:
            string = string + "\n** " + artist + "'s Listeners: **"
        channel_object = "test placeholder"
        if channel_object is None:
            string = string + "\n Contact DeviantCord Support Reference Errorcode 05"
        else:
            string = string + "\n" + foldername +" in " + "test channel"
        last_artist = artist
    divider = ceil(len(string) / 2000)
    if divider == 1:
        messages.append(string)
    else:
        pass_index = 0
        first_index = 0
        while not pass_index > divider:
            messages.append(string[first_index:first_index + 1999])
            first_index = first_index + 1999
            pass_index = pass_index + 1
    return messages

async def journalListString(data, bot):
    messages = []
    last_artist = None
    output = "**Journal Listeners**\n"
    for entry in data:
        artist = entry[0]
        channelid = entry[8]
        channel_object = bot.get_channel(channelid)
        output = output + "**" + artist + "** listener in **" + channel_object.name + "**\n"
        last_artist = artist
    divider = ceil(len(output) / 2000)
    if divider == 1:
        messages.append(output)
    else:
        pass_index = 0
        first_index = 0
        while not pass_index > divider:
            messages.append(output[first_index:first_index + 1999])
            first_index = first_index + 1999
            pass_index = pass_index + 1
    return messages

async def createDeviationListString(data, bot):
    messages = []
    last_artist = None
    string = ""
    for entry in data:
        artist = entry[1]
        foldername = entry[12]
        channelid = entry[7]
        if last_artist == None:
            string = string + "** " + artist + "'s Listeners: **"
        elif not last_artist == artist:
            string = string + "\n** " + artist + "'s Listeners: **"
        channel_object = bot.get_channel(channelid)
        if channel_object is None:
            string = string + "\n Contact DeviantCord Support Reference Errorcode 05"
        else:
            string = string + "\n" + foldername +" in " + channel_object.name
        last_artist = artist
    divider = ceil(len(string) / 2000)
    if divider == 1:
        messages.append(string)
    else:
        pass_index = 0
        first_index = 0
        while not pass_index > divider:
            messages.append(string[first_index:first_index + 1999])
            first_index = first_index + 1999
            pass_index = pass_index + 1
    return messages

async def sendListMessage(channel_object, data):
    for entry in data:
        if not entry == '':
            if not entry == "":
                await channel_object.send(entry)