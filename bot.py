import discord
from discord.ext import tasks
from roblox import Client as RobloxClient

import os
from dotenv import load_dotenv

load_dotenv()
ROBLOX_TOKEN = os.getenv("ROBLOX_TOKEN")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
robloxClient = RobloxClient(ROBLOX_TOKEN)
requests = robloxClient.requests

@tasks.loop(seconds=60)
async def myloop():
    if client.trackerChannel:
        response = await requests.get("https://friends.roblox.com/v1/users/513778147/friends/online")
        print(response.status_code)
        data = response.json()
        userDictKeys = client.userDict.keys()

        userPresent = False
        for user in data['data']:
            if user['displayName'] == client.username:
                if not client.username in userDictKeys:
                    userPresent = True
                    client.userDict[client.username] = True
                    await client.trackerChannel.send(f"{client.username} has logged onto Roblox")
                    if user['userPresence']['UserPresenceType'] == 'InGame':
                        client.wasInGame = True
                        client.game = user['userPresence']['lastLocation']
                        await client.trackerChannel.send(f"{client.username} is playing {client.game}!")
                    else:
                        continue
                else:
                    userPresent = True
                    if user['userPresence']['UserPresenceType'] == 'InGame' and not client.wasInGame:
                        client.wasInGame = True
                        client.game = user['userPresence']['lastLocation']
                        await client.trackerChannel.send(f"{client.username} is playing {client.game}!")
                    elif user['userPresence']['UserPresenceType'] != 'InGame' and client.wasInGame:
                        client.wasInGame = False
                        await client.trackerChannel.send(f"{client.username} stopped playing {client.game}.")
                        client.game = ''

            else:
                continue
        if (not userPresent) and (client.username in userDictKeys):
            client.wasInGame = False
            client.game = ''
            await client.trackerChannel.send(f"{client.username} has logged off")
            del client.userDict[client.username]
        print(response.json())

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    client.trackerChannel = None
    myloop.start()

@client.event
async def on_message(message):
    if message.author == client.user:
            return

    if message.content.startswith('!track'):
        client.trackerChannel = message.channel
        client.userDict = {}
        client.username = message.content.replace('!track ', '')
        client.username = client.username.replace('!track', '')
        client.username = client.username.replace(' ', '')
        client.wasInGame = False
        client.game = ''
        await client.trackerChannel.send(f'Started tracking {client.username}.')

client.run(DISCORD_TOKEN)