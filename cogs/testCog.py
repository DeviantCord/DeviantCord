#
# THIS Python file is property of Errite Games LLC
# All Rights Reserved
#
#
#
from logging.handlers import TimedRotatingFileHandler
import json
import logging

import sentry_sdk
from discord.ext import commands
from discord.ext.commands import CommandNotFound, has_permissions
from sentry_sdk import capture_exception, configure_scope
from errite.tools.mis import fileExists


class testCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        sentry_sdk.init("https://9a825fa0779744fd99f475cb5a4775dc@sentry.io/1876771")
    @commands.command()
    async def testError(self, ctx):
        print("Triggered")
        await ctx.send("Acknowledged, check Sentry and Console")
        division_by_zero = 1 / 0
        print("Did this work?")

    @testError.error
    async def error_handler(self, ctx, error):
        with configure_scope() as scope:
            scope.set_extra("command", ctx.command.name)
            scope.set_extra("discord-guild", ctx.guild.name)
            scope.set_extra("guild-id", ctx.guild.id)
            scope.set_extra("channel-id", ctx.channel.id)
            scope.set_extra("channel-name", ctx.channel.name)
            capture_exception(error)


def setup(bot):
    bot.add_cog(testCog(bot))
    print("erriteCommands bt-0.1.0")

    @bot.event
    async def on_command_error(ctx, error):
        print("Error reached")
        raise error["context"]
        if isinstance(error, CommandNotFound):
            return





