import discord
from discord.ext import commands
import Music
import asyncio

client = commands.Bot(command_prefix='.', case_insensitive=True, intents = discord.Intents.all())

cogs = [Music]

async def main():
    for i in range(len(cogs)):
        await cogs[i].setup(client)
    

token = ''
asyncio.run(main())
client.run('token')
