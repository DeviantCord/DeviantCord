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
        if fileExists("config.json") == True:
            with open("config.json","r") as configJson:
                configData = json.load(configJson)
                self.prefix = configData["prefix"]
                self.location = configData["region"]
                self.server = configData["server"]
                self.client = configData["client"]
                self.guildid = configData["guildid"]


def setup(bot):
    bot.add_cog(adminCog(bot))
    print("erriteMod0 bt-0.1.0")

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, CommandNotFound):
            return





