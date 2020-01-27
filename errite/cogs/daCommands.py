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
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from pythonjsonlogger import jsonlogger
from logging.handlers import TimedRotatingFileHandler
import asyncio
import datetime
import logging
from sentry_sdk import configure_scope, set_context, set_extra, capture_exception
import sentry_sdk
from discord.ext import commands
import psycopg2
import psycopg2.errors
from discord.ext.commands import has_permissions, guild_only, CommandNotFound, BadArgument
import errite.da.daParser as dp
from errite.deviantcord.timeTools import prefixTimeOutSatisfied
from errite.psql.taskManager import syncListeners, addtask, addalltask
from errite.psql.sourceManager import updateSources, updateallfolders, addsource, verifySourceExistance, \
    verifySourceExistanceExtra, verifySourceExistanceAll, addallsource
from errite.psql.sqlManager import grab_sql
from errite.erritediscord.discordTools import sendDeviationNotifications, createDeviationListString, sendListMessage, \
    convertRoleID, convertChannelID
from errite.config.configManager import createConfig, createSensitiveConfig
from errite.tools.mis import fileExists
import urllib


class daCog(commands.Cog):
    """The Deviant Art component class for DeviantCord"""

    def __init__(self, bot):
        self.clientid = None
        self.db_connection = None
        self.connection_info = None
        self.database_active = False
        self.dbInfo = None
        self.database_name = None
        self.database_host = None
        self.database_user = None
        self.database_password = None
        self.database_port = None
        self.clientsecret = None
        self.guildid = None
        self.enablesr = False
        self.jsonlock = False
        self.min_roles = {}
        self.min_roles["guilds"] = []
        self.roleid = 0
        self.failedlogincount = 0
        self.publicmode = None
        self.datevar = datetime.datetime.now().strftime("%Y-%m-%d%H%M%S")
        self.whiletrigger = False
        self.logname = "deviantcog"

        self.deviantlogger = logging.getLogger("deviantcog")
        self.deviantlogger.setLevel(logging.INFO)
        self.dlhandler = TimedRotatingFileHandler(self.logname, when='h', interval=12, backupCount=2000,
                                                  encoding='utf-8')
        supported_keys = [
            'asctime',
            'created',
            'filename',
            'funcName',
            'levelname',
            'levelno',
            'lineno',
            'module',
            'message',
            'process',
            'processName',
            'relativeCreated',
            'thread',
            'threadName'
        ]

        log_format = lambda x: ['%({0:s})'.format(i) for i in x]
        custom_format = ' '.join(log_format(supported_keys))
        self.formatter = jsonlogger.JsonFormatter(custom_format)
        self.dlhandler.setFormatter(self.formatter)
        self.deviantlogger.addHandler(self.dlhandler)

        self.time = 900
        self.token = None
        self.prefix = "$"
        self.bot = bot
        passed = True
        passedJson = False;
        if fileExists("config.json") == False:
            createConfig()
        if fileExists("client.json") == False:
            createSensitiveConfig()
            print("You need to set your login information!")
            self.deviantlogger.error("You need to set your login information!")
            self.deviantlogger.info("client.json created. You need to set your login information")
            passed = False

        if passed == True:
            self.deviantlogger.info("Startup JSON Check passed")
            if fileExists("config.json") == True:
                if fileExists("client.json") == True:
                    with open("config.json", "r") as configjsonFile:
                        with open("client.json", "r") as clientjsonFile:
                            configData = json.load(configjsonFile)
                            use_sentry = configData["sentry-enabled"]
                            if use_sentry:
                                sentry_url = configData["sentry-url"]
                                sentry_sdk.init(sentry_url)
                            sensitiveData = json.load(clientjsonFile)
                            configjsonFile.close()
                            clientjsonFile.close()
                            if sensitiveData["da-client-id"] is not "id here":
                                if sensitiveData["da-secret"] is not "secret":
                                    self.clientsecret = sensitiveData["da-secret"]
                                    self.clientid = sensitiveData["da-client-id"]
                                    self.passedJson = True
            if fileExists("db.json"):
                self.database_active = True
                with open("db.json", "r") as dbJson:
                    self.dbInfo = json.load(dbJson)

        if self.passedJson == True:
            self.deviantlogger.info("Setting config variables")
            # WEB API
            self.clientsecret = sensitiveData["da-secret"]
            self.clientid = sensitiveData["da-client-id"]
            self.token = dp.getToken(self.clientsecret, self.clientid)
            self.publicmode = configData["publicmode"]
            self.enablesr = configData["rolesetup-enabled"]
            self.roleid = configData["roleid"]
            self.logchannelid = configData["logchannelid"]
            self.guildid = configData["guildid"]
            self.prefix = configData["prefix"]
            self.time = configData["sync-time"]
            # Database Specific Options
            self.deviantlogger.info("Setting Database Variables")
            self.database_name = self.dbInfo["database-name"]
            self.database_host = self.dbInfo["database-host"]
            self.database_host2 = self.dbInfo["database-host2"]
            self.database_host3 = self.dbInfo["database-host3"]
            self.database_password = self.dbInfo["database-password"]
            self.database_user = self.dbInfo["database-username"]
            self.stop_duplicaterecovery = False
            if self.database_host2 == "none":
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "' " + \
                              "password='" + self.database_password + "'"
            elif self.database_host3 == "none":
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "," + self.database_host2 + "' " + \
                              "password='" + self.database_password + "'"
            else:
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "," + self.database_host2 + "," + self.database_host3 + "' " + \
                              "password='" + self.database_password + "'"
            print("Connecting to database")
            self.db_connection = psycopg2.connect(connect_str)
            # Errite LLC Specific Options THIS is for DeviantCord Public Hosting, these settings are what
            # stops the bot from executing code meant for DeviantCord Public Hosting only
            self.errite = configData["errite"]
            self.errite_channel = configData["errite-channel"]
        self.deviantlogger.info("Now creating tasks...")
        self.bot.loop.create_task(self.getNewToken())
        self.bot.loop.set_exception_handler(self.error_handler)
        self.bot.loop.create_task(self.syncGalleries())
        self.bot.loop.create_task(self.timeout_ranks())

    async def getNewToken(self):
        """
        Gets a new token from DeviantArt with no params, grabs the clientid and clientsecret from the class file.
        This function is ran every 40 minutes. DA's tokens last 60.
        """
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            print("Getting new token")
            self.deviantlogger.info("TASK: Obtaining new token...")
            self.token = dp.getToken(self.clientsecret, self.clientid)
            await asyncio.sleep(2400)

    async def recoverConnection(self):
        toggle = False
        if not self.stop_duplicaterecovery:
            toggle = True
            self.stop_duplicaterecovery = True
        if toggle:
            self.deviantlogger.info("Recovery Connection invoked, Waiting 60 seconds.")
            await asyncio.sleep(120)
            if self.database_host2 == "none":
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "' " + \
                              "password='" + self.database_password + "'"
            elif self.database_host3 == "none":
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "," + self.database_host2 + "' " + \
                              "password='" + self.database_password + "'"
            else:
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "," + self.database_host2 + "," + self.database_host3 + "' " + \
                              "password='" + self.database_password + "'"
            print("Connecting to database")
            self.db_connection = psycopg2.connect(connect_str)
            self.stop_duplicaterecovery = False

    async def manualgetNewToken(self):
        """
        Gets a new token from DeviantArt with no params, grabs the clientid and clientsecret from the class file.
        This function is only ran when a token error occurs having to do with async tasks also failing.
        """
        self.deviantlogger.info("ManualGetToken: ManualGetToken invoked, Now sleeping for 20 minutes...")
        await asyncio.sleep(1200)
        self.deviantlogger.info("ManualGetToken: Getting new token")
        self.token = dp.getToken(self.clientsecret, self.clientid)
        self.deviantlogger.info("ManualGetToken: Recreating Tasks...")
        self.deviantlogger.info("ManualGetToken: Creating getNewToken...")
        self.bot.loop.create_task(self.getNewToken())
        self.deviantlogger.info("ManualGetToken: Creating syncGalleries...")
        self.bot.loop.create_task(self.syncGalleries())

    async def fix_error(self, amount):
        print("Waiting")
        await asyncio.sleep(amount)
        print("Past")
        if sys.version_info >= (3, 7):
            pending = asyncio.all_tasks()
        elif sys.version_info >= (3, 5, 2):
            pending = asyncio.Task.all_tasks()

        token_present = False
        sg_present = False

        print("Starting dump")
        pending = asyncio.Task.all_tasks()
        for element in pending:
            if str(element).find("coro=<daCog.getNewToken()") > -1:
                print("Found getNewToken")
                token_present = True
            if str(element).find("coro=<daCog.syncGalleries()") > -1:
                print("Found SyncGalleries")
                sg_present = True
        if not token_present:
            self.deviantlogger.warning(
                "manualGetToken: Detected that getNewToken task is dead, creating new task")
            self.bot.loop.create_task(self.getNewToken())
            self.deviantlogger.warning("manualGetToken: getNewToken created!")
        if not sg_present:
            print("Inside sg ")
            self.deviantlogger.warning("manualGetToken: Detected that syncGalleries task is dead, creating new task")
            self.bot.loop.create_task(self.syncGalleries())
            print("Finish!")
            self.deviantlogger.warning("manualGetToken: syncGalleries created!")

        async def debuggetNewToken(self):
            """
            Gets a new token from DeviantArt with no params, grabs the clientid and clientsecret from the class file.
            This function is only ran when a token error occurs having to do with async tasks also failing.
            """
            self.deviantlogger.info("ManualGetToken: Creating syncGalleries...")
            await asyncio.sleep(400)
            self.bot.loop.create_task(self.syncGalleries())

    async def softTokenRenewal(self):
        """
        Gets a new token from DeviantArt with no params, grabs the clientid and clientsecret from the class file.
        This function is only ran when a token error occurs and fixes the token only!.

        This is usually the second method ran to try to fix a token related issue that doesn't involve a failure of
        automated async tasks.
        """
        self.deviantlogger.info("softTokenRenewall: softTokenRenewalInvoked invoked, Now sleeping for 20 minutes...")
        await asyncio.sleep(1200)
        self.deviantlogger.info("softTokenRenewal: Getting new token")
        self.token = dp.getToken(self.clientsecret, self.clientid)
        self.failedlogincount = 0

    async def instantTokenRenewal(self):
        """
        Gets a new token without any async delays from DeviantArt, when a 403 is returned this is the first
        method ran to try to fix the issue.
        """

        self.deviantlogger.info("instantTokenRenewal: invoked and getting new token")
        try:
            self.token = dp.getToken(self.clientsecret, self.clientid)
        except urllib.error.HTTPError as Err:
            if Err.code == 403:
                self.deviantlogger.error("instantTokenRenewal: instant token renewal returned a 403. "
                                         "will now try a softTokenRenewal")
                self.deviantlogger.exception(Err)
                await self.softTokenRenewal()
                self.failedlogincount = 0
            else:
                self.deviantlogger.error("HTTP Error " + str(Err.code) + "encountered")
                self.deviantlogger.exception(Err)
                await self.softTokenRenewal()

    async def instantTokenDiagnosisRenewal(self):
        """
        Gets a new token without any async delays from DeviantArt, and returns a bool if successful
        """

        self.deviantlogger.info("instantTokenRenewal: invoked and getting new token")
        try:
            self.token = dp.getToken(self.clientsecret, self.clientid)
            return True
        except urllib.error.HTTPError as Err:
            return False

    async def rateLimitMeasure(self):
        """
        Triggered when DA sends a Rate Limit response, this tones down SyncGalleries
        """
        self.deviantlogger.info("rateLimitMeasure: Invoked, now sleeping for 40 minutes")
        await asyncio.sleep(2400)
        self.bot.loop.create_task(self.getNewToken())
        self.bot.loop.create_task(self.syncGalleries())

    async def grab_min_role(self, msg):
        if not msg.guild.id in self.min_roles:
            obt_rank = self.db_connection.cursor()
            sql = grab_sql("grab_server_info")
            print("Before execute")
            guild_id = msg.guild.id

            loop = asyncio.get_event_loop()
            # await loop.run_in_executor(ThreadPoolExecutor(), setup_cursor.execute, sql,
            #                          (roleid, timestr, ctx.guild.id,))
            await loop.run_in_executor(ThreadPoolExecutor(), obt_rank.execute, sql, (guild_id,))
            print("After execute")
            # obt_rank.execute(sql, (msg.guild.id,))
            obt_results = await loop.run_in_executor(ThreadPoolExecutor(), obt_rank.fetchone)
            if obt_results is not None:
                prefix = obt_results[0]
                rank = obt_results[1]
                # Initialize Dictionary
                self.min_roles[msg.guild.id] = {}
                self.min_roles[msg.guild.id]["prefix"] = prefix
                self.min_roles[msg.guild.id]["rank"] = rank
                timestr = datetime.datetime.now()
                self.min_roles[msg.guild.id]["last-use"] = timestr
                self.min_roles["guilds"].append(msg.guild.id)
                obt_rank.close()
                print("Returning Role")
                return self.min_roles[msg.guild.id]["rank"]
            if obt_results is None:
                # If for some reason the server is not in the database, then the obt_results will be none
                print("Returning none")
                return None
        elif msg.guild.id in self.min_roles:
            timestr = datetime.datetime.now()
            self.min_roles[msg.guild.id]["last-use"] = timestr
            print("Returning role")
            return int(self.min_roles[msg.guild.id]["rank"])

    async def timeout_ranks(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            print("Time out started")
            for entry in self.min_roles["guilds"]:
                if prefixTimeOutSatisfied(self.min_roles[entry]["last-use"]):
                    print("Deleted " + str(entry))
                    del self.min_roles[entry]
                    self.min_roles["guilds"].remove(entry)
            print("Timeout sleeping")
            await asyncio.sleep(900)

    async def grab_prefix(self, msg):
        if not msg.guild.id in self.min_roles:
            obt_rank = self.db_connection.cursor()
            sql = grab_sql("grab_server_info")
            print("Before execute")
            guild_id = msg.guild.id

            loop = asyncio.get_event_loop()
            # await loop.run_in_executor(ThreadPoolExecutor(), setup_cursor.execute, sql,
            #                          (roleid, timestr, ctx.guild.id,))
            await loop.run_in_executor(ThreadPoolExecutor(), obt_rank.execute, sql, (guild_id,))
            print("After execute")
            # obt_rank.execute(sql, (msg.guild.id,))
            obt_results = await loop.run_in_executor(ThreadPoolExecutor(), obt_rank.fetchone)
            if obt_results is not None:
                prefix = obt_results[0]
                rank = obt_results[1]
                # Initialize Dictionary
                self.min_roles[msg.guild.id] = {}
                self.min_roles[msg.guild.id]["prefix"] = prefix
                self.min_roles[msg.guild.id]["rank"] = rank
                timestr = datetime.datetime.now()
                self.min_roles[msg.guild.id]["last-use"] = timestr
                self.min_roles["guilds"].append(msg.guild.id)
                obt_rank.close()
                print("Returning Prefix")
                return str(self.min_roles[msg.guild.id]["prefix"])
            if obt_results is None:
                # If for some reason the server is not in the database, then the obt_results will be none
                print("Returning none")
                return None
        elif msg.guild.id in self.min_roles:
            timestr = datetime.datetime.now()
            self.min_roles[msg.guild.id]["last-use"] = timestr
            print("Returning role")
            return str(self.min_roles[msg.guild.id]["prefix"])

    async def syncGalleries(self):

        """
        Checks programmed gallery folders for Deviations. This is the method that is ran to trigger every x minutes
        depending on what the user has it configured to.
        """
        delete_notification_tasks = """ DELETE FROM deviantcord.deviation_notifications WHERE id = %s"""
        print("SyncGalleries called")
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            notifications_ids_completed = None
            loop = asyncio.get_event_loop()
            get_cursor = self.db_connection.cursor()
            get_query = "select * from deviantcord.deviation_data"
            await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.execute, get_query)
            obt_results = await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.fetchall)
            source_cursor = self.db_connection.cursor()
            await loop.run_in_executor(ThreadPoolExecutor(), updateSources, source_cursor, self.db_connection,
                                       obt_results, self.token)
            await loop.run_in_executor(ThreadPoolExecutor(), self.db_connection.commit)
            get_query = "SELECT * from deviantcord.deviation_data_all"
            await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.execute, get_query)
            obt_results = await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.fetchall)
            await loop.run_in_executor(ThreadPoolExecutor(), updateallfolders, source_cursor, self.db_connection,
                                       obt_results, self.token)
            task_cursor = self.db_connection.cursor()
            print("If it happened before this then you got it")
            await loop.run_in_executor(ThreadPoolExecutor(), syncListeners, self.db_connection, task_cursor,
                                       source_cursor)
            # do_normal_tasks_query = "SELECT * from deviantcord.deviation_notifications where inverse = false"
            do_normal_tasks_query = "SELECT * from deviantcord.deviation_notifications where inverse = false"
            await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.execute, do_normal_tasks_query)
            obt_results = await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.fetchall)
            notifications_ids_completed = await sendDeviationNotifications(self.bot, obt_results)
            del_notifications = self.db_connection.cursor()
            for id in notifications_ids_completed:
                # id  needs to be a tuple in order for this to work
                del_notifications.execute(delete_notification_tasks, (id,))
            await loop.run_in_executor(ThreadPoolExecutor(), self.db_connection.commit)
            sql = """SELECT * from deviantcord.deviation_notifications WHERE inverse = true ORDER BY notif_creation DESC """
            await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.execute, sql)
            obt_results = await loop.run_in_executor(ThreadPoolExecutor(), get_cursor.fetchall)
            notifications_ids_completed = await sendDeviationNotifications(self.bot, obt_results)
            for id in notifications_ids_completed:
                # id  needs to be a tuple in order for this to work
                del_notifications.execute(delete_notification_tasks, (id,))
            await loop.run_in_executor(ThreadPoolExecutor(), self.db_connection.commit)
            source_cursor.close()
            get_cursor.close()
            await asyncio.sleep(1500)

    @commands.command()
    async def support(self, ctx):
        await ctx.message.author.send("Here is the URL to the official DeviantCord Discord server " +
                                      "\nhttps://discord.gg/ubmkcsk")

    @commands.command()
    async def help(self, ctx):
        if ctx.guild is None:
            return;

        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)
        obtained_prefix = await self.grab_prefix(ctx)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if obtained_prefix is None:
            obtained_prefix = "~"
        glossary = "** __ DeviantCord Glossary__ ** \n **Inverse:** " \
                   "- If answered true, newest deviations will be checked from the top of the folder instead of the bottom.\n " \
                   "**Hybrid:** - If answered true, the opposite of the inverse given will also be checked in addition to the given inverse" \
                   "folders should be read from the top instead of the bottom.\n" \
                   "** Mature:** - Marked true as to whether Deviations marked as mature on DA should be posted. \n **NOTE:** This includes both" \
                   " mature options Moderate and Strict on DA. Regardless of which one is marked the bot will treat it as mature.\n" \
                   "**NOTE:** arguments with quotes around it require quotes when the command is executed and is **Case Sensitive**" \
                   " the artists name and folder need to be exact!\n"
        await ctx.send(glossary)
        text = "** __DeviantCord Help Guide__**\n **" + obtained_prefix + \
               "help** - Gives a list of command with explaination\n**NOTE: Inverse means that newest deviations are at the top, instead of the bottom. Use true or false to answer it**\n**" + \
               obtained_prefix + "addfolder** *\"<artist_username>\"* *\"<folder>\"* *<channel_id>* *<inverse>* *<hybrid>* *<mature>* - Adds a folder listener fo for the bot to notify user of new deviations in the specified channel\n**" + \
               obtained_prefix + "addallfolder** *\"<artist_username>\"* *<channel_id>* *<mature>* - Used to add an allfolder listener that listens for any deviations from the artist.\n **" + \
               obtained_prefix + "deleteallfolder** *\"<artist_username>\"* *<channelid>* - Deletes allfolder listener and removes it from artdata\n **" + \
               obtained_prefix + "deletefolder** *\"<artist_username>\"* *\"<folder>\"* *<channelid>* - Deletes the listener for the folder and erases it from artdata\n **" + \
               obtained_prefix + "listfolders** - Lists all the current folder listeners that the bot is listening to. \n **" + \
               obtained_prefix + "updatehybrid** *\"<artist_username>\"* *\"<folder>\"* *<hybrid>* *<channelid>*- Sets the hybrid property of an existing folder listener \n **" + \
               obtained_prefix + "updateinverse** *\"<artist_username>\"* *\"<folder>\"* *<inverse>* *<channelid>* - Updates the inverse property of a existing folder listener\n" + \
               "**" + obtained_prefix + "updatechannel** *\"<artist_username>\"* *\"<folder>\"* *<newchannelid>* *<oldchannelid>* - Updates the discord channel that notifications will be posted for an existing folder listener\n" + \
               "**" + obtained_prefix + "support** - DM's you a server invite to the official DeviantCord Support server\n" + \
               "** __ADMIN COMMANDS__** \n" + \
               "**" + obtained_prefix + "setprefix** *<prefix>* - Updates the prefix \n" \
                                        "**" + obtained_prefix + "setuprole** *<roleid>* - Sets the minimum roleid to " \
                                                                 "use DeviantCord commands."
        await ctx.send(text)

    @commands.command()
    async def addallfolder(self, ctx, artistname, channelid, mature: bool):
        print("Invoked")
        if ctx.guild is None:
            print("Null guild")
            return;
        useConvChannelID = False
        print("After test")
        min_rank = await self.grab_min_role(ctx)
        print("After")
        obtained_role = ctx.guild.get_role(min_rank)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        useConvChannelID = False
        if isinstance(channelid, str):
            convChannelId = await convertChannelID(channelid, ctx)
            if convChannelId == 0:
                await ctx.send("Invalid channelID")
                return
            else:
                useConvChannelID = True
                channel = self.bot.get_channel(convChannelId)
        elif isinstance(channelid, int):
            channel = self.bot.get_channel(channelid)
            if channel is None:
                await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
                return
        else:
            await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
            return
        if not channel.guild.id == ctx.guild.id:
            return
        if mature:
            if not channel.is_nsfw():
                await ctx.send("Folders marked as mature must be in a NSFW channel!")
                return
        sql = grab_sql("duplicate_all_check")
        check_listener_cursor = self.db_connection.cursor()
        loop = asyncio.get_event_loop()
        if not useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener_cursor.execute,
                                       sql, (channelid, ctx.guild.id, artistname, "All Folder",))
        elif useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener_cursor.execute,
                                       sql, (convChannelId, ctx.guild.id, artistname, "All Folder",))
        duplicate_results = await loop.run_in_executor(ThreadPoolExecutor(), check_listener_cursor.fetchone)
        if duplicate_results is not None:
            await ctx.send("You already have a listener for this folder and artist in this channel. You can only have "
                           "one. If you want to listen for both inverse and noninverse set hybrid for the listener"
                           "to true using the updatehybrid command")
            return
        source_exists = verifySourceExistanceAll(artistname, mature, self.db_connection)

        if not source_exists:
            await ctx.send("Importing All Folder, this may take a bit.")
            passedAllFolder = False
            passedGroupCheck = True
            try:
                allfolderData = dp.getAllFolderArrayResponse(artistname, mature, self.token, mature)
                passedAllFolder = True
            except urllib.error.HTTPError as AllURLError:
                if AllURLError.code == 400:
                    await ctx.send("Could not find an allfolder under this user. Is the username correct? It need to be"
                                   " exactly as it is on DA.")
                    check_listener_cursor.close()
                    return
            try:
                userinfo = dp.userInfoResponse(artistname, self.token, True)
                passedGroupCheck = True
            except urllib.error.HTTPError as err:
                if err.code == 400:
                    if not passedAllFolder:
                        await ctx.send("A bug has occured. Contact DeviantCord Support and reference error code 04")
                    if passedAllFolder:
                        await ctx.send("You have designated a group user. Groups do not have all folders."
                                       " Use the addfolder command instead. Unfortunately this is a limitation by DA :(")
                    print("This is from a group, setting dummy profile picture")
                    pp_picture = "none"
                emptyfolder = True
            loop = asyncio.get_event_loop()
            await ctx.send("Importing this folder for first time, this may take a bit.")
            await loop.run_in_executor(ThreadPoolExecutor(), addallsource, allfolderData, artistname,
                                       self.db_connection,
                                       mature)
            print("Finished adding source")
            if useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addalltask, ctx.guild.id, convChannelId, artistname,
                                           mature, self.db_connection)
            elif not useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addalltask, ctx.guild.id, channelid, artistname,
                                           mature, self.db_connection)
        else:
            loop = asyncio.get_event_loop()
            if useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addalltask, ctx.guild.id, convChannelId, artistname,
                                           mature,
                                           self.db_connection)
            elif not useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addalltask, ctx.guild.id, channelid, artistname,
                                           mature,
                                           self.db_connection)
        await ctx.send(
            "Listener added for allfolder " + " for artist " + artistname + " Reminder: The bot only checks for Deviations every 25 to 30 minutes from when the bot is started!")

    @commands.command()
    async def setuprole(self, ctx, roleid):
        if ctx.guild is None:
            return
        elif not ctx.guild is None:
            if ctx.author.guild_permissions.administrator:
                useConvID = False
                if isinstance(roleid, str):
                    convRoleId = await convertRoleID(roleid, ctx)
                    if convRoleId == 0:
                        await ctx.send("Invalid RoleId, try mentioning the bot or using the numerical roleid. You can "
                                       "grab the numerical id by putting a \ infront of the mention and putting that id")
                        return
                    else:
                        useConvID = True
                elif not isinstance(roleid, int):
                    await ctx.send("Invalid RoleID, try mentioning the bot or using the numerical roleid. You can "
                                   "grab the numerical id by putting a \ infront of the mention and putting that id")
                    return
                else:
                    await ctx.send("Invalid roleid")
                    return
                if useConvID:
                    role_obj = ctx.guild.get_role(convRoleId)
                else:
                    role_obj = ctx.guild.get_role(roleid)
                if role_obj is None:
                    await ctx.send("Invalid RoleID, try mentioning the bot or using the numerical roleid. You can "
                                   "grab the numerical id by putting a \ infront of the mention and putting that id")
                    return
                if ctx.author.top_role < role_obj:
                    await ctx.send("You specified a minimum rank for the bot higher then your highest role "
                                   "on the server. The minimum rank needs to be lower or equal to your highest role")
                    return
                setup_cursor = self.db_connection.cursor()
                sql = grab_sql("update_rank")
                loop = asyncio.get_event_loop()
                timestr = datetime.datetime.now()
                if not useConvID:
                    await loop.run_in_executor(ThreadPoolExecutor(), setup_cursor.execute, sql,
                                               (roleid, timestr, ctx.guild.id,))
                elif useConvID:
                    await loop.run_in_executor(ThreadPoolExecutor(), setup_cursor.execute, sql,
                                               (convRoleId, timestr, ctx.guild.id,))
                await loop.run_in_executor(ThreadPoolExecutor(), self.db_connection.commit)
                if not ctx.guild.id in self.min_roles:
                    self.min_roles[ctx.guild.id] = {}
                    self.min_roles[ctx.guild.id]["rank"] = roleid
                    timestr = datetime.datetime.now()
                    self.min_roles[ctx.guild.id]["last-use"] = timestr
                    self.min_roles["guilds"].append(ctx.guild.id)
                if ctx.guild.id in self.min_roles:
                    self.min_roles[ctx.guild.id]["rank"] = roleid
                    timestr = datetime.datetime.now()
                    self.min_roles[ctx.guild.id]["last-use"] = timestr
                await ctx.send("Rank has been updated.")
            if not ctx.author.guild_permissions.administrator:
                await ctx.send("Setup role requires the user executing the command to have Administrator!")
        else:
            return

    @commands.command()
    async def listfolders(self, ctx):
        if ctx.guild is None:
            return;
        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        await ctx.send("One moment retrieving your listeners...")
        sql = grab_sql("grab_server_listeners")
        list_cursor = self.db_connection.cursor()
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(ThreadPoolExecutor(), list_cursor.execute, sql, (ctx.guild.id,))
        obt_results = await loop.run_in_executor(ThreadPoolExecutor(), list_cursor.fetchall)
        messages = await createDeviationListString(obt_results, self.bot)
        await sendListMessage(ctx.message.channel, messages)

    @commands.command()
    async def deletefolder(self, ctx, artist: str, folder: str, channelid):
        if ctx.guild is None:
            return;
        useConvChannelID = False
        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        if isinstance(channelid, str):
            convChannelId = await convertChannelID(channelid, ctx)
            if convChannelId == 0:
                await ctx.send("Invalid channelID")
                return
            else:
                useConvChannelID = True
                obt_channel = self.bot.get_channel(convChannelId)
        elif isinstance(channelid, int):
            obt_channel = self.bot.get_channel(channelid)
            if obt_channel is None:
                await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
                return
        else:
            await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
            return
        if obt_channel is None:
            await ctx.send(
                "I was not able to grab channel information for the channelid you provided. Is this correct?")
        if not obt_channel.guild.id == ctx.guild.id:
            return
        sql = grab_sql("delete_listener")
        delete_cursor = self.db_connection.cursor()
        loop = asyncio.get_event_loop()
        if not useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), delete_cursor.execute, sql, (ctx.guild.id, artist, folder,
                                                                                          channelid,))
        elif useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), delete_cursor.execute, sql, (ctx.guild.id, artist, folder,
                                                                                          convChannelId,))

        if delete_cursor.rowcount == 1:
            await ctx.send("Listener deleted")
            self.db_connection.commit()
        elif delete_cursor.rowcount > 1:
            await ctx.send("An error has occurred! Please contact support reference error code: del-1")
        elif delete_cursor.rowcount == 0:
            await ctx.send("I could not find the listener matching the information you provided. Is this right?")
        delete_cursor.close()

    @commands.command()
    async def deleteallfolder(self, ctx, artist: str, channelid, mature: bool):
        if ctx.guild is None:
            return;
        useConvChannelID = False
        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        if isinstance(channelid, str):
            convChannelId = await convertChannelID(channelid, ctx)
            if convChannelId == 0:
                await ctx.send("Invalid channelID")
                return
            else:
                useConvChannelID = True
                obt_channel = self.bot.get_channel(convChannelId)
        elif isinstance(channelid, int):
            obt_channel = self.bot.get_channel(channelid)
            if obt_channel is None:
                await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
                return
        else:
            await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
            return
        obt_channel = self.bot.get_channel(channelid)
        if obt_channel is None:
            await ctx.send(
                "I was not able to grab channel information for the channelid you provided. Is this correct?")
        if not obt_channel.guild.id == ctx.guild.id:
            return
        sql = grab_sql("delete_all_listener")
        delete_cursor = self.db_connection.cursor()
        loop = asyncio.get_event_loop()
        if not useConvChannelID:
            test = await loop.run_in_executor(ThreadPoolExecutor(), delete_cursor.execute, sql,
                                              (ctx.guild.id, artist, mature,
                                               channelid, "all-folder",))
        elif useConvChannelID:
            test = await loop.run_in_executor(ThreadPoolExecutor(), delete_cursor.execute, sql,
                                              (ctx.guild.id, artist, mature,
                                               convChannelId, "all-folder",))
        if delete_cursor.rowcount == 1:
            await ctx.send("Listener deleted")
            self.db_connection.commit()
        elif delete_cursor.rowcount > 1:
            await ctx.send("An error has occurred! Please contact support reference error code: del-1")
        elif delete_cursor.rowcount == 0:
            await ctx.send("I could not find the listener matching the information you provided. Is this right?")
        delete_cursor.close()

    @commands.command()
    async def addfolder(self, ctx, artistname: str, foldername: str, channelid, inverted: bool, hybrid: bool,
                        mature: bool):
        """
        The method that is used when the addfolder command is invoked, the addfolder command is used to add another folder
        to an artist that is already in ArtData.
        :return: discord.ext.commands.core.Command object
        """
        print("Invoked")
        if ctx.guild is None:
            return;
        useConvChannelID = False
        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)

        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        if isinstance(channelid, str):
            convChannelId = await convertChannelID(channelid, ctx)
            if convChannelId == 0:
                return
            else:
                useConvChannelID = True
                channel = self.bot.get_channel(convChannelId)
        elif isinstance(channelid, int):
            channel = self.bot.get_channel(channelid)
            if channel is None:
                await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
                return
        else:
            await ctx.send("Invalid ChannelID, is the channel ID correct? Try mentioning the text channel instead")
            return
        if channel is None:
            self.deviantlogger.info("Could not link with provided channelid...sending message to channel")
            await ctx.send(
                "Error: I could not link with the provided channelid, is it correct? Do I have permission to access it?" \
                " I cannot tell because I am just a bot.")
            return;
        if not channel.guild.id == ctx.guild.id:
            return
        if mature:
            if not channel.is_nsfw():
                await ctx.send("Folders marked as mature must be in a NSFW channel!")
                return
        sql = grab_sql("duplicate_check")
        check_listener_cursor = self.db_connection.cursor()
        loop = asyncio.get_event_loop()
        if useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener_cursor.execute,
                                       sql, (convChannelId, ctx.guild.id, artistname, foldername,))
        elif not useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener_cursor.execute,
                                       sql, (channelid, ctx.guild.id, artistname, foldername,))
        duplicate_results = await loop.run_in_executor(ThreadPoolExecutor(), check_listener_cursor.fetchone)
        if duplicate_results is not None:
            await ctx.send("You already have a listener for this folder and artist in this channel. You can only have "
                           "one. If you want to listen for both inverse and noninverse set hybrid for the listener"
                           "to true using the updatehybrid command")
            return
        source_exists = verifySourceExistance(artistname, foldername, inverted, hybrid, mature, self.db_connection)
        folderid = dp.findFolderUUID(artistname, True, foldername, self.token)
        if folderid is "ERROR":
            await ctx.send("Could not find a folder specified. Is the artist and foldername exactly as they are on DA?")
            check_listener_cursor.close()
            return
        if not source_exists:
            if folderid.lower() == "none":
                await ctx.send("Could not find folder, is the foldername correct?")
                return
            loop = asyncio.get_event_loop()
            await ctx.send("Importing this folder for first time, this may take a bit.")
            await loop.run_in_executor(ThreadPoolExecutor(), addsource, artistname, foldername, folderid, inverted,
                                       hybrid, self.token,
                                       self.db_connection, mature)
            print("Finished adding source")
            if not useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addtask, ctx.guild.id, channelid, artistname,
                                           foldername,
                                           folderid, inverted, hybrid, mature, self.db_connection)
            elif useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addtask, ctx.guild.id, convChannelId, artistname,
                                           foldername,
                                           folderid, inverted, hybrid, mature, self.db_connection)
        else:
            loop = asyncio.get_event_loop()
            if not useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addtask, ctx.guild.id, channelid, artistname,
                                           foldername,
                                           folderid, inverted, hybrid, mature, self.db_connection)
            elif useConvChannelID:
                await loop.run_in_executor(ThreadPoolExecutor(), addtask, ctx.guild.id, convChannelId, artistname,
                                           foldername,
                                           folderid, inverted, hybrid, mature, self.db_connection)
        await ctx.send(
            "Listener added for folder " + foldername + " for artist " + artistname + " Reminder: The bot only checks for deviations every 25-30 minutes from when the bot was started!")

    @commands.command()
    async def updateinverse(self, ctx, artistname: str, foldername: str, inverse: bool, channelid):
        if ctx.guild is None:
            return;
        useConvChannelID = False
        test = await self.grab_min_role(ctx)
        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        if isinstance(channelid, str):
            convChannelId = await convertChannelID(channelid, ctx)
            if convChannelId == 0:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
            else:
                useConvChannelID = True
                obt_channel = self.bot.get_channel(convChannelId)
        elif isinstance(channelid, int):
            obt_channel = self.bot.get_channel(channelid)
            if obt_channel is None:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
        else:
            await ctx.send(
                "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                " You can use the listfolders command. ")
            return
        if not obt_channel.guild.id == ctx.guild.id:
            return
        check_listener = self.db_connection.cursor()
        sql = grab_sql("get_listener")
        loop = asyncio.get_event_loop()
        if not useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener.execute, sql,
                                       (artistname, foldername, channelid,))
        elif useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener.execute, sql,
                                       (artistname, foldername, convChannelId,))
        check_results = await loop.run_in_executor(ThreadPoolExecutor(), check_listener.fetchall)
        if check_results is None:
            await ctx.send("There is no listener with the information provided. Is this correct?", inverse)
            return
        if len(check_results) == 0:
            await ctx.send("Really?")
        if check_results[0][11] == inverse:
            await ctx.send("That listener already has inverse set to " + str(inverse).lower())
        else:
            folderid = check_results[0][2]
            hybrid = check_results[0][10]
            exists = await loop.run_in_executor(ThreadPoolExecutor(), verifySourceExistance, artistname,
                                                foldername, inverse, hybrid, True, self.db_connection)
            if not exists:
                dcuuid = str(uuid.uuid1())
                await ctx.send("Reimporting folder for first time with this inverse property this may take a bit")
                information = await loop.run_in_executor(ThreadPoolExecutor(), addsource,
                                                         artistname, foldername, folderid, inverse, hybrid,
                                                         self.token, self.db_connection, True, dcuuid)
                update_cursor = self.db_connection.cursor()
                sql = grab_sql("update_inverse")
                timestr = datetime.datetime.now()
                if useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (inverse, dcuuid,
                                                                                                  information[
                                                                                                      "normal-ids"],
                                                                                                  information[
                                                                                                      "hybrid-ids"],
                                                                                                  timestr, ctx.guild.id,
                                                                                                  convChannelId,
                                                                                                  folderid,
                                                                                                  "regular",))
                elif not useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (inverse, dcuuid,
                                                                                                  information[
                                                                                                      "normal-ids"],
                                                                                                  information[
                                                                                                      "hybrid-ids"],
                                                                                                  timestr, ctx.guild.id,
                                                                                                  channelid, folderid,
                                                                                                  "regular",))
                self.db_connection.commit()
                update_cursor.close()
                await ctx.send("Inverse updated")
            else:
                uuid_cursor = self.db_connection.cursor()
                uuid_sql = grab_sql("grab_source_dcuuid")
                await loop.run_in_executor(ThreadPoolExecutor(), uuid_cursor.execute, uuid_sql, (
                    artistname, foldername, inverse, hybrid,))
                uuid_result = await loop.run_in_executor(ThreadPoolExecutor(), uuid_cursor.fetchone)
                update_cursor = self.db_connection.cursor()
                sql = grab_sql("update_inverse")
                timestr = datetime.datetime.now()
                if useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (
                        inverse, uuid_result, uuid_result[1], uuid_result[2], timestr, ctx.guild.id, convChannelId,
                        folderid, "regular",))
                elif not useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (
                        inverse, uuid_result, uuid_result[1], uuid_result[2], timestr, ctx.guild.id, channelid,
                        folderid, "regular",))
                self.db_connection.commit()
                uuid_cursor.close()
                update_cursor.close()
                await ctx.send("Inverse updated")
        check_listener.close()

    @commands.command()
    async def updatehybrid(self, ctx, artistname: str, foldername: str, hybrid: bool, channelid):
        if ctx.guild is None:
            return;
        useConvChannelID = False
        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        if isinstance(channelid, str):
            convChannelId = await convertChannelID(channelid, ctx)
            if convChannelId == 0:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
            else:
                useConvChannelID = True
                obt_channel = self.bot.get_channel(convChannelId)
        elif isinstance(channelid, int):
            obt_channel = self.bot.get_channel(channelid)
            if obt_channel is None:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
        else:
            await ctx.send(
                "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                " You can use the listfolders command. ")
            return
        check_listener = self.db_connection.cursor()
        sql = grab_sql("get_listener")
        loop = asyncio.get_event_loop()
        if useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener.execute, sql,
                                       (artistname, foldername, convChannelId,))
        elif not useConvChannelID:
            await loop.run_in_executor(ThreadPoolExecutor(), check_listener.execute, sql,
                                       (artistname, foldername, channelid,))
        check_results = await loop.run_in_executor(ThreadPoolExecutor(), check_listener.fetchall)
        if len(check_results ) == 0:
            await ctx.send("Hmm...I dont have a listener for that folder.")
            return
        elif check_results[0][10] == hybrid:
            await ctx.send("This folder is already set to " + str(hybrid))
            return
        else:
            folderid = check_results[0][2]
            obt_hybrid = check_results[0][10]
            inverse = check_results[0][11]
            exists = await loop.run_in_executor(ThreadPoolExecutor(), verifySourceExistance, artistname,
                                                foldername, inverse, hybrid, True, self.db_connection)
            if not exists:
                dcuuid = str(uuid.uuid1())
                await ctx.send("Reimporting folder for first time with this hybrid property this may take a bit")
                information = await loop.run_in_executor(ThreadPoolExecutor(), addsource,
                                                         artistname, foldername, folderid, inverse, hybrid,
                                                         self.token, self.db_connection, True, dcuuid)
                update_cursor = self.db_connection.cursor()
                sql = grab_sql("update_hybrid")
                timestr = datetime.datetime.now()
                if not useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (hybrid, dcuuid,
                                                                                                  information[
                                                                                                      "normal-ids"],
                                                                                                  information[
                                                                                                      "hybrid-ids"],
                                                                                                  timestr, ctx.guild.id,
                                                                                                  channelid, folderid,
                                                                                                  "regular",))
                elif useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (hybrid, dcuuid,
                                                                                                  information[
                                                                                                      "normal-ids"],
                                                                                                  information[
                                                                                                      "hybrid-ids"],
                                                                                                  timestr, ctx.guild.id,
                                                                                                  convChannelId,
                                                                                                  folderid,
                                                                                                  "regular",))
                self.db_connection.commit()
                await ctx.send("Hybrid updated")
                update_cursor.close()
            else:
                uuid_cursor = self.db_connection.cursor()
                uuid_sql = grab_sql("grab_source_dcuuid")
                await loop.run_in_executor(ThreadPoolExecutor(), uuid_cursor.execute, uuid_sql, (
                    artistname, foldername, inverse, hybrid,))
                uuid_result = await loop.run_in_executor(ThreadPoolExecutor(), uuid_cursor.fetchone)
                update_cursor = self.db_connection.cursor()
                sql = grab_sql("update_hybrid")
                timestr = datetime.datetime.now()
                if not useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (
                        hybrid, uuid_result, uuid_result[1], uuid_result[2], timestr, ctx.guild.id, channelid, folderid,
                        "regular",))
                elif useConvChannelID:
                    await loop.run_in_executor(ThreadPoolExecutor(), update_cursor.execute, sql, (
                        hybrid, uuid_result, uuid_result[1], uuid_result[2], timestr, ctx.guild.id, channelid, folderid,
                        "regular",))
                self.db_connection.commit()
                uuid_cursor.close()
                await ctx.send("Hybrid updated")
                update_cursor.close()
        check_listener.close()

    @commands.command()
    async def test(self, ctx):
        print("Here")
    @commands.command()
    async def updatechannel(self, ctx, artistname: str, foldername: str, newchannelid, oldchannelid):
        if ctx.guild is None:
            print("Null guild")
            return;
        useConvChannelID = False
        min_rank = await self.grab_min_role(ctx)
        obtained_role = ctx.guild.get_role(min_rank)
        if obtained_role is None:
            await ctx.send("The minimum rank required to utilize DeviantCord commands on this server has not been set"
                           " or something is wrong. Someone with Administrator on this server needs to set the minimum"
                           "roleid with the setuprole command. \n setuprole <roleid>")
            return
        if not ctx.author.top_role >= obtained_role:
            return;
        if isinstance(oldchannelid, str):
            convChannelId = await convertChannelID(oldchannelid, ctx)
            if convChannelId == 0:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
            else:
                useConvChannelID = True
                obt_channel = self.bot.get_channel(convChannelId)
        elif isinstance(oldchannelid, int):
            obt_channel = self.bot.get_channel(oldchannelid)
            if obt_channel is None:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
        else:
            await ctx.send(
                "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                " You can use the listfolders command. ")
            return
        if isinstance(oldchannelid, str):
            convNewChannelId = await convertChannelID(oldchannelid, ctx)
            if convNewChannelId == 0:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
            else:
                useConvNewChannelID = True
                obt_newchannel = self.bot.get_channel(convNewChannelId)
        elif isinstance(oldchannelid, int):
            obt_channel = self.bot.get_channel(oldchannelid)
            if obt_channel is None:
                await ctx.send(
                    "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                    " You can use the listfolders command. ")
                return
        else:
            await ctx.send(
                "Invalid channelid, try using the numeric channelid or mention the channel the listener is in."
                " You can use the listfolders command. ")
            return
        if useConvNewChannelID:
            new_channel_obt = self.bot.get_channel(convNewChannelId)
        elif not useConvNewChannelID:
            new_channel_obt = self.bot.get_channel(int(newchannelid))
        if new_channel_obt is None:
            self.deviantlogger.info("Could not link with provided newchannelid...sending message to channel")
            await ctx.send(
                "Error: I could not link with the provided newchannelid, is it correct? Do I have permission to access it?" \
                " I cannot tell because I am just a bot.")
            return;
        if not new_channel_obt.guild.id == ctx.guild.id:
            return
        if not useConvChannelID:
            oldchannelid_obt = self.bot.get_channel(int(oldchannelid))
        elif useConvChannelID:
            oldchannelid_obt = self.bot.get_channel(int(convChannelId))
        if oldchannelid_obt is None:
            self.deviantlogger.info("Could not link with provided newchannelid...sending message to channel")
            await ctx.send(
                "Error: I could not link with the provided oldchannelid, is it correct? Do I have permission to access it?" \
                " I cannot tell because I am just a bot.")
            return;
        if not oldchannelid_obt.guild.id == ctx.guild.id:
            return
        check_listener = self.db_connection.cursor()
        sql = grab_sql("duplicate_check")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(ThreadPoolExecutor(), check_listener.execute, sql,
                                   (oldchannelid_obt.id, ctx.guild.id, artistname,
                                    foldername,))
        check_results = await loop.run_in_executor(ThreadPoolExecutor(), check_listener.fetchall)
        if len(check_results) == 0:
            await ctx.send("Could not find listener. Is this information provided right?")
            return
        sql = grab_sql("update_channel")
        update_cursor = self.db_connection.cursor()
        await loop.run_in_executor(ThreadPoolExecutor(),
                                   update_cursor.execute, sql,
                                   (new_channel_obt.id, oldchannelid_obt.id, foldername, artistname,))
        await loop.run_in_executor(ThreadPoolExecutor(), self.db_connection.commit)
        await ctx.send("Channel Updated!")
        update_cursor.close()
        check_listener.close()

    @listfolders.error
    @updatechannel.error
    @updatehybrid.error
    @addfolder.error
    @addallfolder.error
    @setuprole.error
    @updateinverse.error
    @deletefolder.error
    @deleteallfolder.error
    async def command_errorhandler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Error: "
                           "" + str(error.param.name) + " was not found. Use the help command for more information."
                                                        " If the parameter specified by this message has quotes in "
                                                        "the help command. It means that parameter needs to be surrounded"
                                                        " by quotes. ")
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, psycopg2.DataError):
                await ctx.send("Uh oh DeviantCord's database refused the data you submitted. Check that the arguments you"
                               " provided is correct and try again. Otherwise contact DeviantCord support. Error Code 11")
                self.db_connection.rollback()
            elif isinstance(error.original, psycopg2.InternalError):
                await ctx.send(
                    "Uh oh looks like DeviantCord experienced a database related error. Contact DeviantCord support via"
                    " the support command. Reference Error Code: 10")
                self.db_connection.rollback()
            elif isinstance(error.original, psycopg2.ProgrammingError):
                ctx.send(
                    "Uh oh looks like DeviantCord encountered a bug. Please contact DeviantCord Support via the Support command")
                self.db_connection.rollback()
            elif isinstance(error.original, psycopg2.IntegrityError):
                await ctx.send(
                    "Uh oh DeviantCord's database refused the data you submitted. Check that the arguments you"
                    " provided is correct and try again. Otherwise contact DeviantCord support. Error Code 11")
                self.db_connection.rollback()
            elif isinstance(error.original, psycopg2.OperationalError):
                ctx.send(
                    "Uh oh looks like DeviantCord's database is having issues. This should resolve itself within 5 minutes"
                    " if this continues contact DeviantCord Support Reference Error code 09")
                await self.recoverConnection()
            elif isinstance(error.original, psycopg2.DatabaseError):
                ctx.send(
                    "Uh oh looks like DeviantCord's database is having issues. If this doesnt resolve itself within 5 min"
                    " contact DeviantCord Support Reference Error code 08")
                await self.recoverConnection()
            elif isinstance(error.original, urllib.error.HTTPError):
                if error.original.code == 401:
                    await ctx.send(
                        "Error: Automatic Token renewal didn't taken place, tokens will renew in 10 minutes, "
                        "if issues persist past 20 minutes please contact DeviantCord support.")
                    self.deviantlogger.error("addfolder command returned a HTTP 401, ")
                    await self.softTokenRenewal()
                if error.original.code == 503:
                    self.deviantlogger.error(
                        ctx.command.name + " returned a HTTP 503, DA Servers are down for maintenance ")
                    await ctx.send("Error: DA's servers are down for maintenance. Please wait a few minutes");
                if error.original.code == 500:
                    self.deviantlogger.error(ctx.command.name + " returned a HTTP 500, Internal Error ")
                    await ctx.send("DA's servers returned a Error 500 Internal Error. Try again in a few minutes");
                if error.original.code == 429:
                    self.deviantlogger.error(ctx.command.name + " returned a HTTP 429, DA API Overloaded ")
                    await ctx.send("Error: DA API is currently overloaded...please wait for an hour. ")
                    return 429;
            with configure_scope() as scope:
                scope.set_extra("command", ctx.command.name)
                scope.set_extra("discord-guild", ctx.guild.name)
                scope.set_extra("guild-id", ctx.guild.id)
                scope.set_extra("channel-id", ctx.channel.id)
                scope.set_extra("channel-name", ctx.channel.name)
                capture_exception(error)
            self.db_connection.rollback()
            return
        elif isinstance(error, urllib.error.HTTPError):
            if error.code == 401:
                await ctx.send(
                    "Error: Automatic Token renewal didn't taken place, tokens will renew in 10 minutes, "
                    "if issues persist past 20 minutes please contact DeviantCord support.")
                self.deviantlogger.error("addfolder command returned a HTTP 401, ")
                await self.softTokenRenewal()
            if error.code == 503:
                self.deviantlogger.error(
                    ctx.command.name + " returned a HTTP 503, DA Servers are down for maintenance ")
                await ctx.send("Error: DA's servers are down for maintenance. Please wait a few minutes");
            if error.code == 500:
                self.deviantlogger.error(ctx.command.name + " returned a HTTP 500, Internal Error ")
                await ctx.send("DA's servers returned a Error 500 Internal Error. Try again in a few minutes");
            if error.code == 429:
                self.deviantlogger.error(ctx.command.name + " returned a HTTP 429, DA API Overloaded ")
                await ctx.send("Error: DA API is currently overloaded...please wait for an hour. ")
                return 429;
        elif isinstance(error, commands.errors.NoPrivateMessage):
            return
        else:
            with configure_scope() as scope:
                scope.set_extra("command", ctx.command.name)
                scope.set_extra("discord-guild", ctx.guild.name)
                scope.set_extra("guild-id", ctx.guild.id)
                scope.set_extra("channel-id", ctx.channel.id)
                scope.set_extra("channel-name", ctx.channel.name)
                capture_exception(error)

    def error_handler(self, loop, context):
        print("Exception: ", context['exception'])
        capture_exception(context['exception'])
        logger = logging.getLogger("deviantcog")
        logger.exception(context["exception"])
        if self.failedlogincount >= 3:
            self.failedlogincount = 0
        if str(context['exception']) == "HTTP Error 401: Unauthorized":
            self.failedlogincount = self.failedlogincount + 1
            print("Your DA info is invalid, please check client.json to see if it matches your DA developer page")
            logger.error(
                "Your DA info is invalid, please check client.json to see if it matches your DA developer page")
            while self.failedlogincount <= 3:
                if self.instantTokenDiagnosisRenewal():
                    break
                else:
                    self.failedlogincount = self.failedlogincount + 1

            if self.failedlogincount >= 3:
                print("Exceeded 3 failed login limit. If this was hit when starting up then you need to check"
                      "your DA info in client.json..Attempting softtokenrenewal ")
                self.bot.loop.create_task(self.fix_error(1200))
        if isinstance(context["exception"], psycopg2.DataError):
            self.db_connection.rollback()
            self.bot.loop.create_task(self.fix_error(120))
        elif isinstance(context["exception"], psycopg2.InternalError):
            self.db_connection.rollback()
            self.bot.loop.create_task(self.fix_error(120))
        elif isinstance(context["exception"], psycopg2.ProgrammingError):
            self.db_connection.rollback()
            self.bot.loop.create_task(self.fix_error(120))
        elif isinstance(context["exception"], psycopg2.IntegrityError):
            self.db_connection.rollback()
            self.bot.loop.create_task(self.fix_error(120))
        elif isinstance(context["exception"], psycopg2.OperationalError):
            self.bot.loop.create_task(self.recoverConnection())
            self.bot.loop.create_task(self.fix_error(120))
        elif isinstance(context["exception"], psycopg2.DatabaseError):
            self.bot.loop.create_task(self.recoverConnection())
            self.bot.loop.create_task(self.fix_error(120))

        if str(context['exception']).find("psycopg2") > -1:
            logger.error("psycopg2 exception encountered")
            self.bot.loop.create_task(self.recoverConnection())
        if str(context['exception']) == "HTTP Error 400: Bad request":
            logger.error("HTTP Error 400 encountered, ignoring...")
        elif str(context['exception']).find("HTTP Error 400") > -1:
            logger.error("HTTP Error 400 encountered")
            self.bot.loop.create_task(self.fix_error(120))
        elif str(context['exception']).find("HTTP Error 500") > -1:
            logger.error("HTTP Error 500 Encountered")
            self.bot.loop.create_task(self.fix_error(1200))
        elif str(context['exception']).find("HTTP Error 503") > -1:
            logger.error("Encountered a HTTP Error 503: DA's servers are likely down. Now creating task to renew token"
                         "in 20 minutes")
            self.bot.loop.create_task(self.fix_error(2400))
            # loop.run_until_complete(self.manualgetNewToken())
        elif str(context['exception']).find("HTTP Error 429") > -1:
            logger.error("Encountered a HTTP Error 429: Received Rate Limit response, toning down responses for "
                         "in 20 minutes")
            self.bot.loop.create_task(self.fix_error(600))
            # loop.run_until_complete(self.rateLimitMeasure())
        else:
            print("Exception encountered: ", context['exception'])
            logger.error("Exception Encountered " + str(context['exception']))
            self.bot.loop.create_task(self.fix_error(500))


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(daCog(bot))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, BadArgument):
            await ctx.send("Incorrect usage of arguments, use the help command for more information")
        if isinstance(error, CommandNotFound):
            return