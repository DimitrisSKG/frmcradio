import discord
import os
import asyncio

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MP3_URL = os.getenv('MP3_URL')

intents = discord.Intents.default()
bot = discord.Client(intents=intents)

async def play_audio(vc):
    while True:
        if not vc.is_playing() and vc.is_connected():
            options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            source = discord.FFmpegPCMAudio(MP3_URL, **options)
            transformed = discord.PCMVolumeTransformer(source, volume=0.02)
            vc.play(transformed)
        await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    vc = await channel.connect()
    bot.loop.create_task(play_audio(vc))

bot.run(TOKEN)