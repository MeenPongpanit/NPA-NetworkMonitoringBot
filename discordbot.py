import discord
import os
from dotenv import load_dotenv
import snmpfetch
import visualize
from asyncio import sleep
load_dotenv()

client = discord.Client()
client.target = set()
client.notigroup = set()
client.lookup_interval = 20
client.main_channel = 798761859150774282
client.lookup = True
client.devices = dict()
client.threshold = 100

async def lookup():
    while True:
        if client.lookup:
            for device in client.devices.values():
                device.lookup_octet()
        await sleep(client.lookup_interval)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.get_channel(client.main_channel).send(f'I\'m ready!')
    client.loop.create_task(lookup())

# @client.event
# async def on_typing(channel, user, _):
#     await channel.send(f':eyes:  typing ? {user.mention}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$set_noti_threshold'):
        _, threshold = message.content.split()
        client.threshold = float(threshold)

    if message.content == '$interfacegraph':
        for device in client.devices.values():
            await message.channel.send(f'{device.ip}:')
            for index in device.inoctets:
                visualize.utilize_graph(device.inoctets[index], device.interfaces[index]['speed'], client.lookup_interval, device.interfaces[index]["desc"])
                await message.channel.send(f'>>{device.interfaces[index]["desc"]}:', file=discord.File('utl.jpg'))

    if message.content.startswith('$lookupinterval'):
        _, interval = message.content.split()
        interval = int(interval)
        client.lookup_interval = interval
        for device in client.devices.values():
            device.update_interval()
        await message.channel.send(f'lookup interval is now set. ({interval} seconds)')

    if message.content == '$togglelookup':
        for device in client.devices.values():
            device.update_interval()
        await message.channel.send(f'Lookup: {("OFF", "ON")[client.lookup]}->{("OFF", "ON")[not client.lookup]}')
        client.lookup = not client.lookup

    if message.content == '$help':
        await message.channel.send('```'+open('help.txt', 'r').read()+'```')

    if message.content == '$noticeme':
        client.notigroup.add(message.author)
        await message.channel.send(f'{message.author.mention} was added to notification group.')
    
    if message.content.startswith('$notilist'):
        await message.channel.send(f'Notification group: {", ".join(user.mention for user in client.notigroup)}')

    if message.content.startswith('$hello'):
        await message.channel.send(f'Hi, {message.author.mention}.') 

    if message.content.startswith('$netgraph'):
        await message.channel.send('Here! Your pic.', file=discord.File('ant.jpg'))

    if message.content.startswith('$addtarget'):
        _, target = message.content.split()
        client.target.add(target)
        client.devices[target] = snmpfetch.DEVICE(target)
        await message.channel.send(f'Target is now added. ({client.target})')
    
    if message.content.startswith('$removetarget'):
        _, target = message.content.split()
        client.target.remove(target)
        client.devices.pop(target)
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
