import discord
import os
import asyncio
from datetime import datetime

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
MP3_URL = os.getenv('MP3_URL')

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True

bot = discord.Client(intents=intents)

def log_event(message):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)

async def play_audio(vc):
    while True:
        try:
            if vc.is_connected() and not vc.is_playing():
                # Βελτιωμένες ρυθμίσεις για σταθερό streaming
                options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                source = discord.FFmpegPCMAudio(MP3_URL, **options)
                # Χαμηλή ένταση (0.02) όπως την όρισες
                transformed = discord.PCMVolumeTransformer(source, volume=0.02)
                
                vc.play(transformed)
                log_event("Η αναπαραγωγή ξεκίνησε.")
            
            await asyncio.sleep(10)
            
        except Exception as e:
            log_event(f"ΣΦΑΛΜΑ ΡΟΗΣ: {e}")
            await asyncio.sleep(10)

@bot.event
async def on_ready():
    log_event(f'Το Bot είναι online: {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            # Αυξημένο timeout για σταθερή πρώτη σύνδεση
            vc = await channel.connect(timeout=60.0, reconnect=True)
            bot.loop.create_task(play_audio(vc))
            log_event(f"Συνδέθηκε στο κανάλι: {channel.name}")
        except Exception as e:
            log_event(f"ΑΠΟΤΥΧΙΑ ΣΥΝΔΕΣΗΣ: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        # Αν το bot αποσυνδεθεί
        if before.channel is not None and after.channel is None:
            log_event(f"ΑΠΟΣΥΝΔΕΣΗ: Το bot βγήκε από το κανάλι '{before.channel.name}'.")

# Αντικατάστησε το bot.run(TOKEN) με αυτό:
while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        log_event(f"Το bot σταμάτησε αναπάντεχα: {e}. Επανακίνηση σε 10 δευτερόλεπτα...")
        asyncio.run(asyncio.sleep(10))