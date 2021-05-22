import discord
import os
from dotenv import load_dotenv
load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
  print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  if message.content.startswith('!hello'):
    # print('Bello called')
    await message.channel.send(f'Hi, {message.author.mention}.')

  if message.content.startswith('!netgraph'):
    await message.channel.send('Here! Your pic.', file=discord.File('ant.jpg'))

client.run(os.getenv('TOKEN'))
