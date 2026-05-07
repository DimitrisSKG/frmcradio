import discord
import os
import asyncio
from datetime import datetime

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
# Εδώ γράφεις το όνομα του αρχείου που ανέβασες στο GitHub
FILENAME = "music.mp3" 

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = discord.Client(intents=intents)

def log_event(message):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{timestamp}] {message}")

async def play_audio(vc):
    while True:
        try:
            if vc.is_connected() and not vc.is_playing():
                # Εδώ διαβάζει το τοπικό αρχείο
                source = discord.FFmpegPCMAudio(FILENAME)
                transformed = discord.PCMVolumeTransformer(source, volume=0.02)
                vc.play(transformed)
                log_event("Η αναπαραγωγή ξεκίνησε τοπικά.")
            await asyncio.sleep(5)
        except Exception as e:
            log_event(f"ΣΦΑΛΜΑ: {e}")
            await asyncio.sleep(10)

@bot.event
async def on_ready():
    log_event(f'Το Bot είναι online: {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True)
            bot.loop.create_task(play_audio(vc))
        except Exception as e:
            log_event(f"ΑΠΟΤΥΧΙΑ ΣΥΝΔΕΣΗΣ: {e}")

bot.run(TOKEN)