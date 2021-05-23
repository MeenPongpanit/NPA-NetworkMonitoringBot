import discord
import os
from dotenv import load_dotenv
import snmpfetch
load_dotenv()

client = discord.Client()
client.target = set()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.get_channel(798761859150774282).send(f'I\'m ready!')

# @client.event
# async def on_typing(channel, user, _):
#     await channel.send(f':eyes:  typing ? {user.mention}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        # print('Bello called')
        await message.channel.send(f'Hi, {message.author.mention}.') 

    if message.content.startswith('$netgraph'):
        await message.channel.send('Here! Your pic.', file=discord.File('ant.jpg'))

    if message.content.startswith('$addtarget'):
        _, target = message.content.split()
        client.target.add(target)
        await message.channel.send(f'Target is now added. ({client.target})')
    
    if message.content.startswith('$removetarget'):
        _, target = message.content.split()
        client.target.remove(target)
        await message.channel.send(f'Target is now removed. ({client.target})')

    if message.content.startswith('$targetlist'):
        await message.channel.send(f'Targets list: {", ".join(client.target)}')

    if message.content.startswith('$fetchtarget'):
        if message.content.split().__len__() == 4:
            _ ,target, oid, walk_length = message.content.split()
        elif message.content.split().__len__() == 3:
            _ ,target, oid = message.content.split()
            walk_length = 5    
        walk_length = int(walk_length)
        await message.channel.send(f'{target}: value at {oid} is \n{snmpfetch.fetch_oid(target, oid, walk_length)}\n')
       
    elif message.content.startswith('$fetch'):
        # print(message.content)
        reply = ''
        if message.content.split().__len__() == 3:
            _ , oid, walk_length = message.content.split()
        elif message.content.split().__len__() == 2:
            _ , oid = message.content.split()
            walk_length = 5 
        walk_length = int(walk_length)
        if client.target:
            print(f'fetching {oid}') 
            for target in client.target:          
                reply += f'{target}: value at {oid} is \n{snmpfetch.fetchstr_oid(target, oid, walk_length)}\n'
        else:
            reply = 'No target assign yet. Please use !target <target_address>'
        await message.channel.send(reply)
    
    if message.content.startswith('$showinterfaces'):
        reply = '```'
        for target in client.target:
            reply += snmpfetch.fetch_interfaces(target)
        await message.channel.send(reply+'```')

    if message.content.startswith('$bark'):
        await message.channel.send('Wan! Wan!')
    

client.run(os.getenv('TOKEN'))
