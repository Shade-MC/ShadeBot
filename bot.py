# bot.py
import os

import discord
from discord import VoiceState
from discord.ext.commands import Bot
from dotenv import load_dotenv

lonely = {}

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')

client = Bot(command_prefix='!')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        for channel in guild.voice_channels:
            if channel.user_limit == 1:
                lonely[guild] = channel
                print(f'{channel.name} is desinated as lonely')

@client.event
async def on_voice_state_update(member,before,after):
    #On user leave channel
    if before.channel is not None and after.channel is None:
        if len(before.channel.members) == 1:
            await before.channel.members[0].move_to(lonely[before.channel.guild])
            print(f'{member.nick} sent to the lonely corner')
    #On user join channel
    elif before.channel is None and after.channel is not None:
        if len(after.channel.members) == 1:
            if len(lonely[after.channel.guild].members) == 0:
                await after.channel.members[0].move_to(lonely[after.channel.guild])
                print(f'{member.nick} sent to the lonely corner')
            elif len(lonely[after.channel.guild].members) == 1:
                await lonely[after.channel.guild].members[0].move_to(after.channel)
                print(f'{member.nick} sent to a friend')

    #on user change channel
    elif before.channel is not after.channel:
        if len(after.channel.members) == 1:
            await after.channel.members[0].move_to(lonely[after.channel.guild])
            print(f'{member.nick} sent to the lonely corner')
        elif len(before.channel.members) == 1:
            await before.channel.members[0].move_to(lonely[before.channel.guild])
            print(f'{member.nick} sent to the lonely corner')

client.run(TOKEN)