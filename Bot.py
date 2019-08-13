"""

    Copyright 2019 Errite Games LLC / ErriteEpticRikez

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
import json
import os
import asyncio
import discord
import datetime
import sys, traceback
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from discord.ext import commands
from discord.ext.commands import has_permissions
from errite.da.jsonTools import updateprefix, updatelogchannel, update_errite
from errite.config.configManager import createConfig, createSensitiveConfig
from errite.tools.mis import fileExists
from errite.config.converter import convert
from os import listdir
from os.path import isfile, join

# DeviantCord Message Variables (Not all are here)
invalid_cog_errite = "Invalid cog found on reload for discord server "
print("Starting DeviantCord bt-1.4.5")
print("If this causes a HTTP 401 Error when trying to load daCommands your DeviantArt info is wrong. Set it in client.json")
started = True
configData = {}
sensitiveData = {}
errite = False
prefix = None
passed = True
roleid = None
passedJson = False;
whiletrigger = False
logname = "discord"
if fileExists(logname):
    counter = 0
    while not whiletrigger:
                counter += 1
                tempfilename = logname + "-" + str(counter)
                if not fileExists(tempfilename):
                    logname = tempfilename
                    whiletrigger = True

botlogger = logging.getLogger()
botlogger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler(logname, when='h',interval=6, backupCount=2000, encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
botlogger.addHandler(handler)

if fileExists("config.json") == False:
    createConfig()
if fileExists("client.json") == False:
    createSensitiveConfig()
    print("You need to set your login information!")
    passed = False;

if passed == True:
    if fileExists("config.json") == True:

        if fileExists("client.json") == True:
            convert()
            with open("config.json", "r") as configjsonFile:
                with open("client.json", "r") as clientjsonFile:
                    configData = json.load(configjsonFile)
                    sensitiveData = json.load(clientjsonFile)
                    configjsonFile.close()
                    clientjsonFile.close()
                    if sensitiveData["da-client-id"] is not "id here":
                        if sensitiveData["da-secret"] is not "secret":
                            passedJson = True

if passedJson == True:
    prefix = configData["prefix"]
    client = commands.Bot(command_prefix=prefix)
    # WEB API
    clientsecret = sensitiveData["da-secret"]
    clientid = sensitiveData["da-client-id"]
    publicmode = configData["publicmode"]
    logchannelid = configData["logchannelid"]
    roleid = configData["roleid"]
    guildid = configData["guildid"]
    # Errite LLC Specific Options THIS is for DeviantCord Public Hosting, these settings are what
    # stops the bot from executing code meant for DeviantCord Public Hosting only
    errite = configData["errite"]
    errite_channel = configData["errite-channel"]
    location = configData["region"]
    server = configData["server"]
    # The variable below this is referred to as client in all other python files. Its because client is already used
    # that this is different. It refers to the name of the Discord Server internally on Errite Servers.
    discord_server = configData["client"]
else:
    print("JSON Test failed, reverting to default settings")
    client = commands.Bot(command_prefix="$")
    prefix = "$"



cogs_dir = "cogs"
if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            if not extension == "__init__":
                print("Trying")
                print("Loading " + extension)
                client.load_extension(cogs_dir + "." + extension)
        except (discord.ClientException, ModuleNotFoundError):
            print('Failed to load extension {extension}.')
            traceback.print_exc()


async def tester():
    await client.wait_until_ready()

    while not client.is_closed():
        print("Tested!")
        await asyncio.sleep(20)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
@has_permissions(administrator=True)
async def setlogchannel(ctx, logchannel):
    if ctx.guild is None:
        return;
    elif ctx.guild.id == guildid:
        permitted = True
    elif guildid is "not-setup":
        permitted = True;
    if permitted:
        if isinstance(logchannel, int):
            print("Logchannel input is Integer")
            try:
                channel = client.get_channel(logchannel)
                if channel is None:
                    print("Could not link with provided channelid")
                    await ctx.send(
                        "Error: The new channel id you provided is invalid, is it correct? Do I have permission to access it?")
                    return;
                updatelogchannel(logchannel)
                logchannelid = logchannel
            except KeyError:
                print("Encountered KeyError when verifying newchannelid...newchannelid is not a discordchannelid")
                print("Notifying channel")
                await ctx.send("Error: Invalid discord channel id provided...")
                return;
        elif isinstance(logchannel, str):
            print("Log Channel input is String")
            try:
                result = int(logchannel)
                print("Successfully Converted new channelid to ", result)
                channel = client.get_channel(result)
                if channel is None:
                    print("Could not link with provided channelid")
                    await ctx.send(
                        "Error: The new channel id you provided is invalid, is it correct? Do I have permission to access it?")
                    return;
                updatelogchannel(logchannel)
                logchannelid = logchannel
            except KeyError:
                print("Encountered KeyError when verifying newchannelid...newchannelid is not a discordchannelid")
                print("Notifying channel")
                await ctx.send("Error: Invalid discord channel id provided...")
                return;
    await ctx.send("Log Channel updated to ", logchannel)


@client.command()
@has_permissions(administrator=True)
async def setprefix(ctx, suppliedprefix):
    skiprolecheck = False
    if ctx.guild is None:
        return;
    elif ctx.guild.id == guildid:
        permitted = True
    elif not ctx.guild.id == guildid:
        return
    elif errite is None:
        return
    elif not publicmode:
        permitted = True
    if permitted:
        updateprefix(suppliedprefix)
        prefix = suppliedprefix
        client.command_prefix = suppliedprefix
        await ctx.send("Set prefix to " + suppliedprefix + "now reloading...")
        if errite:
            botlogger.info("setprefix: Errite is true")
        if not errite:
            botlogger.info("setprefix: Errite is false")
        cogs_dir = "cogs"
        if __name__ == '__main__':
            for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
                try:
                    if not extension == "__init__":
                        botlogger.info("setprefix: Unloading " + extension)
                        print("Unloading " + extension)
                        client.unload_extension(cogs_dir + "." + extension)
                        botlogger.info("setprefix: loading " + extension)
                        print("Loading " + extension)
                        client.load_extension(cogs_dir + "." + extension)
                        botlogger.info("setprefix: Successfully reloaded " + extension)
                        print("Successfully reloaded " + extension)
                except (discord.ClientException, ModuleNotFoundError):
                    print('Failed to load extension {extension}.')
                    botlogger.error("setprefix: Invalid Cog found for " + extension)
                    traceback.print_exc()
                    await ctx.send("Invalid cog found inside the cogs folder. If you are using the public bot contact"
                                   " DeviantCord Support. ")
                    botlogger.error(extension + " cog failed to load ")
                    if errite:
                        botlogger.info("setprefix: Errite is true, now getting channel")
                        support_channel = client.get_channel(errite_channel)
                        if support_channel is None:
                            botlogger.info("setprefix: Was unable to link with Errite channel")
                            await ctx.send("AutoErrorReport is not working, please mention this while"
                                           " speaking to support.")
                        else:
                            botlogger.info("setprefix: Errite channel successfully established, now sending message")
                            await support_channel.send("Exception experienced while reloading\n"
                                                       "**Server Info:**\n" +
                                                       "Current Server Name: " + ctx.guild.name +
                                                       "\nServer Id: " + str(ctx.guild.id) +
                                                       "\nInternal Name: " + discord_server +
                                                       "\nEGServer: " + server +
                                                       "\nServer Location: " + location +
                                                       "\nException: TEST" +
                                                       "\nCog: " + extension)
                            botlogger.info("setprefix: Errite SOS Reload Message successfully sent")
                except Exception as e:
                    print("Experienced exception while loading " + extension + "\n")
                    botlogger.error("Experienced exeption while loading " + extension)
                    await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}' + "Please contact DeviantCord Support")
                    if errite:
                        support_channel = client.get_channel(errite_channel)
                        if support_channel is None:
                            botlogger.error("setprefix: was unable to link with Errite channel")
                            await ctx.send("AutoErrorReport is not working, please mention this while"
                                           " speaking to support.")
                        else:
                            botlogger.info("setprefix: Errite channel successfully established, now sending message")
                            await support_channel.send("Exception experienced while reloading\n"
                                                       "**Server Info:**\n" +
                                                       "Current Server Name: " + ctx.guild.name +
                                                       "\nServer Id: " + str(ctx.guild.id) +
                                                       "\nInternal Name: " + discord_server +
                                                       "\nEGServer: " + server +
                                                       "\nServer Location: " + location +
                                                       "\nException: " + e)
                            botlogger.info("setprefix: Errite SOS Reload Message successfully sent")
                else:
                    botlogger.info("setprefix: " + extension + "successfully reloaded")
                    await ctx.send('**`SUCCESSFULLY RELOADED `' + extension + '**')
            await ctx.send("Reload Finished! ")


@client.command()
@has_permissions(administrator=True)
async def reload(ctx):
    """Command which Reloads a Module.
    Remember to use dot path. e.g: cogs.owner"""
    skiprolecheck = False
    if ctx.guild is None:
        return;
    elif ctx.guild.id == guildid:
        permitted = True
    elif not publicmode:
        permitted = True
    if permitted:
        if errite:
            botlogger.info("Reload: Errite is true")
        if not errite:
            botlogger.info("Reload: Errite is false")
        if errite is None:
            return
        cogs_dir = "cogs"
        if __name__ == '__main__':
            for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
                try:
                    if not extension == "__init__":
                        botlogger.info("Reload: Unloading " + extension)
                        print("Unloading " + extension)
                        client.unload_extension(cogs_dir + "." + extension)
                        botlogger.info("Reload: loading " + extension)
                        print("Loading " + extension)
                        client.load_extension(cogs_dir + "." + extension)
                        botlogger.info("Reload: Successfully reloaded " + extension)
                        print("Successfully reloaded " + extension)
                except (discord.ClientException, ModuleNotFoundError):
                    print('Failed to load extension {extension}.')
                    botlogger.error("Reload: Invalid Cog found for " + extension)
                    traceback.print_exc()
                    await ctx.send("Invalid cog found inside the cogs folder. If you are using the public bot contact"
                                   " DeviantCord Support. ")
                    botlogger.error(extension + " cog failed to load ")
                    if errite:
                        botlogger.info("Reload: Errite is true, now getting channel")
                        support_channel = client.get_channel(errite_channel)
                        if support_channel is None:
                            botlogger.info("Reload: Was unable to link with Errite channel")
                            await ctx.send("AutoErrorReport is not working, please mention this while"
                                           " speaking to support.")
                        else:
                            botlogger.info("Reload: Errite channel successfully established, now sending message")
                            await support_channel.send("Exception experienced while reloading\n"
                                                       "**Server Info:**\n" +
                                                       "Current Server Name: " + ctx.guild.name +
                                                       "\nServer Id: " + str(ctx.guild.id) +
                                                       "\nInternal Name: " + discord_server +
                                                       "\nEGServer: " + server +
                                                       "\nServer Location: " + location +
                                                       "\nException: TEST" +
                                                       "\nCog: " + extension)
                            botlogger.info("Reload: Errite SOS Reload Message successfully sent")
                except Exception as e:
                    print("Experienced exception while loading " + extension + "\n")
                    botlogger.error("Experienced exeption while loading " + extension)
                    await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}' + "Please contact DeviantCord Support")
                    if errite:
                        support_channel = client.get_channel(errite_channel)
                        if support_channel is None:
                            botlogger.error("Reload: was unable to link with Errite channel")
                            await ctx.send("AutoErrorReport is not working, please mention this while"
                                           " speaking to support.")
                        else:
                            botlogger.info("Reload: Errite channel successfully established, now sending message")
                            await support_channel.send("Exception experienced while reloading\n"
                                                       "**Server Info:**\n" +
                                                       "Current Server Name: " + ctx.guild.name +
                                                       "\nServer Id: " + str(ctx.guild.id) +
                                                       "\nInternal Name: " + discord_server +
                                                       "\nEGServer: " + server +
                                                       "\nServer Location: " + location +
                                                       "\nException: " + e)
                            botlogger.info("Reload: Errite SOS Reload Message successfully sent")
                else:
                    botlogger.info("Reload: " + extension + "successfully reloaded")
                    await ctx.send('**`SUCCESSFULLY RELOADED `' + extension + '**')


@client.command()
@has_permissions(administrator=True)
async def erritetoggle(ctx):
    if ctx.guild is None:
        return
    if ctx.guild.id == guildid:
        if not publicmode:
            if errite:
                update_errite(False)
                await ctx.send("Errite has been toggled to false")
                await ctx.author.send("Originally, errite was to set to true despite " +
                                      "publicmode being false. If you are using the public DeviantCord bot, contact " +
                                      "DeviantCord support **IMMEDIATELY! ** If you are using self hosting" +
                                      "check the bots config.json file to make sure the settings are correct.")
            if not errite:
                await ctx.author.send("The errite property for the bot in config.json is used to tell whether the bot" +
                                      " should use certain lines of code that were designed only for the DeviantCord " +
                                      "public bot. If you are running a self host bot use logchannels instead.  " +
                                      "\n If you are using the DeviantCord public bot and see this message contact" +
                                      "DeviantCord support **IMMEDIATELY**")
        if publicmode:
            if errite:
                update_errite(False)
                await ctx.send("You have opted out of Errite's Auto Error Reporting")
            elif not errite:
                update_errite(True)
                await ctx.send("You have opted back into Errite's Auto Error Reporting")


@setprefix.error
async def setprefix_errorhandler(ctx, error):
    if ctx.guild is None:
        return
    if ctx.guild.id == guildid:
        permitted = True
    elif not publicmode:
        permitted = True
    else:
        return;
    if permitted:
        print("Entered Permitted")
        if isinstance(error, commands.NoPrivateMessage):
            return;
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'suppliedprefix':
                await ctx.send(
                    "Error: No prefix argument found, use " + prefix + "help for more information")
        elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            if error.param.name == 'suppliedprefix':
                await ctx.send(
                        "Error: No prefix argument found, use " + prefix + "help for more information")
        elif isinstance(error,commands.MissingPermissions):
                return;
        elif isinstance(error, commands.errors.NoPrivateMessage):
                return;

def error_handler(loop, context):
    print("Exception: ", context['exception'])
    if str(context['exception']) == "HTTP Error 401: Unauthorized":

        print("Your DA info is invalid, please check client.json to see if it matches your DA developer page")
        loop.stop()
        try:
            exit(211)
        except SystemExit:
            os._exit(211)
    if str(context['exception']) == "HTTP Error 400: Bad request":

        print("You need to setup your DA info for the bot, otherwise please check client.json")
        loop.stop()
        try:
            exit(210)
        except SystemExit:
            os._exit(210)
    else:
        print("Exception encountered: ", context['exception'])


client.remove_command("setlogchannel")
client.run(sensitiveData["discord-token"])
