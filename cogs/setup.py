from discord import Interaction, File
from discord import app_commands
from discord.app_commands import AppCommandError
from discord.ext import commands
import json
from discord.ext.commands import GroupCog
import io

@app_commands.default_permissions(administrator=True)
class Setup(GroupCog, name='setup', description='Setup the bot and server!'):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.config = self.bot.config

    @app_commands.command(name='setup', description='Setup the bot and server!')
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, inter:Interaction):
        #Get the categories field and create a list of categories
        categories = []
        for category in self.config['categories']:
            categories.append(self.config['categories'][category]['name'])
        #Create the categories
        for category in categories:
            await inter.guild.create_category(category)
        #Get the channels field and create a list of channels
        channels = {}
        for category in self.config['categories']:
            for channel in self.config['categories'][category]['channels']:
                print(channel)
                channels[category] == channel

    #create a reset command that deletes all channels and categories, and then just creates 1 that says general
    @app_commands.command(name='reset', description='Reset the server!')
    @app_commands.checks.has_permissions(administrator=True)
    async def reset(self, inter:Interaction):
        #Delete all categories
        for category in inter.guild.categories:
            await category.delete()
        await inter.response.send_message('Reset the server!')

async def setup(bot:commands.Bot):
    await bot.add_cog(Setup(bot))