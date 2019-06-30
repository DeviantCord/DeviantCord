import json
import os
import sys
import discord
from logging.handlers import TimedRotatingFileHandler
import asyncio
import datetime
import logging
from discord.ext import commands
from discord.ext.commands import has_permissions, guild_only, CommandNotFound
import errite.da.daParser as dp
from errite.da.jsonTools import createArtistData, artistExists, folderExists, createFolderData, \
    updateDiscordChannel, updateRole, updateinverseproperty, delfolder, updatehybridproperty
from errite.config.configManager import createConfig, createSensitiveConfig
from errite.tools.mis import fileExists
import urllib


class daCog(commands.Cog):
    """The Deviant Art component class for DeviantCord"""

    def __init__(self, bot):
        self.clientid = None
        self.clientsecret = None
        self.guildid = None
        self.enablesr = False
        self.jsonlock = False
        self.roleid = 0
        self.failedlogincount = 0
        self.publicmode = None
        self.datevar = datetime.datetime.now().strftime("%Y-%m-%d%H%M%S")
        self.whiletrigger = False
        self.logname = "deviantcog"

        self.deviantlogger = logging.getLogger("deviantcog")
        self.deviantlogger.setLevel(logging.DEBUG)
        self.dlhandler = TimedRotatingFileHandler(self.logname, when='h', interval=12, backupCount=2000,
                                                  encoding='utf-8')
        self.dlhandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
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
                            sensitiveData = json.load(clientjsonFile)
                            configjsonFile.close()
                            clientjsonFile.close()
                            if sensitiveData["da-client-id"] is not "id here":
                                if sensitiveData["da-secret"] is not "secret":
                                    self.clientsecret = sensitiveData["da-secret"]
                                    self.clientid = sensitiveData["da-client-id"]
                                    self.passedJson = True

        if self.passedJson == True:
            self.deviantlogger.info("Now setting JSON Variables")
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
            # Errite LLC Specific Options THIS is for DeviantCord Public Hosting, these settings are what
            # stops the bot from executing code meant for DeviantCord Public Hosting only
            self.errite = configData["errite"]
            self.errite_channel = configData["errite-channel"]
        self.deviantlogger.info("Now creating tasks...")
        self.bot.loop.create_task(self.getNewToken())
        self.bot.loop.set_exception_handler(self.error_handler)
        self.bot.loop.create_task(self.syncGalleries())

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
        await asyncio.sleep(amount)
        if sys.version_info >= (3, 7):
            pending = asyncio.all_tasks()
        elif sys.version_info >= (3, 5, 2):
            pending = asyncio.Task.all_tasks()

        token_present = False
        sg_present = False

        for element in pending:
            if str(element).find("coro=<daCog.getNewToken()"):
                token_present = True
            if str(element).find("coro=<daCog.syncGalleries()"):
                sg_present = True
        if not token_present:
            self.deviantlogger.warning(
                "manualGetToken: Detected that getNewToken task is dead, creating new task")
            self.bot.loop.create_task(self.getNewToken())
            self.deviantlogger.warning("manualGetToken: getNewToken created!")
        if not sg_present:
            self.deviantlogger.warning("manualGetToken: Detected that syncGalleries task is dead, creating new task")
            self.bot.loop.create_task(self.syncGalleries())
            self.deviantlogger.warning("manualGetToken: syncGalleries created!")

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

    async def syncGalleries(self):
        """
        Checks programmed gallery folders for Deviations. This is the method that is ran to trigger every x minutes
        depending on what the user has it configured to.
        """
        locked = False
        try:
            locked = self.jsonlock
        except NameError:
            print("Caught Assignment Error...Returning")
            return;
        if not locked:
            if self.passedJson == True:
                self.jsonlock = True
                await self.bot.wait_until_ready()

                while not self.bot.is_closed():
                    dirpath = os.getcwd()
                    self.deviantlogger.debug("Sync Galleries method ran: current directory is : " + dirpath)
                    with open("artdata.json", "r") as jsonFile:
                        self.deviantlogger.info("SyncGalleries: Loading JSON file ArtData")
                        artdata = json.load(jsonFile)
                        for element in artdata["artist_store"]["used-artists"]:
                            self.deviantlogger.debug("Now starting sync for artist " + element)
                            for foldername in artdata["art-data"][element]["folder-list"]:
                                self.deviantlogger.debug(
                                    "Starting Sync for folder " + foldername + " from artist " + element)
                                urls = dp.getGalleryFolder(element, True,
                                                           artdata['art-data'][element][foldername]["artist-folder-id"],
                                                           self.token,
                                                           foldername,
                                                           artdata['art-data'][element][foldername]["inverted-folder"])
                                self.jsonlock = False
                                channel = self.bot.get_channel(
                                    int(artdata["art-data"][element][foldername]["discord-channel-id"]))
                                if artdata["art-data"][element][foldername]["inverted-folder"]:
                                    self.deviantlogger.debug("Folder is inverse")
                                    storage = len(urls)
                                    currentlength = len(urls)
                                    while currentlength >= 1:
                                        self.deviantlogger.debug("New Deviation URL: ")
                                        self.deviantlogger.debug(str(urls[currentlength - 1]))
                                        self.deviantlogger.debug("SyncGalleries: Now posting URL")
                                        await channel.send(
                                            "New deviation from " + element + " you can view it here \n" + urls[
                                                currentlength - 1])
                                        currentlength = currentlength - 1

                                else:
                                    for url in urls:
                                        self.deviantlogger.debug("New Deviation URL: ")
                                        self.deviantlogger.debug(url)
                                        self.deviantlogger.debug("SyncGalleries: Now posting URL")
                                        await channel.send(
                                            "New deviation from " + element + " you can view it here \n" + url)
                        self.jsonlock = False
                        await asyncio.sleep(self.time)
        else:
            await asyncio.sleep(self.time)

    @commands.command()
    async def help(self, ctx):
        self.deviantlogger.info("Help command invoked")
        skiprolecheck = False
        testvar = None
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                self.deviantlogger.error("Help Command found that RoleID Is invalid.")
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        text = "**DeviantCord Help Guide**\n**" + self.prefix + \
               "help** - Gives a list of command with explaination\n**NOTE: Inverse means that newest deviations are at the top, instead of the bottom. Use true or false to answer it**\n**" + \
               self.prefix + "addfolder** *<artist_username>* *<folder>* *<channel_id>* *<inverse>* - Adds another artists gallery folder for the bot to notify the specified channel of new deviations. Use this when your adding another folder to an artist already added \n**" + \
               self.prefix \
               + "addartist** *<artist_username>* *<folder>* *<channel_id>* *<inverse>*- Used to add an artist and the first folder into the bots datafile. Use this command when you are adding an artist for the first time!\n**" + \
               self.prefix + "deletefolder** *<artist_username>* *<folder>* - Deletes the listener for the folder and erases it from artdata\n **" + \
               self.prefix + "manualSync** - Will check all configured folders for new deviations instead of waiting for the timer to trigger and start the check *DO NOT SPAM THIS*\n" + "**" + \
               self.prefix + "listfolders** - Lists all the current folder listeners that the bot is listening to. \n **" + \
               self.prefix + "updatehybrid** *<artist_username> *<folder>* *<hybrid>* - Sets the hybrid property of an existing folder listener \n **" + \
               self.prefix + "updateinverse** *<artist_username> *<folder>* *<inverse>* - Updates the inverse property of a existing folder listener\n" + \
               "**" + self.prefix + "updatechannel** *<artist_username> *<folder>* *<channelid>* - Updates the discord channel that notifications will be posted for an existing folder listener\n" + \
               "** __ADMIN COMMANDS__** \n" + \
               "**" + self.prefix + "erritetoggle** - Toggles the Errite Error Notifier that lets DeviantCord Support know of issues with the bot for your Discord server.\n**ONLY FOR the Official DeviantCord Public Bot NOT SELF HOSTED**\n" + \
               "**" + self.prefix + "setprefix** *<prefix>* - Updates the prefix for all commands and reloads\n" + \
               "**" + self.prefix + "reload** - Reloads DeviantCord"

        await ctx.send(text)

    @commands.command()
    @has_permissions(administrator=True)
    async def setuprole(self, ctx, roleid):
        if self.enablesr:
            if ctx.guild is None:
                return;
            if self.guildid == 0:
                self.deviantlogger.info('Setup has been invoked')
                updateRole(int(roleid), ctx.guild.id)
                self.deviantlogger.info("Setup Role: Madeit past update method. ")
                self.deviantlogger.debug("Before update: " + str(self.roleid))
                self.roleid = roleid
                self.deviantlogger.debug("After update: " + str(self.roleid))
                await ctx.send("Role has been setup!")
        else:
            return

    @commands.command()
    async def listfolders(self, ctx):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        if self.jsonlock is True:
            if ctx.guild.get_role(self.roleid) is None:
                return
            elif ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                await ctx.send(
                    "ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in listfolders ROLEID: " + str(self.roleid))
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if self.jsonlock:
            await ctx.send(
                "There is currently a task going on using ArtData, so this data may change soon. You might want to run the command again soon.!")
            # This is only reading data so there is no risk of just ignoring the json lock no need for return

        if permitted:
            with open("artdata.json", "r") as jsonFile:
                tempartdata = json.load(jsonFile)
                jsonFile.close()
                if len(tempartdata["artist_store"]["used-artists"]) > 0:
                    output = "**Current Folder Listeners**\n"
                    for artist in tempartdata["artist_store"]["used-artists"]:
                        output = output + "\n__" + artist + "___\n"
                        for folder in tempartdata["art-data"][artist]["folder-list"]:
                            output = output + "**" + folder + "**\n"
                    await ctx.send(output)
                else:
                    await ctx.send(
                        "Bad News... there aren't any folders. Maybe they went on vacation? I can't tell because I'm a bot, not a travel agent.")
                    return;

    @commands.command()
    async def deletefolder(self, ctx, artist, folder):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        if self.jsonlock is True:
            if ctx.guild.get_role(self.roleid) is None:
                return
            elif ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                await ctx.send(
                    "ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in deletefolder ROLEID: " + str(self.roleid))
            if ctx.author.guild_permissions.administrator:
                skiprolecheck
            else:
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if self.jsonlock:
            await ctx.send(
                "There is currently a task going on using ArtData, so this data may change soon. You might want to run the command again soon.!")
            return
        if permitted:
            self.jsonlock = True
            if artistExists(artist.lower()):
                if folderExists(artist, folder):
                    delfolder(artist, folder)
                    await ctx.send(
                        "Folder listener deleted successfully! I will no longer post updates for this folder. ")
                    self.jsonlock = False
                    return
                else:
                    self.jsonlock = False
                    await ctx.send(
                        "Error: This folder does not exist, so I can't delete it! You can't just delete thin air!")
                    return
            else:
                self.jsonlock = False
                await ctx.send(
                    "Error: This artist does not have a listener. Is this a mistake? I can't tell I'm just a bot!")

    @commands.command()
    async def addfolder(self, ctx, artistname, foldername, channelid, inverted):
        """
        The method that is used when the addfolder command is invoked, the addfolder command is used to add another folder
        to an artist that is already in ArtData.
        :return: discord.ext.commands.core.Command object
        """
        if ctx.guild is None:
            return;
        if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
            return;
        skiprolecheck = False
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in addfolder ROLEID: " + str(self.roleid))
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if self.jsonlock:
            await ctx.send("ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return;
        if permitted:
            self.jsonlock = True
            self.deviantlogger.info("addFolder command invoked.");
            dirpath = os.getcwd()
            self.deviantlogger.info("current directory is : " + str(dirpath))
            self.deviantlogger.info("Channel ID" + str(channelid))
            self.deviantlogger.info("Artist: " + artistname)
            self.deviantlogger.info("Foldername: " + foldername)
            isInverted = False
            if isinstance(inverted, bool) == True:
                self.deviantlogger.info("Inverted confirmed as bool")
                isInverted = inverted
                self.deviantlogger.info("Inverted Value confirmed as " + str(isInverted))
            if isinstance(inverted, str) == True:
                self.deviantlogger.info("Inverted is confirmed as str")
                if inverted.lower() == "true":
                    isInverted = True
                elif inverted.lower() == "false":
                    isInverted = False
                else:
                    self.jsonlock = False
                    self.deviantlogger.debug("Inverted Value confirmed as " + str(isInverted))
                    await ctx.send("Error: Invalid inverted parameter. Must use true or false")
                    return;
            channel = self.bot.get_channel(int(channelid))
            if channel is None:
                self.jsonlock = False
                self.deviantlogger.info("Could not link with provided channelid...sending message to channel")
                await ctx.send(
                    "Error: I could not link with the provided channelid, is it correct? Do I have permission to access it?" \
                    " I cannot tell because I am just a bot.")
                return;
            if channel.guild is None:
                self.jsonlock = False
                return;
            if not channel.guild.id == ctx.guild.id:
                self.jsonlock = False
                return
            if (artistExists(artistname) == False):
                self.jsonlock = False
                self.deviantlogger.info("Addfolder command was just ran, but the artist is not in artdata!")
                await channel.send(
                    "You need to run the addartist command for a new artist. Use the help command for more information")
                return;
            if (folderExists(artistname, foldername) == True):
                self.jsonlock = False
                self.deviantlogger.info("This folder is already in the JSON File!")
                await channel.send("I already know about this folder. Do you mean a different folder?")
                return;
            if (folderExists(artistname, foldername) == False):
                requestedfolderid = dp.findFolderUUID(artistname, True, foldername, self.token)
                if requestedfolderid == "ERROR":
                    self.jsonlock = False
                    self.deviantlogger.info("Invalid artist lookup, input: " + artistname)
                    await ctx.send("Error: This Artist does not exist!")
                    return;
                if requestedfolderid == "None":
                    self.jsonlock = False
                    self.deviantlogger.info("Artist folder not found, for " + artistname + " in" + foldername)
                    await ctx.send("Error: Folder " + foldername + " not found")
                    return;
                else:
                    self.deviantlogger.info("addfolder command passed all checks, now proceeding to execution")
                    self.deviantlogger.debug("IsInverted: " + str(isInverted))
                    self.deviantlogger.info("Now creating folder data for " + artistname + "in " + foldername)
                    createFolderData(artistname, requestedfolderid, foldername, channelid, isInverted)
                    await channel.send("Added " + artistname + "'s " + foldername + " gallery folder")
                    self.deviantlogger.info(
                        "Now populating folder data with deviations for " + artistname + "in " + foldername)
                    await channel.send("Now populating with current deviations...")
                    with open("artdata.json", "r") as jsonFile:
                        artdata = json.load(jsonFile)
                        jsonFile.close()
                        self.deviantlogger.info("Addfolder: Now running getGalleryFolderFT")
                        dp.getGalleryFolderFT(artistname, True,
                                              artdata["art-data"][artistname.lower()][foldername]["artist-folder-id"],
                                              self.token, foldername)
                        self.jsonlock = False
                        await channel.send(
                            "Finished populating...this channel will now receive updates on new deviations by "
                            + artistname + " in folder " + foldername)
                        self.deviantlogger.info("Finished populating folder!")

    @commands.command()
    async def updateinverse(self, ctx, artistname, foldername, inverse):
        skiprolecheck = False
        if ctx.guild is None:
            return
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        if self.jsonlock:
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in updateinverse ROLEID: " + str(self.roleid))
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                self.jsonlock = False
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if self.jsonlock:
            await ctx.send("ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return;
        if permitted:
            self.jsonlock = True
            if isinstance(inverse, bool):
                self.deviantlogger.info("New Inverse Instance of bool")
            elif isinstance(inverse, str):
                self.deviantlogger.info("New Inverse Instance of String")
                self.deviantlogger.debug("OBTAINED INVERSE: " + inverse)
                self.deviantlogger.info("CHECK: " + inverse.lower())
                print(inverse.lower())
                if inverse.lower() == "true":
                    print("Inverse is true")
                elif inverse.lower() == "false":
                    print("Inverse is false")
                else:
                    await ctx.send("Invalid inverse given...")
                    self.jsonlock = False
                    return

            self.deviantlogger.info("UpdateInverse: Entered JSON checks")
            if artistExists(artistname):
                if folderExists(artistname, foldername):
                    updateinverseproperty(artistname, foldername, inverse)
                    self.deviantlogger.info("Update inverse finished for " + artistname + " on" + foldername)
                    self.jsonlock = False
                    await ctx.send("Inverse Updated for " + artistname + " in " + foldername)
                else:
                    await ctx.send(
                        "I am not currently listening for new deviations on " + foldername + "is this the correct " \
                                                                                             "name for the folder?")
                    self.jsonlock = False
                    return;
            else:
                self.jsonlock = False
                await ctx.send("I do not have " + artistname + "in my datafiles is this the correct artist?")

    @commands.command()
    async def updatehybrid(self, ctx, artistname, foldername, inverse):
        skiprolecheck = False
        if ctx.guild is None:
            return
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        if self.jsonlock:
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in updatehybrid ROLEID: " + str(self.roleid))
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                self.jsonlock = False
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if self.jsonlock:
            await ctx.send("ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return;
        if permitted:
            print("Entered Permitted")
            self.jsonlock = True
            if isinstance(inverse, bool):
                self.deviantlogger.info("New Inverse Instance of bool")
            elif isinstance(inverse, str):
                self.deviantlogger.info("New Inverse Instance of String")
                self.deviantlogger.debug("OBTAINED HYBRID: " + inverse)
                self.deviantlogger.info("CHECK: " + inverse.lower())
                if inverse.lower() == "true":
                    print("hybrid is true")
                elif inverse.lower() == "false":
                    print("hybrid is false")
                else:
                    await ctx.send("Invalid hybrid given...")
                    self.jsonlock = False
                    return

            self.deviantlogger.info("UpdateHybrid: Entered JSON checks")
            if artistExists(artistname):
                if folderExists(artistname, foldername):
                    updatehybridproperty(artistname, foldername, inverse)
                    self.deviantlogger.info("Update hybrid finished for " + artistname + " on" + foldername)
                    self.jsonlock = False
                    await ctx.send("Hybrid Updated for " + artistname + " in " + foldername)
                else:
                    await ctx.send(
                        "I am not currently listening for new deviations on " + foldername + "is this the correct " \
                                                                                             "name for the folder?")
                    self.jsonlock = False
                    return;
            else:
                self.jsonlock = False
                await ctx.send("I do not have " + artistname + "in my datafiles is this the correct artist?")

    @commands.command()
    async def updatechannel(self, ctx, artistname, foldername, newchannelid):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        if self.jsonlock:
            return
        if not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in updatechannel ROLEID: " + str(self.roleid))
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                self.deviantlogger.error("updatechannel Command found that RoleID Is invalid.")
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if self.jsonlock:
            await ctx.send("ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return;
        if permitted:
            self.jsonlock = True
            if isinstance(newchannelid, int):
                self.deviantlogger.info("New Channelid Instance of Integer")
                channel = self.bot.get_channel(newchannelid)
                if channel.guild is None:
                    self.jsonlock = False
                    return;
                if not channel.guild.id == ctx.guild.id:
                    self.jsonlock = False
                    return

            elif isinstance(newchannelid, str):
                self.deviantlogger.info("New ChannelID Instance of String")
                try:
                    result = int(newchannelid)
                    channel = self.bot.get_channel(result)
                    if channel is None:
                        self.jsonlock = False
                        self.deviantlogger.info("INVALID ChannelID: Could not link with provided channelid")
                        await ctx.send(
                            "Error: The new channel id you provided is invalid, is it correct? Do I have permission to access it?")
                        return;
                except KeyError:
                    self.jsonlock = False
                    self.deviantlogger.error(
                        "Encountered KeyError when verifying newchannelid...newchannelid is not a discordchannelid")
                    await ctx.send("Error: Invalid discord channel id provided...")
                    return;
                if channel.guild is None:
                    self.jsonlock = False
                    return;
                if not channel.guild.id == ctx.guild.id:
                    self.jsonlock = False
                    return
            if artistExists(artistname):
                if folderExists(artistname, foldername):
                    updateDiscordChannel(artistname, foldername, newchannelid)
                    self.jsonlock = False
                    self.deviantlogger.info("Update Discord Channel finished!")
                    await ctx.send("Channel Updated!")
                else:
                    self.jsonlock = False
                    self.deviantlogger.warning("Folder " + foldername + " does not exist in artdata")
                    await ctx.send(
                        "I am not currently listening for new deviations on " + foldername + "is this the correct " \
                                                                                             "name for the folder?")
                    return;
            else:
                self.jsonlock = False
                self.deviantlogger.warning("Artist " + artistname + " is not in artdata")
                await ctx.send("I do not have " + artistname + "in my datafiles is this the correct artist?")

    @commands.command()
    async def manualSync(self, ctx):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                self.deviantlogger.error("manualsync Command found that RoleID Is invalid.")
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if self.jsonlock:
            await ctx.send("ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return;
        if permitted:
            self.jsonlock = True
            dirpath = os.getcwd()
            self.deviantlogger.info("manualSync: current directory is : " + dirpath)
            with open("artdata.json", "r") as jsonFile:
                self.deviantlogger.info("manualSync: Loading JSON file ArtData")
                artdata = json.load(jsonFile)
                for element in artdata["artist_store"]["used-artists"]:
                    self.deviantlogger.debug("Now starting sync for artist " + element)
                    for foldername in artdata["art-data"][element]["folder-list"]:
                        self.deviantlogger.debug("Starting Sync for folder " + foldername + " from artist " + element)
                        urls = dp.getGalleryFolder(element, True,
                                                   artdata['art-data'][element][foldername]["artist-folder-id"],
                                                   self.token, foldername,
                                                   artdata["art-data"][element][foldername]["inverted-folder"])
                        self.jsonlock = False
                        channel = self.bot.get_channel(
                            int(artdata["art-data"][element][foldername]["discord-channel-id"]))
                        if artdata["art-data"][element][foldername]["inverted-folder"]:
                            self.deviantlogger.debug("Folder is inverse")
                            storage = len(urls)
                            currentlength = len(urls)
                            while currentlength >= 1:
                                self.deviantlogger.debug("New Deviation URL: ")
                                self.deviantlogger.debug(str(urls[currentlength - 1]))
                                self.deviantlogger.debug("SyncGalleries: Now posting URL")
                                await channel.send(
                                    "New deviation from " + element + " you can view it here \n" + urls[
                                        currentlength - 1])
                                currentlength = currentlength - 1
                            self.jsonlock = False

                        else:
                            self.jsonlock = False
                            for url in urls:
                                self.deviantlogger.debug("New Deviation URL: ")
                                self.deviantlogger.debug(url)
                                self.deviantlogger.debug("ManualSync: Now posting URL")
                                await channel.send("New deviation from " + element + " you can view it here \n" + url)

    @commands.command()
    async def addartist(self, ctx, artistname, foldername, channelid, inverted):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            if ctx.author.guild_permissions.administrator:
                skiprolecheck = True
            else:
                self.deviantlogger.error("addartist Command found that RoleID Is invalid.")
                await ctx.send("Uh oh, there is an issue with the RoleID I am supposed to be looking for."
                               " If you are using selfhosting, set rolesetup-enabled in config.json to true or contact"
                               " DeviantCord Support if you are using our public bot")
                self.jsonlock = False
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                self.deviantlogger.debug("User that passed Guild check does not have permissiont to use addartist")
                return;
        if self.jsonlock:
            await ctx.send("ERROR: Another command using ArtData is currently running, please wait for that to finish!")
            return;
        if permitted:
            self.jsonlock = True
            self.deviantlogger.info("addArtist command invoked.");
            dirpath = os.getcwd()
            self.deviantlogger.info("current directory is : " + dirpath)
            self.deviantlogger.info("Channel ID" + str(channelid))
            self.deviantlogger.info("Artist: " + artistname)
            self.deviantlogger.info("Foldername: " + foldername)
            self.deviantlogger.info("Inverted: " + str(inverted))
            isInverted = False
            if isinstance(inverted, bool) == True:
                self.deviantlogger.info("Inverted confirmed as bool")
                isInverted = inverted
                self.deviantlogger.info("Inverted Value confirmed as ", isInverted)
            if isinstance(inverted, str) == True:
                self.deviantlogger.info("Inverted is confirmed as str")
                if inverted.lower() == "true":
                    isInverted = True
                elif inverted.lower() == "false":
                    isInverted = False
                else:
                    self.jsonlock = False
                    self.deviantlogger.debug("Inverted Value confirmed as " + str(isInverted))
                    await ctx.send("Error: Invalid inverted parameter. Must use true or false")
                    return;
            channel = self.bot.get_channel(int(channelid))
            if channel is None:
                self.jsonlock = False
                await ctx.send(
                    "Error: I could not link with the provided channelid, is it correct? Do I have permission to access it?" \
                    " I cannot tell because I am just a bot.")
                self.deviantlogger.info("Add Artist: Could not link with provided channelid")
                return;
            if channel.guild is None:
                self.jsonlock = False
                return;
            if not channel.guild.id == ctx.guild.id:
                self.jsonlock = False
                return
            if (artistExists(artistname) == True):
                self.jsonlock = False
                self.deviantlogger.debug("This artist is already in the JSON File!")
                await channel.send(
                    "This artist has already been added! Use the addfolder command to add another folder")
                return;
            if (artistExists(artistname) == False):
                requestedfolderid = dp.findFolderUUID(artistname, True, foldername, self.token)
                if requestedfolderid == "ERROR":
                    self.jsonlock = False
                    self.deviantlogger.debug("addartist: findFolderUUID request failed, artist does not exist. ")
                    await ctx.send(
                        "Error: Artist " + artistname + " does not exist. If your input did not seem to transfer" /
                        " completely surround the artist argument in quotations ")
                    return;
                elif requestedfolderid == "None":
                    self.jsonlock = False
                    self.deviantlogger.warning("addartist: findFolderUUID request failed, folder does not exist. ")
                    await ctx.send("Error: Folder " + foldername + " not found")
                    return;
                else:
                    self.deviantlogger.info("Successfully passed checks for addartist, creating ArtistData")
                    createArtistData(artistname, requestedfolderid, foldername, channelid, isInverted)
                    self.deviantlogger.info("Successfully created ArtistData, now populating...")
                    await channel.send("Added " + artistname + "'s " + foldername + " gallery folder")
                    await channel.send("Now populating with current deviations...")
                    self.deviantlogger.info("AddArtist: Opening artdata")
                    with open("artdata.json", "r") as jsonFile:
                        self.deviantlogger.info("Loading json for artdata")
                        artdata = json.load(jsonFile)
                        jsonFile.close()
                        dp.getGalleryFolderFT(artistname, True,
                                              artdata["art-data"][artistname.lower()][foldername]["artist-folder-id"],
                                              self.token, foldername)
                        self.jsonlock = False
                        self.deviantlogger.info("Finished populating deviations for " + artistname + "in " + foldername)
                        await channel.send(
                            "Finished populating...this channel will now receive updates on new deviations by "
                            + artistname + " in folder " + foldername)

    @help.error
    async def help_errorhandler(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            return;
        if isinstance(error, commands.errors.NoPrivateMessage):
            return;
        if isinstance(error, discord.ext.commands.NoPrivateMessage):
            return;
        else:
            self.deviantlogger.error("ERROR ENCOUNTERED with help command Error: " + str(error))
            self.deviantlogger.exception(error)

    @updateinverse.error
    @updatehybrid.error
    async def updateinverse_errorhandler(self, ctx, error):
        self.jsonlock = False;
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        else:
            return;
        if permitted:
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'inverse':
                    await ctx.send(
                        "Error: No inverse argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'artistname':
                    await ctx.send(
                        "Error: No artistname argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'foldername':
                    await ctx.send(
                        "Error: No foldername argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'channelid':
                    await ctx.send(
                        "Error: No channelid argument found, use " + self.prefix + "help for more information")
            elif isinstance(error, commands.errors.NoPrivateMessage):
                return
            else:
                self.deviantlogger.error(error)
                self.deviantlogger.exception(error)

    @updatechannel.error
    async def updatechannel_errorhandler(self, ctx, error):
        self.jsonlock = False;
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        else:
            return;
        if permitted:
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'inverted':
                    await ctx.send(
                        "Error: No inverted argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'artistname':
                    await ctx.send(
                        "Error: No artistname argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'foldername':
                    await ctx.send(
                        "Error: No foldername argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'channelid':
                    await ctx.send(
                        "Error: No channelid argument found, use " + self.prefix + "help for more information")
            elif isinstance(error, commands.errors.NoPrivateMessage):
                return
            else:
                self.deviantlogger.error(error)
                self.deviantlogger.exception(error)

    @setuprole.error
    async def setuprole_errorhandler(self, ctx, error):
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        else:
            return;
        if permitted:
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'roleid':
                    await ctx.send(
                        "Error: No roleid argument found, use " + self.prefix + "help for more information")
            if isinstance(error, commands.MissingPermissions):
                print("You don't have admin!")
            if isinstance(error, commands.errors.NoPrivateMessage):
                return
            else:
                self.deviantlogger.error(error)
                self.deviantlogger.exception(error)

    @addfolder.error
    async def addfolder_errorhandler(self, ctx, error):
        self.jsonlock = False;
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        else:
            return;
        if permitted:
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'inverted':
                    await ctx.send(
                        "Error: No inverted argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'artistname':
                    await ctx.send(
                        "Error: No artistname argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'foldername':
                    await ctx.send(
                        "Error: No foldername argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'channelid':
                    await ctx.send(
                        "Error: No channelid argument found, use " + self.prefix + "help for more information")
            if isinstance(error, urllib.error.HTTPError):
                if error.code == 401:
                    await ctx.send(
                        "Error: Automatic Token renewal didn't taken place, tokens will renew in 10 minutes, "
                        "if issues persist past 20 minutes please contact DeviantCord support.")
                    self.deviantlogger.error("addfolder command returned a HTTP 401, ")
                    await self.softTokenRenewal()
                if error.code == 503:
                    self.deviantlogger.error(
                        "addfolder command returned a HTTP 503, DA Servers are down for maintenance ")
                    await ctx.send("Error: DA's servers are down for maintenance. Please wait a few minutes");
                if error.code == 500:
                    self.deviantlogger.error("addfolder command returned a HTTP 500, Internal Error ")
                    await ctx.send("DA's servers returned a Error 500 Internal Error. Try again in a few minutes");
                if error.code == 429:
                    self.deviantlogger.error("addfolder command returned a HTTP 429, DA API Overloaded ")
                    await ctx.send("Error: DA API is currently overloaded...please wait for an hour. ")
                    return 429;
            if isinstance(error, commands.errors.NoPrivateMessage):
                return
            else:
                self.deviantlogger.error(error)
                self.deviantlogger.exception(error)

    @addartist.error
    async def addartist_errorhandler(self, ctx, error):
        self.jsonlock = False;
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not ctx.guild.id == self.guildid:
            return
        elif not self.publicmode:
            permitted = True
        else:
            return;
        if permitted:
            if isinstance(error, commands.MissingRequiredArgument):
                if error.param.name == 'inverted':
                    await ctx.send(
                        "Error: No inverted argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'artistname':
                    await ctx.send(
                        "Error: No artistname argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'foldername':
                    await ctx.send(
                        "Error: No foldername argument found, use " + self.prefix + "help for more information")
                if error.param.name == 'channelid':
                    await ctx.send(
                        "Error: No channelid argument found, use " + self.prefix + "help for more information")
            if isinstance(error, urllib.error.HTTPError):
                if error.code == 401:
                    await ctx.send(
                        "Error: Automatic Token renewal didn't taken place, tokens will renew in 10 minutes, if issues persist"
                        "past 20 minutes please contact DeviantCord support.")
                    self.deviantlogger.error("AddArtist command returned a HTTP 401, ")
                    self.deviantlogger.info("Invoking softTokenRenewal")
                    await self.softTokenRenewal()
                if error.code == 503:
                    self.deviantlogger.error(
                        "AddArtist command returned a HTTP 503, DA Servers are down for maintenance ")
                    await ctx.send(
                        "Error: DA's servers are down, check DeviantArt's Twitter and DeviantCord Support for more information");
                if error.code == 500:
                    self.deviantlogger.error("AddArtist command returned a HTTP 500, Internal Error ")
                    await ctx.send("DA's servers returned a Error 500 Internal Error. Try again in a few minutes");
                if error.code == 429:
                    self.deviantlogger.error("AddArtist command returned a HTTP 429, DA API Overloaded ")
                    await ctx.send("Error: DA API is currently overloaded...please wait for an hour. DeviantCord"
                                   "will continue to check for deviations at a delayed pace. Though commands will be "
                                   "delayed")
                    return 429;
            if isinstance(error, commands.errors.NoPrivateMessage):
                return
            else:
                self.deviantlogger.error(error)
                self.deviantlogger.exception(error)

    def error_handler(self, loop, context):
        self.jsonlock = False
        print("Exception: ", context['exception'])
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
                loop.run_until_complete(self.fix_error(1200))

        if str(context['exception']) == "HTTP Error 400: Bad request":
            logger.error("HTTP Error 400 encountered, ignoring...")
        elif str(context['exception']).find("HTTP Error 400") > -1:
            logger.error("HTTP Error 400 encountered")
            loop.run_until_complete(self.fix_error(120))
        elif str(context['exception']).find("HTTP Error 500") > -1:
            logger.error("HTTP Error 500 Encountered")
            loop.run_until_complete(self.fix_error(1200))
        elif str(context['exception']).find("HTTP Error 503") > -1:
            logger.error("Encountered a HTTP Error 503: DA's servers are likely down. Now creating task to renew token"
                         "in 20 minutes")
            loop.run_until_complete(self.fix_error(2400))
            # loop.run_until_complete(self.manualgetNewToken())
        elif str(context['exception']).find("HTTP Error 429") > -1:
            logger.error("Encountered a HTTP Error 429: Received Rate Limit response, toning down responses for "
                         "in 20 minutes")
            loop.run_until_complete(self.fix_error(600))
            # loop.run_until_complete(self.rateLimitMeasure())
        else:
            print("Exception encountered: ", context['exception'])
            logger.error("Exception Encountered " + str(context['exception']))
            loop.run_until_complete(self.fix_error(500))


def setup(bot):
    bot.remove_command("help")
    bot.add_cog(daCog(bot))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            return
