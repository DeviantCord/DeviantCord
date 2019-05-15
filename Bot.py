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
from errite.da.jsonTools import updateprefix, updatelogchannel
from errite.config.configManager import createConfig, createSensitiveConfig
from errite.tools.mis import fileExists
from errite.config.converter import convert
from os import listdir
from os.path import isfile, join
print("Starting DeviantBot bt-1.2.1")
print("If this causes a HTTP 401 Error when trying to load daCommands your DeviantArt info is wrong. Set it in client.json")
started = True
configData = {}
sensitiveData = {}
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
    print("IN")
    skiprolecheck = False
    if ctx.guild is None:
        return;
    elif ctx.guild.id == guildid:
        permitted = True
    elif not publicmode:
        permitted = True
    if permitted:
        updateprefix(suppliedprefix)
        try:
            prefix = suppliedprefix
            client.command_prefix = prefix
            client.unload_extension(cogs_dir + "." + "daCommands")
            client.load_extension(cogs_dir + "." + "daCommands")
            await ctx.send("Prefix updated to " + prefix)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

@client.command()
@has_permissions(administrator=True)
async def reload(ctx):
    """Command which Reloads a Module.
    Remember to use dot path. e.g: cogs.owner"""

    try:
        client.unload_extension(cogs_dir + "." + "daCommands")
        client.load_extension(cogs_dir + "." + "daCommands")
    except Exception as e:
        await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
    else:
        await ctx.send('**`SUCCESS`**')


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
