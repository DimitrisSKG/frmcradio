import discord
import os
import asyncio
from datetime import datetime

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MP3_URL = os.getenv('MP3_URL')

intents = discord.Intents.default()
# Προσθέτουμε ρητά τα intents
intents.guilds = True
intents.voice_states = True

bot = discord.Client(intents=intents)

async def play_audio(vc):
    while True:
        try:
            if vc.is_connected() and not vc.is_playing():
                options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                source = discord.FFmpegPCMAudio(MP3_URL, **options)
                transformed = discord.PCMVolumeTransformer(source, volume=0.02)
                vc.play(transformed)
            await asyncio.sleep(10)
        except Exception as e:
            print(f"[{datetime.now()}] Σφάλμα: {e}")
            await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            # Προσθήκη timeout στο connect για να αποφύγουμε το σφάλμα 4014/4006
            vc = await channel.connect(timeout=60.0, reconnect=True)
            bot.loop.create_task(play_audio(vc))
        except Exception as e:
            print(f"Αποτυχία σύνδεσης: {e}")

bot.run(TOKEN)
