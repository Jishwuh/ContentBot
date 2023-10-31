import discord
from discord import Interaction
from discord import app_commands
from discord.app_commands import AppCommandError
# from discord.ext import commands
from discord.ext.commands import Bot, GroupCog
import os, sys
import sqlite3

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Debugging(GroupCog, name="debugging", description="Debugging commands"):
    def __init__(self, bot:Bot):
        self.bot = bot
        # super().__init__()
        #Create a database called "debugging.db" and make a table called "inactivecogs"
        self.db = sqlite3.connect(f"{os.getcwd()}/dbs/debugging.db")
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS inactivecogs (cogname TEXT)")
        self.db.commit()
        self.cursor.close()
        self.db.close()

    #make a command that unloads a specific cog and reloads it from user input
    @app_commands.command(name="reload", description="Reloads a cog")
    # @commands.has_permissions(administrator=True)
    async def reload(self, interaction: Interaction, cog:str):
        if os.path.exists(f"./cogs/{cog}.py") and "debugging" not in cog:
            try:
                #unload the cog
                await interaction.response.send_message(f"Unloading {cog}")
                await self.bot.unload_extension(f"cogs.{cog}")
                #load the cog
                await interaction.edit_original_response(content=f"Loading {cog}")
                await self.bot.load_extension(f"cogs.{cog}")
                #Send a message saying the cog was reloaded
                await interaction.edit_original_response(content=f"{cog} was reloaded!")
            except Exception as e:
                #Send a message saying the cog could not be reloaded
                await interaction.edit_original_response(content=f"{cog} could not be reloaded!")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                await interaction.followup.send(f"Error: {exc_type}\n{fname}\n{exc_tb.tb_lineno}\n{e}")
        else:
            #If the cog doesn't exist
            await interaction.response.send_message(f"{cog} doesn't exist!")

# make a command that loads a specific cog from user input
    @app_commands.command(name="load", description="Loads a cog")
    # @commands.has_permissions(administrator=True)
    async def load(self, interaction: Interaction, cog:str):
        if os.path.exists(f"./cogs/{cog}.py") and "debugging" not in cog:
            try:
                #load the cog
                await interaction.response.send_message(f"Loading {cog}")
                await self.bot.load_extension(f"cogs.{cog}")
                #Send a message saying the cog was reloaded
                await interaction.edit_original_response(content=f"{cog} was loaded!")
            except Exception as e:
                #Send a message saying the cog could not be reloaded
                await interaction.edit_original_response(content=f"{cog} could not be loaded!")
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                await interaction.followup.send(f"Error: {exc_type}\n{fname}\n{exc_tb.tb_lineno}\n{e}")
        else:
            #If the cog doesn't exist
            await interaction.response.send_message(f"{cog} doesn't exist!")

# make a command that unloads a specific cog from user input
    @app_commands.command(name="unload", description="Unloads a cog")
    # @commands.has_permissions(administrator=True)
    async def unload(self, interaction: Interaction, cog:str):
        if os.path.exists(f"./cogs/{cog}.py") and "debugging" not in cog:
            #unload the cog
            await interaction.response.send_message(f"Unloading {cog}")
            await self.bot.unload_extension(f"cogs.{cog}")
            #Send a message saying the cog was reloaded
            await interaction.edit_original_response(content=f"{cog} was unloaded!")
        else:
            #If the cog doesn't exist
            await interaction.response.send_message(f"{cog} doesn't exist!")

    #Deactivate a cog. Put the name of the cog in the database
    @app_commands.command(name="deactivate", description="Deactivates a cog")
    # @commands.has_permissions(administrator=True)
    async def deactivate(self, interaction: Interaction, cog:str):
        if os.path.exists(f"./cogs/{cog}.py") and "debugging" not in cog:
            #unload the cog
            await interaction.response.send_message(f"Unloading {cog}")
            await self.bot.unload_extension(f"cogs.{cog}")
            #Add the cog to the database
            self.db = sqlite3.connect("debugging.db")
            self.cursor = self.db.cursor()
            self.cursor.execute("INSERT INTO inactivecogs VALUES (?)", (cog,))
            self.db.commit()
            self.cursor.close()
            self.db.close()
            #Send a message saying the cog was deactivated
            await interaction.edit_original_response(content=f"{cog} was deactivated (unloaded) and will not be loaded on startup!")
        else:
            #If user doesn't have administrator permissions
            await interaction.response.send_message("You don't have permission to use this command!")

    #Activate a cog. Remove the name of the cog from the database
    @app_commands.command(name="activate", description="Activates a cog")
    # @commands.has_permissions(administrator=True)
    async def activate(self, interaction: Interaction, cog:str):
        if os.path.exists(f"./cogs/{cog}.py") and "debugging" not in cog:
            #Add the cog to the database
            self.db = sqlite3.connect("debugging.db")
            self.cursor = self.db.cursor()
            self.cursor.execute("DELETE FROM inactivecogs WHERE cogname = ?", (cog,))
            self.db.commit()
            self.cursor.close()
            self.db.close()
            #Send a message saying the cog was deactivated
            await interaction.response.send_message(f"{cog} was activated (loaded) and will be loaded on startup!")
        else:
            #If the cog doesn't exist
            await interaction.response.send_message(f"{cog} doesn't exist!")

    #Reload all
    @app_commands.command(name="reloadall", description="Reloads all cogs")
    # @commands.has_permissions(administrator=True)
    async def reloadall(self, interaction: Interaction):
        cogs = os.listdir("./cogs/")
        #Unload all cogs
        for cog in cogs:
            #make sure debugging cog isn't unloaded
            if "debugging" not in cog:
                #unload the cog
                #Make sure the cog is a .py
                if ".py" in cog:
                    #unload the cog
                    # await interaction.response.send_message(f"Unloading {cog}")
                    await self.bot.unload_extension(f"cogs.{cog[:-3]}")
        #Load all cogs
        for cog in cogs:
            #make sure debugging cog isn't loaded
            if "debugging" not in cog:
                #load the cog
                if ".py" in cog:
                    #load the cog
                    # await interaction.response.send_message(f"Loading {cog}")
                    await self.bot.load_extension(f"cogs.{cog[:-3]}")
        await interaction.response.send_message(f"All cogs were reloaded!")

    @app_commands.command(name = 'sync', description = 'Syncs all commands to current guild')
    async def sync(self, interaction: Interaction):
        self.bot.tree.copy_global_to(guild=interaction.guild)
        await self.bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message('Synced commands!', ephemeral=True)
        print(f'Synced commands to guild {interaction.guild} ({interaction.guild.id}), executed by {interaction.user} ({interaction.user.id})')

    @app_commands.command(name = 'sync_global', description = 'Syncs all commands to global')
    async def syncall(self, interaction: Interaction):
        if interaction.user.id == (775117485489258527 or 451160769711702016):
            await self.bot.tree.sync(guild=None)
            await interaction.response.send_message('Synced commands globally!', ephemeral=True)
            print(f'Synced commands to global, executed by {interaction.user} ({interaction.user.id})')
        else:
            await interaction.response.send_message('You don\'t have permission to use this command!', ephemeral=True)

    @app_commands.command(name = 'clear', description = 'Clears all commands from current guild')
    async def clear(self, interaction: Interaction):
        if interaction.user.id == (775117485489258527 or 451160769711702016):
            try:
                self.bot.tree.clear_commands(guild=interaction.guild)
                await self.bot.tree.sync(guild=interaction.guild)
                await interaction.response.send_message('Cleared commands!', ephemeral=True)
                print(f'Cleared commands in guild {interaction.guild} ({interaction.guild.id}), executed by {interaction.user} ({interaction.user.id})')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                await interaction.response.send_message(f'Failed to clear commands! Error: \n```{exc_type}\n{fname}\n{exc_tb.tb_lineno}```', ephemeral=True)
                print(f'Failed to clear commands in guild {interaction.guild} ({interaction.guild.id}), executed by {interaction.user} ({interaction.user.id})\n{exc_type}\n{fname}\n{exc_tb.tb_lineno}')
        else:
            await interaction.response.send_message('You don\'t have permission to use this command!', ephemeral=True)

    @app_commands.command(name = 'clear_global', description = 'Clears all commands from global')
    async def clearall(self, interaction: Interaction):
        if interaction.user.id == (775117485489258527 or 451160769711702016):
            try:
                self.bot.tree.clear_commands(guild=None)
                await self.bot.tree.sync(guild=None)
                await interaction.response.send_message('Cleared commands!', ephemeral=True)
                print(f'Cleared commands in global, executed by {interaction.user} ({interaction.user.id})')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                await interaction.response.send_message(f'Failed to clear commands! Error: \n```{exc_type}\n{fname}\n{exc_tb.tb_lineno}```', ephemeral=True)
                print(f'Failed to clear commands in global, executed by {interaction.user} ({interaction.user.id})\n{exc_type}\n{fname}\n{exc_tb.tb_lineno}')
        else:
            await interaction.response.send_message('You don\'t have permission to use this command!', ephemeral=True)

    async def cog_app_command_error(self, interaction:Interaction, error:AppCommandError):
        await interaction.response.send_message(error, ephemeral=True)

async def setup(bot: Bot):
    print("Debugging cog loaded!")
    await bot.add_cog(Debugging(bot))