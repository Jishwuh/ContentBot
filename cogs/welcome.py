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
from easy_pil import Editor, load_image_async, Font

@app_commands.guild_only()
@app_commands.default_permissions(administrator=True)
class Welcome(GroupCog, name='welcome', description='General Welcome Messages'):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.config = self.bot.config
        self.welcomeChannel = self.config['welcomeChannel']
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        background = Editor('assets/welcome.png')
        if member.avatar is None:
            profileImage = await load_image_async(member.default_avatar.url)
        else:
            profileImage = await load_image_async(member.avatar.url)
        profile = Editor(profileImage).resize((200, 200)).circle_image()
        poppins = Font.poppins(size=50, variant='bold')

        smallPoppins = Font.poppins(size=30, variant='light')

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline='black', stroke_width=5)

        background.text((400, 260), f'Welcome {member.name}#{member.discriminator} to {member.guild.name}!', font=poppins, align='center')
        background.text((400, 325), f'You are member #{len(member.guild.members)}!', font=smallPoppins, align='center')

        file = File(fp=background.image_bytes, filename='newestMember.png')
        await self.bot.get_channel(self.welcomeChannel).send(file=file)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
