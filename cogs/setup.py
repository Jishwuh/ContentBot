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

    @app_commands.command(name='channels', description='Setup the channels!')
    @app_commands.checks.has_permissions(administrator=True)
    async def channels(self, inter:Interaction):
        await inter.response.defer(thinking=True)
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
        await inter.followup.send('Setup for channels complete!')
        #Open the config and edit channelSetup to true
        with open('config.json', 'r') as f:
            config = json.load(f)
        config['channelSetup'] = True
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

        # --------------------------------------------------

    @app_commands.command(name='roles', description='Setup the roles!')
    @app_commands.checks.has_permissions(administrator=True)
    async def roles(self, inter:Interaction):
        for role in self.config['roles']:
            await inter.guild.create_role(name=self.config['roles'][role]['name'], color=self.config['roles'][role]['color'], hoist=self.config['roles'][role]['hoist'], mentionable=self.config['roles'][role]['mentionable'], permissions=Permissions(int(self.config['roles'][role]['permissions'])))
        await inter.followup.send('Roles Setup complete!')
        #Open the config and edit roleSetup to true
        with open('config.json', 'r') as f:
            config = json.load(f)
        config['roleSetup'] = True
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=4)

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