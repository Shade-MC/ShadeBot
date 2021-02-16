# bot.py
import os

import time
import random
import discord
import re
from discord import VoiceState
from discord.ext.commands import Bot
from dotenv import load_dotenv

guildDict = {}

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')

client = Bot(command_prefix='!')

insults = []
with open('insults.txt') as file:
    for line in file:
        insults.append(line)



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        guildDict[guild] = {'scrim': False, 'funnyMeme': False}
        for channel in guild.voice_channels:
            if channel.user_limit == 1:
                guildDict[guild]["lonely"] = channel
                print(f'{channel.name} is desinated as lonely')


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None:
        guild = before.channel.guild
    else:
        guild = after.channel.guild
    lonely = guildDict[guild]['lonely']
    if guildDict[guild]['funnyMeme']:
        #On user leave channel
        if before.channel is not None and after.channel is None:
            if len(before.channel.members) == 1:
                await before.channel.members[0].move_to(lonely)
                print(f'{member.nick} sent to the lonely corner')
        #On user join channel
        elif before.channel is None and after.channel is not None:
            if len(after.channel.members) == 1:
                if len(lonely.members) == 0:
                    await after.channel.members[0].move_to(lonely)
                    print(f'{member.nick} sent to the lonely corner')
                elif len(lonely.members) == 1:
                    await lonely.members[0].move_to(after.channel)
                    print(f'{member.nick} sent to a friend')
        #on user change channel
        elif before.channel is not after.channel:
            if after.channel != lonely:
                if len(after.channel.members) == 1:
                    await after.channel.members[0].move_to(lonely)
                    print(f'{member.nick} sent to the lonely corner')
                elif len(before.channel.members) == 1:
                    await before.channel.members[0].move_to(lonely)
                    print(f'{member.nick} sent to the lonely corner')


@client.command()
async def scrim(ctx):
    if not guildDict[ctx.guild]['scrim']:
        guildDict[ctx.guild]['scrim'] = True

        guildDict[ctx.guild]['scrimLobby'] = await ctx.guild.create_voice_channel('Scrim Lobby')
        await ctx.send("Everyone join the scrim lobby.\n When ready send the start command")



@client.command()
async def start(ctx):
    if not guildDict[ctx.guild]['scrim']:
        await ctx.send("Send the 'scrim' command to set up the lobby first")
        return -1
    guildDict[ctx.guild]['teamA'] = await ctx.guild.create_voice_channel('teamA')
    guildDict[ctx.guild]['teamB'] = await ctx.guild.create_voice_channel('teamB')

    bus = guildDict[ctx.guild]['scrimLobby'].members
    random.shuffle(bus)

    for index, child in enumerate(bus):
        if index % 2:
            await child.move_to(guildDict[ctx.guild]['teamA'])
        else:
            await child.move_to(guildDict[ctx.guild]['teamB'])


@client.command()
async def scramble(ctx):
    if guildDict[ctx.guild]['scrim']:

        roster = guildDict[ctx.guild]['scrimLobby'].members + guildDict[ctx.guild]['teamB'].members + guildDict[ctx.guild]['teamA'].members
        print(roster)
        random.shuffle(roster)
        print(roster)

        if random.choice(range(2)):
            for index, child in enumerate(roster):
                if index % 2:
                    await child.move_to(guildDict[ctx.guild]['teamA'])
                else:
                    await child.move_to(guildDict[ctx.guild]['teamB'])
        else:
            for index, child in enumerate(roster):
                if index % 2:
                    await child.move_to(guildDict[ctx.guild]['teamB'])
                else:
                    await child.move_to(guildDict[ctx.guild]['teamA'])


@client.command()
async def stop(ctx):
    if not guildDict[ctx.guild]['scrim']:
        await ctx.send("This command is to end a scrim,\n you haven't started a scrim,\n "
                       "how could you end what hasn't began")
        return -1

    await guildDict[ctx.guild]['teamA'].delete()
    guildDict[ctx.guild]['teamA'] = None

    await guildDict[ctx.guild]['teamB'].delete()
    guildDict[ctx.guild]['teamB'] = None

    await guildDict[ctx.guild]['scrimLobby'].delete()
    guildDict[ctx.guild]['scrimLobby'] = None

    guildDict[ctx.guild]['scrim'] = False


@client.command()
async def fuckingStop(ctx):
    guildDict[ctx.guild]['funnyMeme'] = False
    await ctx.send("Sorry, i'll stop.")


@client.command()
async def meme(ctx):
    guildDict[ctx.guild]['funnyMeme'] = True
    await ctx.send("You Fool!, you have no idea the power you unleashed")


@client.command()
async def coin(ctx):
    coin = ['heads', 'tails']
    await ctx.send(random.choice(coin))


@client.command()
async def buly(ctx):
    await ctx.send("{} {}".format(ctx.author.mention, "Damn, can't even spell bully right"))


async def bullyMesage(ctx,message):

    if len(ctx.message.mentions) == 0 and len(ctx.message.role_mentions) == 0:
        print("I'm rubber your glue")
        temp = ctx.author.mention
    elif len(ctx.message.mentions) > 0:
        print(ctx.message.mentions)
        temp = ctx.message.mentions[0].mention
    else:
        temp = ctx.message.role_mentions[0].mention


    ident = id_to_int(temp)
    if ident == 141735904606683137:
        print("Master messaged")
        if random.choice(range(2)) == 1:
            message = "Master is the best"
    elif ident == 332635642758692864:
        if random.choice(range(10)) == 5:
            message = "SAD CAT next time!"
    await ctx.send("{} {}".format(temp, message))


def id_to_int(id):
    str = ""
    for i in id:
        if re.match("[0-9]", i):
            str = str + i
    return int(str)


@client.command()
async def BULLY(ctx):
    await bully(ctx)


@client.command()
async def bully(ctx):
    if random.choice(range(100)) == 50:
        await bullyMesage(ctx, " is the coolest")
    else:
        await bullyMesage(ctx, random.choice(insults))


@client.command()
async def gay(ctx):
    await ctx.send(file=discord.File('youGay.png'))


@client.command()
async def catgirl(ctx):
    if random.choice(range(10)) == 9:
        await ctx.send(file=discord.File('cap yeet.jpg'))
    else:
        await ctx.send(file=discord.File('Bella.png'))



client.run(TOKEN)
