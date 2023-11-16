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
import traceback

@app_commands.default_permissions(manage_roles=True)
class ReactionRoles(GroupCog, name='reactionroles', description='Reaction Roles Tools'):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.config = self.bot.config
        # Run the setup hook
        self.bot.loop.create_task(self.setup_hook())

    async def setup_hook(self):
        # Setup the database
        # Check if the database exists
        if not os.path.exists('dbs/reactionroles.db'):
            # Create the database
            async with sqlite3.connect('dbs/reactionroles.db') as conn:
                await conn.execute('CREATE TABLE IF NOT EXISTS reactionroles (message_id text, role_id INTEGER, emoji TEXT)')
                await conn.commit()

    async def addReactionRole(self, message_id:int, role_id:int, emoji:str):
        # Connect to the database
        async with sqlite3.connect('dbs/reactionroles.db') as conn:
            # Create a cursor
            # Add the command to the database
            await conn.execute('INSERT INTO reactionroles VALUES (?, ?, ?)', (message_id, role_id, emoji))
            # Commit the changes
            await conn.commit()

    async def getReactionRole(self, message_id:int, emoji:str):
        try:
            # Connect to the database
            async with sqlite3.connect('dbs/reactionroles.db') as conn:
                # Create a cursor
                cursor = await conn.cursor()
                # Get the command from the database
                await cursor.execute('SELECT * FROM reactionroles WHERE message_id=? AND emoji=?', (message_id, emoji))
                # Get the command
                command = await cursor.fetchone()
                if command is None:
                    return None
                # Return the command
                return command
        except Exception:
            traceback.print_exc()

    async def deleteReactionRole(self, message_id:int, emoji:str):
        try:
            # Connect to the database
            async with sqlite3.connect('dbs/reactionroles.db') as conn:
                # Create a cursor
                cursor = await conn.cursor()
                # Delete the command from the database
                await cursor.execute('DELETE FROM reactionroles WHERE message_id=? AND emoji=?', (message_id, emoji))
                # Commit the changes
                await conn.commit()
        except Exception:
            traceback.print_exc()

    @app_commands.command(name='add', description='Add a reaction role!')
    async def add(self, inter:Interaction, message:str, role:discord.Role, emoji:str):
        try:
            await inter.response.defer(thinking=True, ephemeral=True)
            # Get the message
            message: discord.Message = await inter.channel.fetch_message(int(message))
            # Add the reaction
            await message.add_reaction(emoji)
            # Add the reaction role to the database
            await self.addReactionRole(message.id, role.id, emoji)
            # Respond
            await inter.followup.send('Reaction Role added!', ephemeral=True)
        except Exception as e:
            await inter.followup.send(f'Something went wrong!\n\n```{e}```...', ephemeral=True)

    @app_commands.command(name='remove', description='Remove a reaction role!')
    async def remove(self, inter:Interaction, message:str, emoji:str):
        try:
            await inter.response.defer(thinking=True, ephemeral=True)
            # Get the message
            message: discord.Message = await inter.channel.fetch_message(int(message))
            # Remove the reaction
            await message.clear_reaction(emoji)
            # Remove the reaction role from the database
            await self.deleteReactionRole(message.id, emoji)
            # Respond
            await inter.followup.send('Reaction Role removed!', ephemeral=True)
        except Exception as e:
            await inter.followup.send(f'Something went wrong!\n\n```{e}```...', ephemeral=True)

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.command(name="create_embed", description="Create a reaction role embed")
    @app_commands.describe(color="Use a hex code to set the color of the embed (ex: #ffffff is white)")
    async def create_embed(self, inter:Interaction, title:str, color:str):
        try:
            await inter.response.defer(thinking=True, ephemeral=True)
            # Create the embed
            embed = discord.Embed(title=title, color=int(color.replace('#', ''), 16))
            # Send the embed
            message = await inter.channel.send(embed=embed)
            # Respond
            await inter.followup.send('Embed created!', ephemeral=True)
        except Exception as e:
            await inter.followup.send(f'Something went wrong!\n\n```{e}```...', ephemeral=True)

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.command(name="add_reaction_embed", description="Add a reaction to a reaction role embed")
    async def add_reaction(self, inter:Interaction, message:str, emoji:str, role:discord.Role):
        try:
            await inter.response.defer(thinking=True, ephemeral=True)
            # Get the message
            message: discord.Message = await inter.channel.fetch_message(int(message))
            #Get the description of the embed and add the reaction in format emoji - role
            description = message.embeds[0].description
            if description is None:
                description = ''
            description += f'\n{emoji} - {role.mention}'
            #Edit the embed
            await message.edit(embed=discord.Embed(title=message.embeds[0].title, description=description, color=message.embeds[0].color))
            #Add it to the database
            await self.addReactionRole(message.id, role.id, emoji)
            # Add the reaction
            await message.add_reaction(emoji)
            # Respond
            await inter.followup.send('Reaction added!', ephemeral=True)
        except Exception as e:
            print(traceback.format_exc())
            await inter.followup.send(f'Something went wrong!\n\n```{e}```...', ephemeral=True)

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.command(name="remove_reaction_embed", description="Remove a reaction from a reaction role embed")
    async def remove_reaction(self, inter:Interaction, message:str, emoji:str):
        try:
            await inter.response.defer(thinking=True, ephemeral=True)
            # Get the message
            message: discord.Message = await inter.channel.fetch_message(int(message))
            #Get the description of the embed, find the emoji - role and remove it from the description
            description = message.embeds[0].description
            #Get the index of the emoji
            index = description.find(emoji)
            #Get the index of the next line
            index2 = description.find('\n', index)
            #Remove the emoji - role from the description
            description = description.replace(description[index:index2], '')
            #Edit the embed
            await message.edit(embed=discord.Embed(title=message.embeds[0].title, description=description, color=message.embeds[0].color))
            #Remove the reaction from the database
            await self.deleteReactionRole(message.id, emoji)
            #Remove the reaction
            await message.clear_reaction(emoji)
            # Respond
            await inter.followup.send('Reaction removed!', ephemeral=True)
        except Exception as e:
            await inter.followup.send(f'Something went wrong!\n\n```{e}```...', ephemeral=True)

    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.command(name="delete_embed", description="Delete a reaction role embed")
    async def delete_embed(self, inter:Interaction, message:str):
        try:
            await inter.response.defer(thinking=True, ephemeral=True)
            # Get the message
            message: discord.Message = await inter.channel.fetch_message(int(message))
            #Delete the embed
            await message.delete()
            # Respond
            await inter.followup.send('Embed deleted!', ephemeral=True)
        except Exception as e:
            await inter.followup.send(f'Something went wrong!\n\n```{e}```...', ephemeral=True)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload:discord.RawReactionActionEvent):
        # Check if the user is a bot
        if payload.member.bot:
            return
        # Get the reaction role
        reactionRole = await self.getReactionRole(payload.message_id, payload.emoji.name)
        # Check if the reaction role exists
        if reactionRole is None:
            return
        # Get the role
        role = payload.member.guild.get_role(reactionRole[1])
        # Add the role
        await payload.member.add_roles(role)
        await payload.member.send(f'You have been given the role {role.name}!')
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload:discord.RawReactionActionEvent):
        # Get the reaction role
        reactionRole = await self.getReactionRole(payload.message_id, payload.emoji.name)
        # Check if the reaction role exists
        if reactionRole is None:
            return
        # Get the guild
        guild = self.bot.get_guild(payload.guild_id)
        # Get the member
        member = guild.get_member(payload.user_id)
        # Get the role
        role = guild.get_role(reactionRole[1])
        # Remove the role
        await member.remove_roles(role)
        await member.send(f'You have removed the role {role.name}!')

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))