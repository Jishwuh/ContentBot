from discord import Interaction, File
from discord import app_commands
from discord.app_commands import AppCommandError
from discord.ext import commands
from discord import PermissionOverwrite
from discord import Permissions
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
        await inter.response.defer(thinking=True)
        #Create the roles
        for role in self.config['roles']:
            await inter.guild.create_role(name=self.config['roles'][role]['name'], color=self.config['roles'][role]['color'], hoist=self.config['roles'][role]['hoist'], mentionable=self.config['roles'][role]['mentionable'], permissions=Permissions(int(self.config['roles'][role]['permissions'])))
        # CHANNEL AND CATEGORIES DONE
        # --------------------------------------------------
        for category in self.config['categories']:
            #Create the category
            categoryCreate = await inter.guild.create_category_channel(name=self.config['categories'][category]['name'])
            #Create the channels
            for channel in self.config['categories'][category]['channels']:
                #check if there is a user_limit field
                if 'user_limit' in channel:
                    channelCreate = await inter.guild.create_voice_channel(name=channel['name'], category=categoryCreate, user_limit=channel['user_limit'])
                else:
                    channelCreate = await inter.guild.create_text_channel(name=channel['name'], category=categoryCreate)
                #Set the permissions
                await channelCreate.set_permissions(inter.guild.default_role, overwrite=PermissionOverwrite.from_pair(allow=Permissions(int(channel['allow'])), deny=Permissions(int(channel['deny']))))
        await inter.followup.send('Setup complete!')
        # --------------------------------------------------

    #Duplicate the setup command but its a mock, and just responds with the channels and categories and doesn't make them
    @app_commands.command(name='mock', description='Mock the setup command!')
    @app_commands.checks.has_permissions(administrator=True)
    async def mock(self, inter:Interaction):
        #Get the categories field and create a list of categories
        categories = []
        for category in self.config['categories']:
            categories.append(self.config['categories'][category]['name'])
        #Create the categories
        for category in categories:
            await inter.response.send_message(category)
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
        await inter.response.defer(thinking=True)
        #Delete all categories and channels except for the general channel
        for category in inter.guild.categories:
            await category.delete()
        for channel in inter.guild.channels:
            if channel.name != 'general':
                await channel.delete()
        #Delete all the roles except ContentBot and admin
        for role in inter.guild.roles:
            # print(role.name)
            if "@everyone" in role.name or "ContentBot" in role.name or "boss" in role.name:
                pass
            else:
                await role.delete()
        await inter.followup.send('Reset complete!')
async def setup(bot:commands.Bot):
    await bot.add_cog(Setup(bot))