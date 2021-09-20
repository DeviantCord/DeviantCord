#
# THIS Python file is property of Errite Games LLC
# All Rights Reserved
#
#
#
from logging.handlers import TimedRotatingFileHandler
import json
import logging
from discord.ext import commands
from discord.ext.commands import CommandNotFound, has_permissions
from errite.tools.mis import fileExists
import discord
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
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

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
from asyncio import get_event_loop
import urllib


class adminCog(commands.Cog):
    def __init__(self, bot):
        self.logname = "admincog"
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
        self.logname = "erritecog"

        self.deviantlogger = logging.getLogger("erritecog")
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
                                sentry_sdk.init(sentry_url, integrations=[AioHttpIntegration()])
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
            self.ban_channel = configData["ban-channel"]
            self.ban_notification_channel = configData["ban-notification-channel"]
            self.time = configData["sync-time"]
            # Database Specific Options
            self.deviantlogger.info("Setting Database Variables")
            self.database_name = self.dbInfo["database-name"]
            self.database_host = self.dbInfo["database-host"]
            self.database_host2 = self.dbInfo["database-host2"]
            self.database_host3 = self.dbInfo["database-host3"]
            self.database_password = self.dbInfo["database-password"]
            self.database_user = self.dbInfo["database-username"]
            self.database_port = self.dbInfo["database-port"]
            self.stop_duplicaterecovery = False
            if self.database_host2 == "none":
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "' " + \
                              "'port='" + str(self.database_port) + "password='" + self.database_password + "'"
            elif self.database_host3 == "none":
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "," + self.database_host2 + "' " + \
                              "'port='" + str(self.database_port) + "password='" + self.database_password + "'"
            else:
                connect_str = "dbname='" + self.database_name + "' user='" + self.database_user \
                              + "'host='" + self.database_host + "," + self.database_host2 + "," + self.database_host3 + " " + \
                              "'port='" + str(self.database_port) + "'password='" + self.database_password + "'"
            print("Connecting to database")
            self.db_connection = psycopg2.connect(connect_str)
            # Errite LLC Specific Options THIS is for DeviantCord Public Hosting, these settings are what
            # stops the bot from executing code meant for DeviantCord Public Hosting only
            self.errite = configData["errite"]
            self.errite_channel = configData["errite-channel"]
        self.deviantlogger.info("Now creating tasks...")
        self.bot.loop.set_exception_handler(self.error_handler)
        self.bot.loop.create_task(self.timeout_ranks())

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
            print("Obtained prefix " + str(obt_results[0]))
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

    @commands.command()
    @has_permissions(administrator=True)
    async def blacklistfolder(self, ctx, artist:str, given_folder:str, reason:str):
        if ctx.guild is None:
            return
        print(str(ctx.message.channel.id) + ' vs ' + str(self.ban_channel))
        if ctx.message.channel.id == self.ban_channel:
            bl_cursor = self.db_connection.cursor()
            folder = "UPDATE deviantcord.deviation_data set disabled = true WHERE artist = %s AND folder_name = %s"
            allfolder = "UPDATE deviantcord.deviation_data_all set disabled = %s WHERE artist = %s"
            listener = "UPDATE deviantcord.deviation_listeners set disabled = true WHERE artist = %s AND foldername = %s"
            loop = get_event_loop()
            print("Starting execution")
            try:
                bl_cursor.execute(folder,(artist, given_folder,))
                self.db_connection.commit()
                bl_cursor.execute(allfolder,(True, artist))
                self.db_connection.commit()
                bl_cursor.execute(listener, (artist, given_folder))
                self.db_connection.commit()
            except Exception as ex:
                print("Some shit happened, look in Sentry")
            print("Committing")
            self.db_connection.commit()
            print("Done")
            await ctx.send("Artist " + artist + " has been blacklisted.")
            notification = discord.Embed(title="New Artist Temporarily disabled")
            notification.add_field(name="by ", value=ctx.author.display_name + "#" + ctx.author.discriminator)
            notification.add_field(name="Artist ", value=artist)
            notification.add_field(name="Foldername", value=given_folder)
            notification.add_field(name="Reason:", value=reason)
            notification.set_thumbnail(url=ctx.author.avatar_url)
            channel = self.bot.get_channel(self.ban_notification_channel)
            if channel is None:
                return
            else:
                await channel.send(embed=notification)


    @commands.command()
    @has_permissions(administrator=True)
    async def checkpresence(self, ctx, provided_guildid:int):
        if ctx.guild is None:
            return
        if ctx.guild.id == self.guildid:
            found = False
            if ctx.message.channel.id == self.errite_channel_id:
                self.adminlogger.info("CheckPresence: Command came from Errite exec channel."
                                      "Checking guildid " + str(provided_guildid))
                for retrieved_guild in self.bot.guilds:
                    print("Entered for")
                    if retrieved_guild.id == int(provided_guildid):
                        found = True
                        break
                if found is True:
                    info = self.bot.get_guild(int(provided_guildid))
                    await ctx.send("Guild " + info.name + " has the bot on the server.")
                if found is False:
                    await ctx.send("DeviantCord is not on that guild.")

    @commands.command()
    @has_permissions(administrator=True)
    async def issueleave(self, ctx, provided_guildid:int):
        if ctx.guild is None:
            return
        if self.guildid is None:
            return
        if not provided_guildid == self.guildid:
            return
        if self.errite_channel_id is None:
            return
        if provided_guildid == self.guildid:
            if ctx.message.channel.id == self.errite_channel_id:
                designated_target = self.bot.get_guild(provided_guildid)
                if designated_target.id is None:
                    await ctx.send("Invalid guildid given.")
                    return
                else:
                    print("YOU")
                    print(designated_target)
                    print(ctx.guild.name)
                    await ctx.send("Received issueleave for " + designated_target.name + " executing now. ")
                    await designated_target.leave()

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
    bot.add_cog(adminCog(bot))
    print("erriteCommands bt-0.2.0")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            return





