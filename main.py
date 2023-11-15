import discord
import traceback
from pathlib import Path
from discord.ext import commands
from discord.message import Message
import json
from discord.ext.commands import CommandNotFound
from dotenv import load_dotenv
import os

load_dotenv()

#Create a basic discord bot
class client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.guild_id = self.config['guild_id']
        super().__init__(intents = intents, command_prefix = '!')

    async def setup_hook(self) -> None:
        for cog in Path('cogs').glob('*.py'):
            if cog.name.startswith('_'):
                continue
            try:
                await self.load_extension(f'cogs.{cog.stem}')
            except Exception:
                traceback.print_exc()
        # self.tree.copy_global_to(guild=discord.Object(id=self.guild_id))
        # await self.tree.sync(guild=discord.Object(id=self.guild_id))
        print(f'Loaded {len(self.tree.get_commands())} commands')

    async def on_ready(self) -> None:
        print(f'Logged in as {self.user}')
        print(f'Invite Link: https://discord.com/oauth2/authorize?client_id={self.user.id}&scope=bot&permissions=8')


bot = client()  
bot.run(os.getenv('TOKEN'))
    
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx):
    synced = await ctx.bot.tree.sync()

    await ctx.send(
        f"Synced {len(synced)} commands."
    )
    return

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    raise error