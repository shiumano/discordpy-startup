import discord, importlib, os
import botsystem


token = os.environ['DISCORD_BOT_TOKEN']

client = discord.Client()
botsystem.set_client()

@client.event
async def on_ready():
    print(f'{client.user}としてログインしました')

@client.event
async def on_message(message):
    if message.content == '@reload':
        try:
            importlib.reload(botsystem)
            await message.channel.send('Reloaded.')
        except Exception as e:
            await message.channel.send(f'Not reloaded : {e}')
    await botsystem.commands(message)
client.run(token)
