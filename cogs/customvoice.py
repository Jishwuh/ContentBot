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
from discord import CategoryChannel
import aiosqlite3 as sqlite3

# @app_commands.default_permissions(administrator=True)
class CustomVoice(GroupCog, name='customvoice', description='Custom Voice Channel Commands'):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.config = self.bot.config
        #Run the setup hook
        self.bot.loop.create_task(self.setup_hook())
        
    async def setup_hook(self):
        #Create the database
        #Check if the database exists
        if not os.path.exists('dbs/customvoice.db'):
            #Create the database
            open('dbs/customvoice.db', 'w').close()
        async with sqlite3.connect('dbs/customvoice.db') as db:
            #What we need is a database that will store a channel ID, the user ID of the channel owner (primary key).
            #The channel ID will be the channel ID of the channel that the user created.
            #The user ID will be the user ID of the user that created the channel.
            await db.execute('CREATE TABLE IF NOT EXISTS customvoice (channel_id INTEGER, user_id INTEGER PRIMARY KEY)')
            await db.commit()
            print('Custom Voice Database Created!')
        #Now create another database named channelsinit.db, which will store the channel ID of the voice channels that are setup
        #Check if the database exists
        if not os.path.exists('dbs/channelsinit.db'):
            #Create the database
            open('dbs/channelsinit.db', 'w').close()
        async with sqlite3.connect('dbs/channelsinit.db') as db:
            await db.execute('CREATE TABLE IF NOT EXISTS channelsinit (channel_id INTEGER PRIMARY KEY)')
            await db.commit()
            print('Channels Init Database Created!')
            
    #create a function that will take a channel ID and check if it is in the database
    async def check_channel_init(self, channel_id):
        async with sqlite3.connect('dbs/channelsinit.db') as db:
            cursor = await db.execute('SELECT channel_id FROM channelsinit WHERE channel_id = ?', (channel_id,))
            result = await cursor.fetchone()
            await cursor.close()
            if result is None:
                return False
            else:
                return True
            
    #create a function that will take a channel ID and add it to the database
    async def add_channel_init(self, channel_id):
        async with sqlite3.connect('dbs/channelsinit.db') as db:
            await db.execute('INSERT INTO channelsinit (channel_id) VALUES (?)', (channel_id,))
            await db.commit()

    async def remove_channel_init(self, channel_id):
        async with sqlite3.connect('dbs/channelsinit.db') as db:
            await db.execute('DELETE FROM channelsinit WHERE channel_id = ?', (channel_id,))
            await db.commit()
        
    #create functions for adding a channel to the database, removing a channel from the database, changing the channel owner, and getting the channel owner
    async def check_channel(self, channel_id):
        async with sqlite3.connect('dbs/customvoice.db') as db:
            cursor = await db.execute('SELECT channel_id FROM customvoice WHERE channel_id = ?', (channel_id,))
            result = await cursor.fetchone()
            await cursor.close()
            if result is None:
                return False
            else:
                return True

    async def add_channel(self, channel_id, user_id):
        async with sqlite3.connect('dbs/customvoice.db') as db:
            await db.execute('INSERT INTO customvoice (channel_id, user_id) VALUES (?, ?)', (channel_id, user_id))
            await db.commit()
            

    async def remove_channel(self, channel_id):
        async with sqlite3.connect('dbs/customvoice.db') as db:
            await db.execute('DELETE FROM customvoice WHERE channel_id = ?', (channel_id,))
            await db.commit()

    async def change_owner(self, channel_id, user_id):
        async with sqlite3.connect('dbs/customvoice.db') as db:
            await db.execute('UPDATE customvoice SET user_id = ? WHERE channel_id = ?', (user_id, channel_id))
            await db.commit()

    async def get_owner(self, channel_id):
        async with sqlite3.connect('dbs/customvoice.db') as db:
            cursor = await db.execute('SELECT user_id FROM customvoice WHERE channel_id = ?', (channel_id,))
            result = await cursor.fetchone()
            await cursor.close()
            return result[0]
        
    #Make a channel delete listener that checks if a channel in the channelsinit database is deleted, and if it is then delete it from the database
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.VoiceChannel):
        if await self.check_channel_init(channel.id):
            await self.remove_channel_init(channel.id)
            print(f'Removed {channel.name} from the channelsinit database because it was deleted!')
    
    #make an admin command that will respond ephemeraly with a list of users and channels in the customvoice.db
    @app_commands.command(name='list', description='List all the custom voice channels!')
    @app_commands.checks.has_permissions(administrator=True)
    async def list(self, inter:Interaction):
        await inter.response.defer(thinking=True)
        #Create a list of all the channels in the database
        channels = []
        async with sqlite3.connect('dbs/customvoice.db') as db:
            cursor = await db.execute('SELECT channel_id FROM customvoice')
            result = await cursor.fetchall()
            await cursor.close()
            for i in result:
                channels.append(i[0])
        #Create a list of all the users in the database
        users = []
        async with sqlite3.connect('dbs/customvoice.db') as db:
            cursor = await db.execute('SELECT user_id FROM customvoice')
            result = await cursor.fetchall()
            await cursor.close()
            for i in result:
                users.append(i[0])
        #Create a list of all the channels that are in the database
        channelsInDatabase = []
        for channel in channels:
            channelsInDatabase.append(self.bot.get_channel(channel))
        #Create a list of all the users that are in the database
        usersInDatabase = []
        for user in users:
            usersInDatabase.append(self.bot.get_user(user))
        #Create a string of all the channels and users in the database
        string = ''
        for i in range(len(channelsInDatabase)):
            string += f'Channel: {channelsInDatabase[i].name} | Owner: {usersInDatabase[i].name}\n'
        #Send the string
        await inter.followup.send(string)

    #Create a setup command that can only be used by administrators that will ask them for a category (discord.Category) and the name of the channel (str)
    @app_commands.command(name='setup', description='Setup custom voice channels!')
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, inter:Interaction, category:CategoryChannel, name:str):
        await inter.response.defer(thinking=True)
        #Create the voice channel with the name and put it in the category
        channel = await inter.guild.create_voice_channel(name=name, category=category)
        #Add the channel to the database
        await self.add_channel_init(channel.id)
        await inter.followup.send(f'Created the channel {channel.mention}!')

    #Create a listener that listens to check if a user has joined a channel in the database
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        #Check if the channel is in the database
        if after.channel != None:
            if await self.check_channel_init(after.channel.id):
                #Create a voice channel with the name of the user and drag them into it
                channel = await after.channel.clone(name=member.name)
                await member.move_to(channel)
                #Add the channel to the database
                await self.add_channel(channel.id, member.id)
            else:
                pass
        else:
            pass

        #Check if the user left a channel, and if the channel is in the database
        if before.channel is not None and await self.check_channel(before.channel.id):
            #Check if the channel is empty
            if len(before.channel.members) == 0:
                #Delete the channel
                await before.channel.delete()
                #Remove the channel from the database
                await self.remove_channel(before.channel.id)
                return
            #Check if the user was the owner of the channel, if they were then change the owner to the first person in the channel
            if member.id == await self.get_owner(before.channel.id):
                peopleInChannel = before.channel.members
                #remove the user from the list
                peopleInChannel.remove(member)
                await self.change_owner(before.channel.id, peopleInChannel[0].id)
                #Send a message to the channel saying that the owner has changed 
                await before.channel.send(f'The owner of this channel has changed to {peopleInChannel[0].mention} since the previous owner left the channel.')

    #Create a command that will change the owner of the channel
    @app_commands.command(name='changeowner', description='Change the owner of the channel!')
    async def changeowner(self, inter:Interaction, member:discord.Member):
        await inter.response.defer(thinking=True)
        #Check if the user is in a channel
        if inter.user.voice is None:
            await inter.followup.send('You are not in a channel!')
            return
        #Check if the channel is in the database
        if await self.check_channel(inter.user.voice.channel.id):
            #Check if the user is the owner of the channel
            if inter.user.id == await self.get_owner(inter.user.voice.channel.id):
                #Change the owner of the channel
                await self.change_owner(inter.user.voice.channel.id, member.id)
                await inter.followup.send(f'The owner of this channel has changed to {member.mention}!')
            else:
                await inter.followup.send('You are not the owner of this channel!')
        else:
            await inter.followup.send('This channel is not a custom voice channel!')

    #Create a command that will delete the channel
    @app_commands.command(name='delete', description='Delete the channel!')
    async def delete(self, inter:Interaction):
        await inter.response.defer(thinking=True)
        #Check if the user is in a channel
        if inter.user.voice is None:
            await inter.followup.send('You are not in a channel!')
            return
        #Check if the channel is in the database
        if await self.check_channel(inter.user.voice.channel.id):
            #Check if the user is the owner of the channel
            if inter.user.id == await self.get_owner(inter.user.voice.channel.id):
                #Delete the channel
                await inter.user.voice.channel.delete()
                #Remove the channel from the database
                await self.remove_channel(inter.user.voice.channel.id)
            else:
                await inter.followup.send('You are not the owner of this channel!')
        else:
            await inter.followup.send('This channel is not a custom voice channel!')

    #Create a command that will rename the channel
    @app_commands.command(name='rename', description='Rename the channel!')
    async def rename(self, inter:Interaction, name:str):
        await inter.response.defer(thinking=True)
        #Check if the user is in a channel
        if inter.user.voice is None:
            await inter.followup.send('You are not in a channel!')
            return
        #Check if the channel is in the database
        if await self.check_channel(inter.user.voice.channel.id):
            #Check if the user is the owner of the channel
            if inter.user.id == await self.get_owner(inter.user.voice.channel.id):
                #Rename the channel
                await inter.user.voice.channel.edit(name=name)
                await inter.followup.send(f'The name of this channel has been changed to {name}!')
            else:
                await inter.followup.send('You are not the owner of this channel!')
        else:
            await inter.followup.send('This channel is not a custom voice channel!')

    #Create a command that will change the amount of people that can join the channel
    @app_commands.command(name='userlimit', description='Change the user limit of the channel!')
    async def userlimit(self, inter:Interaction, limit:int):
        await inter.response.defer(thinking=True)
        #Check if the user is in a channel
        if inter.user.voice is None:
            await inter.followup.send('You are not in a channel!')
            return
        #Check if the channel is in the database
        if await self.check_channel(inter.user.voice.channel.id):
            #Check if the user is the owner of the channel
            if inter.user.id == await self.get_owner(inter.user.voice.channel.id):
                #Change the user limit of the channel
                await inter.user.voice.channel.edit(user_limit=limit)
                await inter.followup.send(f'The user limit of this channel has been changed to {limit}!')
            else:
                await inter.followup.send('You are not the owner of this channel!')
        else:
            await inter.followup.send('This channel is not a custom voice channel!')

async def setup(bot:commands.Bot):
    await bot.add_cog(CustomVoice(bot))