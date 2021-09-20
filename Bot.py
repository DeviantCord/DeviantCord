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

import json
import os
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor

import discord
import psycopg2
import datetime
import sys, traceback
import logging
from sentry_sdk import configure_scope, set_context, set_extra, capture_exception
import sentry_sdk
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from discord.ext import commands
from discord.ext.commands import has_permissions
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from errite.da.jsonTools import updateprefix, updatelogchannel, update_errite
from errite.config.configManager import createConfig, createSensitiveConfig
from errite.tools.mis import fileExists
from errite.config.converter import convert
from errite.psql.sqlManager import grab_sql
from errite.deviantcord.timeTools import prefixTimeOutSatisfied
from os import listdir
from os.path import isfile, join

# DeviantCord Message Variables (Not all are here)
invalid_cog_errite = "Invalid cog found on reload for discord server "
print("Starting DeviantCord bt-3.0.4")
print("If this causes a HTTP 401 Error when trying to load daCommands your DeviantArt info is wrong. Set it in client.json")
started = True
configData = {}
DBData = None
sensitiveData = {}
server_prefixes = {}
server_prefixes["guilds"] = []
errite = False
prefix = None
passed = True
roleid = None
work = False
stopCollision = False
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
botlogger.setLevel(logging.INFO)
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
                    use_sentry = configData["sentry-enabled"]
                    if use_sentry:
                        sentry_url = configData["sentry-url"]
                        sentry_sdk.init(sentry_url, integrations=[AioHttpIntegration()])
                    sensitiveData = json.load(clientjsonFile)
                    configjsonFile.close()
                    clientjsonFile.close()
                    if not sensitiveData["da-client-id"]  == "id here":
                        if not sensitiveData["da-secret"] == "secret":
                            passedJson = True
        if fileExists("db.json"):
            with open("db.json") as BotdbJsonFile:
                dbInfo = json.load(BotdbJsonFile)
                database_name = dbInfo["database-name"]
                database_host = dbInfo["database-host"]
                database_host2 = dbInfo["database-host2"]
                database_host3 = dbInfo["database-host3"]
                database_password = dbInfo["database-password"]
                database_port = dbInfo["database-port"]
                database_user = dbInfo["database-username"]
                if database_host2 == "none":
                    connect_str = "dbname='" + database_name + "' user='" + database_user \
                                  + "'host='" + database_host + "' " + \
                                  "'port='" + str(database_port) + "password='" + database_password + "'"
                elif database_host3 == "none":
                    connect_str = "dbname='" + database_name + "' user='" + database_user \
                                  + "'host='" + database_host + "," + database_host2 + "' " + \
                                  "'port='" + str(database_port) + "password='" + database_password + "'"
                else:
                    connect_str = "dbname='" + database_name + "' user='" + database_user \
                                  + "'host='" + database_host + "," + database_host2 + "," + database_host3 + "'" + \
                                  "port='" + str(database_port) + "'password='" + database_password + "'"
                print("DeviantCord Main Bot component now connecting to DB")
                db_connection = psycopg2.connect(connect_str)

def grab_prefix(bot, msg):
    if msg.guild is None:
        return "$"
    if not msg.guild.id in server_prefixes:
        obt_prefix = db_connection.cursor()
        sql = grab_sql("grab_server_info")
        obt_prefix.execute(sql,(msg.guild.id,))
        obt_results = obt_prefix.fetchone()
        if obt_results is not None:
            prefix = obt_results[0][0]
            #Initialize Dictionary
            server_prefixes[msg.guild.id] = {}
            server_prefixes[msg.guild.id]["prefix"] = prefix
            timestr = datetime.datetime.now()
            server_prefixes[msg.guild.id]["last-use"] = timestr
            server_prefixes["guilds"].append(msg.guild.id)
            obt_prefix.close()
            return server_prefixes[msg.guild.id]["prefix"]
        if obt_results is None:
            #If for some reason the server is not in the database, then the obt_results will be none
            return "~"
    elif msg.guild.id in server_prefixes:
        timestr = datetime.datetime.now()
        server_prefixes[msg.guild.id]["last-use"] = timestr
        return server_prefixes[msg.guild.id]["prefix"]

async def timeout_prefixes():
    await client.wait_until_ready()

    while not client.is_closed():
        print("Time out started")
        for entry in server_prefixes["guilds"]:
            if prefixTimeOutSatisfied(server_prefixes[entry]["last-use"]):
                print("Deleted " + str(entry))
                del server_prefixes[entry]
                server_prefixes["guilds"].remove(entry)
        print("Timeout sleeping")
        await asyncio.sleep(900)

if passedJson == True:
    prefix = configData["prefix"]
    intents = discord.Intents(messages=True, guilds=True)
    client = commands.Bot(command_prefix=grab_prefix, intents=intents)

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
    stop_duplicaterecovery = False
    server = configData["server"]
    # The variable below this is referred to as client in all other python files. Its because client is already used
    # that this is different. It refers to the name of the Discord Server internally on Errite Servers.
    discord_server = configData["client"]
    client.loop.create_task(timeout_prefixes())
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

async def setRecover(input:bool):
    stopCollision = input
async def recoverConnection():
    toggle = False
    if not stopCollision:
        toggle = True
        setRecover(True)
    if toggle:
        await asyncio.sleep(120)
        if database_host2 == "none":
            connect_str = "dbname='" + database_name + "' user='" + database_user \
                          + "'host='" + database_host + "' " + \
                          "password='" + database_password + "'"
        elif database_host3 == "none":
            connect_str = "dbname='" + database_name + "' user='" + database_user \
                          + "'host='" + database_host + "," + database_host2 + "' " + \
                          "password='" + database_password + "'"
        else:
            connect_str = "dbname='" + database_name + "' user='" + database_user \
                          + "'host='" + database_host + "," + database_host2 + "," + database_host3 + "' " + \
                          "password='" + database_password + "'"
        print("Connecting to database")
        db_connection = psycopg2.connect(connect_str)
        setRecover(False)

@client.event
async def on_guild_join(guild):
    print("Test")
    sql = grab_sql("new_server")
    ns_cursor = db_connection.cursor()
    await client.loop.run_in_executor(ThreadPoolExecutor(), ns_cursor.execute, sql,(guild.id, '~', False, 0,))
    await asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(), db_connection.commit)

@client.event
async def on_guild_remove(guild):
    print("Test")
    sql = grab_sql("delete_server_config")
    delserver_cursor = db_connection.cursor()
    await client.loop.run_in_executor(ThreadPoolExecutor(), delserver_cursor.execute, sql,(guild.id,))
    sql = grab_sql("delete_server_data")
    await client.loop.run_in_executor(ThreadPoolExecutor(), delserver_cursor.execute, sql, (guild.id,))
    sql = grab_sql("cleanup_journal_Listener_leave")
    await client.loop.run_in_executor(ThreadPoolExecutor(), delserver_cursor.execute, sql,(guild.id,))
    await asyncio.get_event_loop().run_in_executor(ThreadPoolExecutor(), db_connection.commit)



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def setprefix(ctx, suppliedprefix):
    skiprolecheck = False
    if ctx.guild is None:
        return;
    elif not ctx.guild is None:
        if ctx.author.guild_permissions.administrator:
            print("Entered")
            setup_cursor = db_connection.cursor()
            sql = grab_sql("update_prefix")
            timestr = datetime.datetime.now()
            await client.loop.run_in_executor(ThreadPoolExecutor(), setup_cursor.execute, sql,(suppliedprefix, timestr, ctx.guild.id,))
            print("Committing")
            await client.loop.run_in_executor(ThreadPoolExecutor(), db_connection.commit)
            server_prefixes[ctx.guild.id]["prefix"] = suppliedprefix
            await ctx.send("Prefix has been updated.")
        elif not ctx.author.guild_permissions.administrator:
            await ctx.send("You need to have a rank with Administrator permissions")


@setprefix.error
async def setprefix_errorhandler(ctx, error):
    if ctx.guild is None:
        return
    if isinstance(error, commands.NoPrivateMessage):
        return;
    elif isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'suppliedprefix':
            await ctx.send(
                "Error: No prefix argument found, use the help command for more information")
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        if error.param.name == 'suppliedprefix':
            await ctx.send(
                "Error: No prefix argument found, use the help command for more information")
    elif isinstance(error,commands.MissingPermissions):
            return;
    elif isinstance(error, commands.errors.NoPrivateMessage):
            return;
    else:
        with configure_scope() as scope:
            scope.set_extra("command", ctx.command.name)
            scope.set_extra("discord-guild", ctx.guild.name)
            scope.set_extra("guild-id", ctx.guild.id)
            scope.set_extra("channel-id", ctx.channel.id)
            scope.set_extra("channel-name", ctx.channel.name)
            capture_exception(error)


def error_handler(loop, context):
    print("Exception: ", context['exception'])
    if str(context['exception']).find("psycopg2") > -1:
        botlogger.error("psycopg2 exception encountered")
        client.loop.create_task(recoverConnection())
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
