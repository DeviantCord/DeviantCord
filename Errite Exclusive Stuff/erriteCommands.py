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


class adminCog(commands.Cog):
    def __init__(self, bot):
        self.logname = "admincog"
        # This is the channelid in the DeviantCord Discord server that will be intercepted by the other bots.
        self.errite_channel_id = "replace this with channelid"
        self.adminlogger = logging.getLogger("admincog")
        self.adminlogger.setLevel(logging.DEBUG)
        self.adminhandler = TimedRotatingFileHandler(self.logname, when='h', interval=12, backupCount=2000,
                                                  encoding='utf-8')
        self.adminhandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.adminlogger.addHandler(self.adminhandler)
        self.prefix = "$"
        self.guildid = None
        self.location = "undefined"
        self.server = "undefined"
        self.client = "undefined"
        self.servers = None
        self.bot = bot

        if fileExists("config.json") == True:
            with open("config.json","r") as configJson:
                configData = json.load(configJson)
                self.prefix = configData["prefix"]
                self.location = configData["region"]
                self.server = configData["server"]
                self.client = configData["client"]
                self.guildid = configData["guildid"]


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



def setup(bot):
    bot.add_cog(adminCog(bot))
    print("erriteCommands bt-0.1.0")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            return





