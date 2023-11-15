from discord import Interaction, File
from discord import app_commands
from discord.app_commands import AppCommandError
from discord.ext import commands
from discord import PermissionOverwrite
from discord import Permissions
import discord
import discord.ext
import json
import os
from discord.ext.commands import GroupCog
import io
import aiosqlite3 as sqlite3

@app_commands.default_permissions(administrator=True)
class CustomCommands(GroupCog, name='customcommands', description='Custom Commands Tools'):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.config = self.bot.config
        #Run the setup hook
        self.prefix = self.config['customCommandsPrefix']
        self.bot.loop.create_task(self.setup_hook())
        self.cursor = self.bot.loop.create_task(self.getCursor())

    async def setup_hook(self):
        #Create the database
        #Check if the database exists
        if not os.path.exists('dbs/customcommands.db'):
            #Create the database
            open('dbs/customcommands.db', 'w').close()
            #Connect to the database
            async with sqlite3.connect('dbs/customcommands.db') as conn:
                await conn.execute('CREATE TABLE IF NOT EXISTS commands (command text, response text, image text)')
                await conn.commit()

    async def getCursor(self):
        #Connect to the database
        async with sqlite3.connect('dbs/customcommands.db') as conn:
            #Create a cursor
            cursor = await conn.cursor()
            #Return the cursor
            return cursor

    async def addCommand(self, command:str, response:str, image:str=None):
        #Connect to the database
        async with sqlite3.connect('dbs/customcommands.db') as conn:
            #Create a cursor
            #Add the command to the database
            await conn.execute('INSERT INTO commands VALUES (?, ?, ?)', (command, response, image))
            #Commit the changes
            await conn.commit()

    async def getCommand(self, command:str):
        #Connect to the database
        async with sqlite3.connect('dbs/customcommands.db') as conn:
            #Create a cursor
            cursor = await conn.cursor()
            #Get the command from the database
            await cursor.execute('SELECT * FROM commands WHERE command=?', (command,))
            #Get the command
            command = await cursor.fetchone()
            #Return the command
            return command
    
    async def deleteCommand(self, command:str):
        #Connect to the database
        async with sqlite3.connect('dbs/customcommands.db') as conn:
            #Create a cursor
            cursor = await conn.cursor()
            #Delete the command from the database
            await cursor.execute('DELETE FROM commands WHERE command=?', (command,))
            #Commit the changes
            await conn.commit()

    @app_commands.command(name='add', description='Add a custom command!')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def add(self, interaction:Interaction, command:str, response:str, image:discord.Attachment=None):
        await interaction.response.defer(thinking=True)
        #Check if the command already exists'
        commandExists = await self.getCommand(command)
        if commandExists is None:
            #Add the command to the database
            await self.addCommand(command, response, [image.filename if image is not None else None][0])
            #Save the image
            if image is not None:
                await image.save(f'commandImages/{image.filename}')
            #Send the response
            await interaction.followup.send('Command added!')
        else:
            await interaction.followup.send('That command already exists!')

    @app_commands.command(name='delete', description='Delete a custom command!')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def delete(self, interaction:Interaction, command:str):
        await interaction.response.defer(thinking=True)
        #Check if the command exists
        commandExists = await self.getCommand(command)
        if commandExists is not None:
            #Delete the command
            await self.deleteCommand(command)
            #Delete the image
            if commandExists[2] is not None:
                os.remove(f'commandImages/{commandExists[2]}')
            #Send the response
            await interaction.followup.send('Command deleted!')
        else:
            await interaction.followup.send('That command does not exist!')

    @app_commands.command(name='edit', description='Edit a custom command!')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def edit(self, interaction:Interaction, command:str, response:str, image:discord.Attachment=None):
        await interaction.response.defer(thinking=True)
        #Check if the command exists
        commandExists = await self.getCommand(command)
        if commandExists is not None:
            #Delete the command
            await self.deleteCommand(command)
            #Delete the image
            if commandExists[2] is not None:
                os.remove(f'commandImages/{commandExists[2]}')
            #Add the command
            await self.addCommand(command, response, image.filename)
            #Save the image
            if image is not None:
                await image.save(f'commandImages/{image.filename}')
            #Send the response
            await interaction.followup.send('Command edited!')
        else:
            await interaction.followup.send('That command does not exist!')

    @app_commands.command(name='list', description='List all custom commands!')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def list(self, interaction:Interaction):
        await interaction.response.defer(thinking=True)
        #Connect to the database
        conn = await sqlite3.connect('dbs/customcommands.db')
        #Create a cursor
        cursor = await conn.cursor()
        #Get all the commands
        await cursor.execute('SELECT * FROM commands')
        #Get the commands
        commands = await cursor.fetchall()
        #Create the embed
        embed = discord.Embed(title='Custom Commands', description='Here are all the custom commands!', color=discord.Color.green())
        #Add the fields
        for command in commands:
            embed.add_field(name=command[0], value=command[1], inline=False)
        #Send the embed
        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        #Check if the message is a command
        if message.content.startswith(self.prefix):
            #Get the command
            command = message.content.split(self.prefix)[1]
            #Get the command from the database
            commandExists = await self.getCommand(command)
            if commandExists is not None:
                #Send the response
                if commandExists[2] is not None:
                    await message.channel.send(content=commandExists[1], file=discord.File(f'commandImages/{commandExists[2]}'))
                else:
                    await message.channel.send(commandExists[1])
async def setup(bot):
    await bot.add_cog(CustomCommands(bot))