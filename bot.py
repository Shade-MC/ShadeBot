# bot.py
import os

import time
import random
import discord
import re
from discord.ext import commands
from discord.ext.commands import Bot
from dotenv import load_dotenv


client = Bot(command_prefix='!')
load_dotenv('.env')

async def load_channel(guild, name):
    if find_channel(guild, name) is None:
        return await guild.create_voice_channel(name)
    else:
        return find_channel(guild, name)


def find_channel(guild, name):
    for channel in guild.channels:
        if channel.name == name:
            return channel
    return None


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        guildDict[guild] = {'funnyMeme': False, 'Scrim Lobby': await load_channel(guild, 'Scrim Lobby')}
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


# @client.command()
# async def scrim(ctx):
#     if not guildDict[ctx.guild]['scrim']:
#         guildDict[ctx.guild]['scrim'] = True
#
#         guildDict[ctx.guild]['scrimLobby'] = await ctx.guild.create_voice_channel('Scrim Lobby')
#         await ctx.send("Everyone join the scrim lobby.\n When ready send the start command")


@client.command(brief=os.getenv('START_BRIEF'), description=os.getenv('START_DESCRIPTION'))
async def start(ctx):
    if guildDict[ctx.guild]['Scrim Lobby'] is None:
        await ctx.send("Some shitty programmer just fuck up. Sorry!\nDon't worry i'll fix it\n"
                       "Feel free to join the 'Scrim Lobby' and try again")
        guildDict[ctx.guild]['Scrim Lobby'] = await load_channel(ctx.guild, 'Scrim Lobby')
        return -1
    guildDict[ctx.guild]['teamA'] = await load_channel(ctx.guild, 'teamA')
    guildDict[ctx.guild]['teamB'] = await load_channel(ctx.guild, 'teamB')

    bus = guildDict[ctx.guild]['Scrim Lobby'].members

    await distribute(bus, [guildDict[ctx.guild]['teamA'], guildDict[ctx.guild]['teamB']])


async def distribute(roster, destinations):
    print([member.nick for member in roster])
    random.shuffle(roster)
    print([member.nick for member in roster])
    print([channel.name for channel in destinations])
    random.shuffle(destinations)
    print([channel.name for channel in destinations])
    for i, cannonFodder in enumerate(roster):
        await cannonFodder.move_to(destinations[i % len(destinations)])


@client.command(brief=os.getenv('chaos_brief'), description=os.getenv('chaos_description'))
async def chaos(ctx):
    if ctx.guild.permissions_for(ctx.author).move_members or ctx.author.id == int(os.getenv('SHADE_ID')):
        channelList = []
        memberList = []
        for channel in ctx.guild.voice_channels:
            channelList.append(channel)
            memberList += channel.members
        await distribute(memberList, channelList)


@client.command(brief=os.getenv('scramble_brief'), description=os.getenv('scramble_description'))
async def scramble(ctx):
    if guildDict[ctx.guild]['teamA'] is None or guildDict[ctx.guild]['teamA'] is None or \
            guildDict[ctx.guild]['Scrim Lobby'] is None:
        await ctx.send("Oops looks like some of the channels for this command are missing,\n "
                       "Don't worry i'll remake them, feel free to try the command again")
        guildDict[ctx.guild]['teamA'] = await load_channel(ctx.guild, 'teamA')
        guildDict[ctx.guild]['teamB'] = await load_channel(ctx.guild, 'teamB')
        guildDict[ctx.guild]['Scrim Lobby'] = await load_channel(ctx.guild, 'Scrim Lobby')
    else:
        roster = guildDict[ctx.guild]['Scrim Lobby'].members + guildDict[ctx.guild]['teamB'].members + guildDict[ctx.guild]['teamA'].members
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


async def abandon_ship(ship, land):
    for crew in ship.members:
        await crew.move_to(land)
    await ship.delete()


@client.command(brief=os.getenv('stop_brief'), description=os.getenv('stop_description'))
async def stop(ctx):
    if guildDict[ctx.guild]['Scrim Lobby'] is None:
        await ctx.send("Ohh No, that wasn't supposed to happen.")
        return -1
    guildDict[ctx.guild]['teamA'] = await load_channel(ctx.guild, 'teamA')
    if guildDict[ctx.guild]['teamA'] is not None:
        await abandon_ship(guildDict[ctx.guild]['teamA'], guildDict[ctx.guild]['Scrim Lobby'])
    guildDict[ctx.guild]['teamB'] = await load_channel(ctx.guild, 'teamB')
    if guildDict[ctx.guild]['teamB'] is not None:
        await abandon_ship(guildDict[ctx.guild]['teamB'], guildDict[ctx.guild]['Scrim Lobby'])


@client.command(brief=os.getenv('fuckingStop_brief'), description=os.getenv('fuckingStop_description'))
async def fuckingStop(ctx):
    guildDict[ctx.guild]['funnyMeme'] = False
    await ctx.send("Sorry, i'll stop.")


@client.command(brief=os.getenv('meme_brief'), description=os.getenv('meme_description'))
async def meme(ctx):
    guildDict[ctx.guild]['funnyMeme'] = True
    await ctx.send("You Fool!, you have no idea the power you unleashed")


@client.command(brief=os.getenv('coin_brief'), description=os.getenv('coin_description'))
async def coin(ctx):
    coin = ['heads', 'tails']
    await ctx.send(random.choice(coin))


@client.command(brief=os.getenv('buly_brief'), description=os.getenv('buly_description'))
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
    if ident == int(os.getenv('SHADE_ID')):
        print("Master messaged")
        if random.choice(range(2)) == 1:
            message = "Master is the best"
    elif ident == int(os.getenv('CAT_ID')):
        if random.choice(range(10)) == 5:
            message = "SAD CAT next time!"
    await ctx.send("{} {}".format(temp, message))


def id_to_int(id):
    str = ""
    for i in id:
        if re.match("[0-9]", i):
            str = str + i
    return int(str)


@client.command(brief=os.getenv('BULLY_BRIEF'), description=os.getenv('BULLY_DESCRIPTION'))
async def BULLY(ctx):
    await bully(ctx)


@client.command(brief=os.getenv('bullie_brief'), description=os.getenv('bullie_description'))
async def bully(ctx):
    if random.choice(range(100)) == 50:
        await bullyMesage(ctx, " is the coolest")
    else:
        await bullyMesage(ctx, random.choice(insults))


@client.command(brief=os.getenv('gay_brief'), description=os.getenv('gay_description'))
async def gay(ctx):
    await ctx.send(file=discord.File('youGay.png'))


@client.command(brief=os.getenv('catgirl_brief'), description=os.getenv('catgirl_description'))
async def catgirl(ctx):
    if random.choice(range(10)) == 9:
        await ctx.send(file=discord.File('cap yeet.jpg'))
    else:
        await ctx.send(file=discord.File('Bella.png'))

if __name__ == "__main__":
    guildDict = {}

    TOKEN = os.getenv('DISCORD_TOKEN')
    insults = []
    with open('insults.txt') as file:
        for line in file:
            insults.append(line)

    client.run(TOKEN)
