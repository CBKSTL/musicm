import discord
from discord.ext import commands
import Music
import asyncio

client = commands.Bot(command_prefix='.', case_insensitive=True, intents = discord.Intents.all())

cogs = [Music]
    
class Help(commands.HelpCommand):
    def get_command_signature(self, command):
        return '%s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title="Help", color=0x47A7FF)
        prefix = self.context.clean_prefix
        embed.description = f"Do `{prefix}help <command>` for more help of the command.\nFor example: `{prefix}help play`\n\nCapitalization of the commands are ignored.\n`[argument]` are optional, `<argument>` are required."
        for cog, commands in mapping.items():
            command_signatures = []

            for c in commands:
                signature = f'prefix`' + self.get_command_signature(c)[1:].replace(" ", '` ', 1)
                command_signatures.append(signature)

            cog_name = getattr(cog, "qualified_name", "No Category")
            embed.add_field(name=cog_name, value="\n".join(command_signatures), inline=False)

        embed.set_footer(text='Renny by ren.xxx', icon_url = 'https://cdn.discordapp.com/avatars/887915339294318633/836a28ee2d030dab64661a8154c0de61.png?size=160')
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(title=self.get_command_signature(command) , color=0x47A7FF)
        if command.description:
            embed.description = command.description
        if alias := command.aliases:
            alias = '`' + "`, `".join(alias) + '`'
            embed.add_field(name="Aliases", value=alias, inline=False)

        embed.set_footer(text='Renny by ren.xxx', icon_url = 'https://cdn.discordapp.com/avatars/887915339294318633/836a28ee2d030dab64661a8154c0de61.png?size=160')
        channel = self.get_destination()
        await channel.send(embed=embed)

client.help_command = Help()

async def main():
    for i in range(len(cogs)):
        await cogs[i].setup(client)

token = 'token'
asyncio.run(main())
client.run(token)
