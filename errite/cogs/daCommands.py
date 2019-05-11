import json
import os
import discord
from logging.handlers import TimedRotatingFileHandler
import asyncio
import datetime
import logging
from discord.ext import commands
from discord.ext.commands import has_permissions, guild_only
import errite.da.daParser as dp
from errite.da.jsonTools import createArtistData, artistExists, folderExists, createFolderData, \
    updateDiscordChannel, updateRole, updateinverseproperty
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
        self.roleid = 0
        self.publicmode = None
        self.datevar = datetime.datetime.now().strftime("%Y-%m-%d%H%M%S")
        self.whiletrigger = False
        self.logname = "deviantcog-" + self.datevar
        if fileExists(self.logname + self.datevar):
            counter = 0
            while not self.whiletrigger:
                counter += 1
                tempfilename = self.logname + "-" + str(counter)
                if not fileExists(tempfilename):
                    self.logname = tempfilename
                    self.whiletrigger = True

        self.deviantlogger = logging.getLogger("deviantcog")
        self.deviantlogger.setLevel(logging.DEBUG)
        self.dlhandler = TimedRotatingFileHandler(self.logname, when='h',interval=12, backupCount=2000, encoding='utf-8')
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
        self.deviantlogger.info("Now creating tasks...")
        self.bot.loop.create_task(self.getNewToken())
        self.bot.loop.set_exception_handler(error_handler)
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
            self.token = dp.getToken(self.clientsecret,self.clientid)
            await asyncio.sleep(2400)

    async def manualgetNewToken(self):
        """
        Gets a new token from DeviantArt with no params, grabs the clientid and clientsecret from the class file.
        This function is only ran when a token error occurs and fixes it.
        """
        self.deviantlogger.info("ManualGetToken: Getting new token")
        self.token = dp.getToken(self.clientsecret,self.clientid)
    async def syncGalleries(self):
        """
        Checks programmed gallery folders for Deviations. This is the method that is ran to trigger every x minutes
        depending on what the user has it configured to.
        """
        if self.passedJson == True:

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
                            self.deviantlogger.debug("Starting Sync for folder " + foldername + " from artist " + element)
                            urls = dp.getGalleryFolder(element, True,
                                                       artdata['art-data'][element][foldername]["artist-folder-id"],
                                                       self.token,
                                                       foldername,
                                                       artdata['art-data'][element][foldername]["inverted-folder"])
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
                                        "New deviation from " + element + " you can view it here \n" + urls[currentlength-1])
                                    currentlength = currentlength - 1

                            else:
                                for url in urls:
                                    self.deviantlogger.debug("New Deviation URL: ")
                                    self.deviantlogger.debug(url)
                                    self.deviantlogger.debug("SyncGalleries: Now posting URL")
                                    await channel.send("New deviation from " + element + " you can view it here \n" + url)
                    await asyncio.sleep(self.time)
    @commands.command()
    async def help(self, ctx):
        self.deviantlogger.info("Help command invoked")
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            if ctx.author.server_permission.administrator:
                skiprolecheck = True
            else:
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        text = "**DeviantCord Help Guide**\n**" + self.prefix +\
               "help** - Gives a list of command with explaination\n**NOTE: Inverse means that newest deviations are at the top, instead of the bottom. Use true or false to answer it**\n**" + \
               self.prefix + "addfolder** *<artist_username>* *<folder>* *<channel_id>* *<inverse>* - Adds another artists gallery folder for the bot to notify the specified channel of new deviations. Use this when your adding another folder to an artist already added \n**" + \
               self.prefix\
               + "addartist** *<artist_username>* *<folder>* *<channel_id>* *<inverse>*- Used to add an artist and the first folder into the bots datafile. Use this command when you are adding an artist for the first time!\n**" + \
               self.prefix + "manualSync** - Will check all configured folders for new deviations instead of waiting for the timer to trigger and start the check *DO NOT SPAM THIS*\n" + "**" + \
               self.prefix + "updateinverse** *<artist_username> *<folder>* *<inverse>* - Updates the inverse property of a existing folder listener\n" + \
               "**" + self.prefix + "updatechannel** *<artist_username> *<folder>* *<channelid>* - Updates the discord channel that notifications will be posted for an existing folder listener\n" + \
               "** __ADMIN COMMANDS__** \n" + \
               "**WARNING: The COMMANDS BELOW WILL RESTART DEVIANTCORD, MAKE SURE YOU OR YOUR STAFF ARE NOT ADDING ANY NEW FOLDERS BEFORE EXECUTING COMMANDS BELOW**\n"+ \
               "**" + self.prefix + "setprefix** *<prefix>* - Updates the prefix for all commands and reloads\n" + \
               "**" + self.prefix + "reload** - Reloads DeviantCord"

        await ctx.send(text)

    @commands.command()
    @has_permissions(administrator=True)
    async def setuprole(self, ctx, roleid):
        if self.enablesr:
            if ctx.guild is None:
                return;
            if self.guildid is 0:
                self.deviantlogger.info('Setup has been invoked')
                updateRole(int(roleid), ctx.guild.id)
                await ctx.send("Role has been setup!")
                self.roleid = roleid
        else:
            return

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
        if ctx.guild.id == self.guildid:
            permitted = True
        elif not self.publicmode:
            permitted = True
        else:
            return;
        if permitted:
            self.deviantlogger.info("addFolder command invoked.");
            dirpath = os.getcwd()
            self.deviantlogger.info("current directory is : " + str(dirpath))
            self.deviantlogger.info("Channel ID" + str(channelid))
            self.deviantlogger.info("Artist: " + artistname)
            self.deviantlogger.info("Foldername: " + foldername)
            print("Inverted: " + inverted)
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
                    self.deviantlogger.debug("Inverted Value confirmed as " + str(isInverted))
                    await ctx.send("Error: Invalid inverted parameter. Must use true or false")
                    return;
            print("Checking channel")
            channel = self.bot.get_channel(int(channelid))
            if channel is None:
                self.deviantlogger.info("Could not link with provided channelid...sending message to channel")
                await ctx.send(
                    "Error: I could not link with the provided channelid, is it correct? Do I have permission to access it?" \
                    " I cannot tell because I am just a bot.")
                return;
            if channel.guild is None:
                return;
            if not channel.guild.id == ctx.guild.id:
                return
            if (artistExists(artistname) == False):
                self.deviantlogger.info("Addfolder command was just ran, but the artist is not in artdata!")
                await channel.send(
                    "You need to run the addartist command for a new artist. Use the help command for more information")
                return;
            if (folderExists(artistname, foldername) == True):
                self.deviantlogger.info("This artist is already in the JSON File!")
                await channel.send("I already know about this folder. Do you mean a different folder?")
            if (folderExists(artistname, foldername) == False):
                requestedfolderid = dp.findFolderUUID(artistname, True, foldername, self.token)
                if requestedfolderid == "ERROR":
                    self.deviantlogger.info("Invalid artist lookup, input: " + artistname)
                    await ctx.send("Error: This Artist does not exist!")
                    return;
                if requestedfolderid == "None":
                    self.deviantlogger.info("Artist folder not found, for " + artistname + " in" + foldername)
                    await ctx.send("Error: Folder " + foldername + " not found")
                    return;
                else:
                    self.deviantlogger.info("addfolder command passed all checks, now proceeding to execution")
                    self.deviantlogger.debug("IsInverted: " + str(isInverted))
                    self.deviantlogger.info("Now creating folder data for " + artistname + "in " + foldername)
                    createFolderData(artistname, requestedfolderid, foldername, channelid, isInverted)
                    await channel.send("Add1ed " + artistname + "'s " + foldername + " gallery folder")
                    self.deviantlogger.info("Now populating folder data with deviations for " + artistname + "in " + foldername)
                    await channel.send("Now populating with current deviations...")
                    with open("artdata.json", "r") as jsonFile:
                        artdata = json.load(jsonFile)
                        jsonFile.close()
                        self.deviantlogger.info("Addfolder: Now running getGalleryFolderFT")
                        dp.getGalleryFolderFT(artistname, True,
                                              artdata["art-data"][artistname.lower()][foldername]["artist-folder-id"],
                                              self.token, foldername)
                        await channel.send(
                            "Finished populating...this channel will now receive updates on new deviations by "
                            + artistname + " in folder " + foldername)
                        self.deviantlogger.info("Finished populating folder!")

    @commands.command()
    async def updateinverse(self, ctx, artistname, foldername, inverse):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in updatechannel ROLEID: " + str(self.roleid))
            if ctx.author.server_permission.administrator:
                skiprolecheck = True
            else:
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if permitted:
            if isinstance(inverse, bool):
                self.deviantlogger.info("New Inverse Instance of bool")
            elif isinstance(inverse, str):
                self.deviantlogger.info("New Inverse Instance of String")
                self.deviantlogger.debug("OBTAINED INVERSE: " + inverse)
                self.deviantlogger("CHECK: " + inverse.lower())
                print(inverse.lower())
                if inverse.lower() == "true":
                    print("Inverse is true")
                elif inverse.lower() is "false":
                    print("Inverse is false")
                else:
                    await ctx.send("Invalid inverse given...")
                    return

            if artistExists(artistname):
                if folderExists(artistname, foldername):
                    updateinverseproperty(artistname, foldername, inverse)
                    self.deviantlogger.info("Update inverse finished for " + artistname + " on" + foldername)
                    await ctx.send("Inverse Updated for " + artistname + " in" + foldername)
                else:
                    await ctx.send(
                        "I am not currently listening for new deviations on " + foldername + "is this the correct " \
                                                                                             "name for the folder?")
                    return;
            else:
                await ctx.send("I do not have " + artistname + "in my datafiles is this the correct artist?")


    @commands.command()
    async def updatechannel(self, ctx, artistname, foldername, newchannelid):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            self.deviantlogger.error("Detected invalid roleid in updatechannel ROLEID: " + str(self.roleid))
            if ctx.author.server_permission.administrator:
                skiprolecheck = True
            else:
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if permitted:
            if isinstance(newchannelid, int):
                self.deviantlogger.info("New Channelid Instance of Integer")
                channel = self.bot.get_channel(newchannelid)
                if channel.guild is None:
                    return;
                if not channel.guild.id == ctx.guild.id:
                    return

            elif isinstance(newchannelid, str):
                self.deviantlogger.info("New ChannelID Instance of String")
                try:
                    result = int(newchannelid)
                    channel = self.bot.get_channel(result)
                    if channel is None:
                        self.deviantlogger.info("INVALID ChannelID: Could not link with provided channelid")
                        await ctx.send(
                            "Error: The new channel id you provided is invalid, is it correct? Do I have permission to access it?")
                        return;
                except KeyError:
                    self.deviantlogger.error("Encountered KeyError when verifying newchannelid...newchannelid is not a discordchannelid")
                    await ctx.send("Error: Invalid discord channel id provided...")
                    return;
                if channel.guild is None:
                    return;
                if not channel.guild.id == ctx.guild.id:
                    return
            if artistExists(artistname):
                if folderExists(artistname, foldername):
                    updateDiscordChannel(artistname, foldername, newchannelid)
                    self.deviantlogger.info("Update Discord Channel finished!")
                    await ctx.send("Channel Updated!")
                else:
                    self.deviantlogger.warning("Folder " + foldername + " does not exist in artdata")
                    await ctx.send(
                        "I am not currently listening for new deviations on " + foldername + "is this the correct " \
                                                                                             "name for the folder?")
                    return;
            else:
                self.deviantlogger.warning("Artist " + artistname + " is not in artdata")
                await ctx.send("I do not have " + artistname + "in my datafiles is this the correct artist?")

    @commands.command()
    async def manualSync(self, ctx):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            if ctx.author.server_permission.administrator:
                skiprolecheck = True
            else:
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                return;
        if permitted:
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
                                self.deviantlogger.debug("ManualSync: Now posting URL")
                                await channel.send("New deviation from " + element + " you can view it here \n" + url)

    @commands.command()
    async def addartist(self, ctx, artistname, foldername, channelid, inverted):
        skiprolecheck = False
        if ctx.guild is None:
            return;
        elif ctx.guild.id == self.guildid:
            permitted = True
        elif not self.publicmode:
            permitted = True
        if ctx.guild.get_role(self.roleid) is None:
            if ctx.author.server_permission.administrator:
                skiprolecheck = True
            else:
                return;
        if not skiprolecheck:
            if not ctx.author.top_role >= ctx.guild.get_role(self.roleid):
                self.deviantlogger.debug("User that passed Guild check does not have permissiont to use addartist")
                return;
        if permitted:
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
                    self.deviantlogger.debug("Inverted Value confirmed as " + str(isInverted))
                    await ctx.send("Error: Invalid inverted parameter. Must use true or false")
                    return;
            channel = self.bot.get_channel(int(channelid))
            if channel is None:
                await ctx.send(
                    "Error: I could not link with the provided channelid, is it correct? Do I have permission to access it?" \
                    " I cannot tell because I am just a bot.")
                self.deviantlogger.info("Add Artist: Could not link with provided channelid")
                return;
            if channel.guild is None:
                return;
            if not channel.guild.id == ctx.guild.id:
                return
            if (artistExists(artistname) == True):
                self.deviantlogger.debug("This artist is already in the JSON File!")
                await channel.send(
                    "This artist has already been added! Only one folder can be listened to at this time!")
            if (artistExists(artistname) == False):
                requestedfolderid = dp.findFolderUUID(artistname, True, foldername, self.token)
                if requestedfolderid == "ERROR":
                    self.deviantlogger.debug("addartist: findFolderUUID request failed, artist does not exis. ")
                    await ctx.send(
                        "Error: Artist " + artistname + " does not exist. If your input did not seem to transfer" /
                        " completely surround the artist argument in quotations ")
                elif requestedfolderid == "None":
                    self.deviantlogger.warning("addartist: findFolderUUID request failed, folder does not exis. ")
                    await ctx.send("Error: Folder " + foldername + " not found")
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


    @updateinverse.error
    async def updateinverse_errorhandler(self, ctx, error):
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
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
            if isinstance(error, commands.errors.NoPrivateMessage):
                return


    @updatechannel.error
    async def updatechannel_errorhandler(self, ctx, error):
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
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
            if isinstance(error, commands.errors.NoPrivateMessage):
                return

    @setuprole.error
    async def setuprole_errorhandler(self, ctx, error):
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
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


    @addfolder.error
    async def addfolder_errorhandler(self, ctx, error):
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
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
                        "Error: Automatic Token renewal didn't taken place, the token is now renewed, please try again.")
                    self.deviantlogger.error("addfolder command returned a HTTP 401, ")
                    self.manualgetNewToken()
                if error.code == 503:
                    self.deviantlogger.error("addfolder command returned a HTTP 503, DA Servers are down for maintenance ")
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

    @addartist.error
    async def addartist_errorhandler(self,ctx, error):
        try:
            if ctx.guild.id is None:
                return;
        except AttributeError:
            return;
        if ctx.guild.id == self.guildid:
            permitted = True
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
                        "Error: Automatic Token renewal didn't taken place, the token is now renewed, please try again.")
                    self.deviantlogger.error("AddArtist command returned a HTTP 401, ")
                    self.manualgetNewToken()
                if error.code == 503:
                    self.deviantlogger.error("AddArtist command returned a HTTP 503, DA Servers are down for maintenance ")
                    await ctx.send("Error: DA's servers are down for maintenance. Please wait a few minutes");
                if error.code == 500:
                    self.deviantlogger.error("AddArtist command returned a HTTP 500, Internal Error ")
                    await ctx.send("DA's servers returned a Error 500 Internal Error. Try again in a few minutes");
                if error.code == 429:
                    self.deviantlogger.error("AddArtist command returned a HTTP 429, DA API Overloaded ")
                    await ctx.send("Error: DA API is currently overloaded...please wait for an hour. ")
                    return 429;
            if isinstance(error, commands.errors.NoPrivateMessage):
                return


def error_handler(loop, context):
    print("Exception: ", context['exception'])
    logger = logging.getLogger("deviantcog")
    if str(context['exception']) == "HTTP Error 401: Unauthorized":
        print("Your DA info is invalid, please check client.json to see if it matches your DA developer page")
        logger("Your DA info is invalid, please check client.json to see if it matches your DA developer page")
        loop.stop()
        try:
            exit(211)
        except SystemExit:
            os._exit(211)
    if str(context['exception']) == "HTTP Error 400: Bad request":

        print("You need to setup your DA info for the bot, otherwise please check client.json")
        logger.error("You need to setup your DA info for the bot, otherwise please check client.json")
        loop.stop()
        try:
            exit(210)
        except SystemExit:
            os._exit(210)
    else:
        print("Exception encountered: ", context['exception'])
        logger.error("Exception Encountered " + str(context['exception']))


def setup(bot):
        bot.remove_command("help")
        bot.add_cog(daCog(bot))