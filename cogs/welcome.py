from discord import Interaction, File
from discord import app_commands
from discord.app_commands import AppCommandError
from discord.ext import commands
from discord import PermissionOverwrite
from discord import Permissions
import discord
import discord.ext
import requests
import json
import os
from discord.ext.commands import GroupCog
import io
from discord import CategoryChannel
import aiosqlite3 as sqlite3
from PIL import Image, ImageDraw, ImageFont

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Welcome(GroupCog, name='welcome', description='General Welcome Messages'):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.config = self.bot.config
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        #Check the welcomeChannel field in the config
        if self.config['welcomeChannel'] == 0:
            return
        # Get the channel where you want to send the welcome image
        channel = self.bot.get_channel(self.config['welcomeChannel'])

        # Create an image with PIL that will serve as the welcome image with the user's name, avatar and discriminator
        # Create an image object
        img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))
        # Create a draw object
        d = ImageDraw.Draw(img)
        # Load the default font
        font = ImageFont.load_default()
        # Draw the text
        d.text((10, 10), f'Welcome {member.name}#{member.discriminator}', font=font, fill=(255, 255, 255))
        # Save the image
        img.save('welcome.png')

        # Send the image to the channel
        await channel.send(file=discord.File('welcome.png'))


async def setup(bot):
    await bot.add_cog(Welcome(bot))
