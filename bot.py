import asyncio, json, time, threading, os
from datetime import datetime
import discord
from discord.ext import commands
from discord.ui import *
from discord.ext.commands.core import has_permissions
from discord import *

import TOKEN

def get_prefix(client,message):
    return data["prefix"][str(message.guild.id)]

class CustomHelpCommand(commands.HelpCommand):

    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed=discord.Embed(title="__**:information_source: Help Menü :information_source:**__",description="*Willkommen, dies ist das Help Menü da muss noch jemandamal den text abändern bruh.*\n:man_technologist_tone2: | Credits: <@!650664693274247208> \n\n",colour=discord.Colour.dark_theme())
        c=0
        for cog in reversed(mapping):
            b=""
            for a in mapping[cog]:
                b=b+", `"+get_prefix(client,self.get_destination())+a.name+"`"
            if not "help" in b:
                if not cog.qualified_name=="TeamOnly":
                    c+=1
                    embed.add_field(name=cog.qualified_name,value=b[1:])
        for a in range(3-(c%3)):
            embed.add_field(name="` `",value="` `")
        b=""
        for command in tree.get_commands():
            command:discord.app_commands.Command
            b=b+", `/"+command.name+"`"
        if b=="":
            b="No Slash Commands"
        emoji=client.get_emoji(TOKEN.slash_emoji)
        embed.add_field(name=f"{emoji} __Slash Commands__ {emoji}",value=b[1:])
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        await self.get_destination().send(f"{cog.qualified_name}: {[command.name for command in cog.get_commands()]}")

    async def send_group_help(self, group):
        await self.get_destination().send(f"{group.name}: {[command.name for index,command in enumerate(group.commands)]}")

    async def send_command_help(self, command):
        aliases=""
        for a in command.aliases:
            aliases=aliases+", "+a
        embed=discord.Embed(title=command.name.capitalize(),description=command.help,colour=discord.Colour.dark_theme())
        embed.add_field(name="Usage",value=command.usage)
        embed.set_footer(text=aliases)
        await self.get_destination().send(embed=embed)

intents=discord.Intents.all()
token=TOKEN.TOKEN
bot=commands.Bot(command_prefix=get_prefix,intents=intents,help_command=CustomHelpCommand(),case_insensitive=True)
client=discord.Client(intents=intents)
tree=app_commands.CommandTree(client)
colors=TOKEN.colors

# on_script_run

if os.path.isfile("bot_data.json"):
    with open('bot_data.json', encoding='utf-8') as f:
        data = json.load(f)
else:
    data = {}
    with open('bot_data.json', 'w') as f:
        json.dump(data, f, indent=4)

data_attributes=["prefix"]
for data_attribute in data_attributes:
    if not data_attribute in data:data[data_attribute]={}

# helping_functions

async def send_embed(ctx,title=None,description=None,image_url=None,url=None,color=discord.Colour.dark_theme(),message=None):
    embed=discord.Embed(title=title,description=description,color=color,timestamp=datetime.now())
    if image_url !=None:embed.set_image(url=image_url)
    if url!=None: embed.url=url
    if message==None:
        return await ctx.send(embed=embed)
    else:
        return await message.edit(content="",embed=embed)

# on_ready

@client.event
async def on_ready():
    print(f"Slash Client als {client.user}")
    print("\rSynchronizing Commands...",end="")
    time.sleep(1)
    await tree.sync()
    for guild in TOKEN.AdminGuilds:
        await tree.sync(guild=guild)
    print("\rCommands Synchronized!")

@bot.event
async def on_ready():
    if not client.is_ready():
        loop = asyncio.get_event_loop()
        loop.create_task(client.start(token))
    print('\rCommand Client online als {}'.format(bot.user))

# Events

@bot.event
async def on_message(message:discord.Message):
    if message.author.bot:
        return
    try:
        if message.mentions[0]==client.user:
            pre=data["prefix"][str(message.guild.id)]
            return await message.channel.send(embed=discord.Embed(title=f"Mein Prefix ist: {pre}",color=colors[1]))
    except KeyError:
        data["prefix"][str(message.guild.id)]="t."
        return await message.channel.send(embed=discord.Embed(title="Es gab ein Problem versuche es noch einmal.",color=colors[2]))
    except IndexError:
        pass
    await bot.process_commands(message)

@client.event
async def on_guild_join(guild:discord.Guild):
    print(guild.name)
    await tree.sync()
    data["prefix"][str(guild.id)]="t."

# Error-Events

@client.event
async def on_command_error(ctx, error):
    if len(error.args) == 1:
        error = str(error.args[0])
    else:
        err=""
        for a in error.args:
            err=err+"\n\n"+a
        error=err
    return await send_embed(ctx,"Error!",str(error),color=colors[2])

@tree.error
async def on_error(interaction:discord.Interaction, error:discord.app_commands.errors.CommandInvokeError):
    if isinstance(error,discord.app_commands.errors.CommandNotFound):
        return
    if len(error.args) == 1:
        error = str(error.args[0])
    else:
        err=""
        for a in error.args:
            err=err+"\n\n"+a
        error=err
    embed=discord.Embed(title="Error!",description=str(error),timestamp=datetime.now(),color=colors[2])
    try:
        await interaction.response.send_message(embed=embed,ephemeral=True)
    except:
        await interaction.channel.send(embed=embed)

## Cogs ## Cogs ## Cogs ## Cogs ## Cogs ## Cogs ## Cogs ## Cogs ## Cogs ##

class prefix_view(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Reset Prefix",custom_id="reset_prefix")
    async def reset_prefix(self,interaction:Interaction,button:Button):
        if button.custom_id == "reset_prefix" and interaction.user.guild_permissions.manage_guild:
            data["prefix"][str(interaction.guild_id)]="t."
            embed=discord.Embed(title="Das Prefix wurde auf \"t.\" zurückgesetzt",color=colors[1])
            await interaction.message.edit(embed=embed,view=None)

class Bot(commands.Cog,name="__Bot__"):
    @commands.command(usage="prefix <Text>")
    async def prefix(self,ctx:commands.Context,neues_prefix=None):
        """Ändere das Prefix des Bots für diesen Server."""
        if neues_prefix == None:
            return await ctx.send(embed=discord.Embed(title=f"Das aktuelle Prefix ist: {data['prefix'][str(ctx.guild.id)]}",color=colors[1]),view=prefix_view())
        else:
            if ctx.author.guild_permissions.manage_guild:
                data['prefix'][str(ctx.guild.id)]=neues_prefix
                return await ctx.send(embed=discord.Embed(title=f"Das neue Prefix ist: {data['prefix'][str(ctx.guild.id)]}",color=colors[0]),view=prefix_view())
            else:
                return await ctx.send(embed=discord.Embed(title=f"Du hast leider keine Rechte das Prefix zu änder, du benötigst die Serververwaltungsrechte.",color=colors[2]))

## Slash Commands ## Slash Commands ## Slash Commands ## Slash Commands ##

@tree.command(name="help",description="Bot-Hilfe")
async def _help(interaction:discord.Interaction):
    embed=discord.Embed(title="__**:information_source: Help Menü :information_source:**__",description="*Willkommen, dies ist das CoolDudE Help Menü.*\n:man_technologist_tone2: | Developer: <@!650664693274247208> \nFalls du Hilfe benötigst schreibe ihn an, natürlich auch bei anderen Anliegen.\n\n",colour=discord.Colour.dark_theme())
    c=0
    mapping=bot.cogs
    for cog in reversed(mapping):
        b=""
        for a in mapping[cog].get_commands():
            b=b+", `"+get_prefix(bot,interaction)+a.name+"`"
        if not "help" in b:
            if not cog=="TeamOnly":
                c+=1
                embed.add_field(name=cog,value=b[1:])
    for a in range(3-(c%3)):
        embed.add_field(name="` `",value="` `")
    b=""
    for command in tree.get_commands():
        command:discord.app_commands.Command
        b=b+", `/"+command.name+"`"
    if b=="":
        b="No Slash Commands"
    emoji=client.get_emoji(TOKEN.slash_emoji)
    embed.add_field(name=f"{emoji} __Slash Commands__ {emoji}",value=b[1:])
    await interaction.response.send_message(embed=embed,ephemeral=True)

## Slash Command-Zusätze ## Slash Command-Zusätze ## Slash Command-Zusätze ##



# Loops

def save_data():
    global data
    while True:
        time.sleep(3)
        with open("bot_data.json","w") as f:
            json.dump(data,f,indent=4)

# Start

async def load_cogs(cogs):
    for cog in cogs:
        try:
            await client.add_cog(cog())
        except Exception as e:
            print(e)

async def main():
    async with client:
        cogs=[]
        await load_cogs(cogs)
        threading.Thread(target=save_data).start()
        await bot.start(token)

asyncio.run(main())

# Made by Discord Development
