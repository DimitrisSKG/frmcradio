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

# Συνάρτηση για εγγραφή σε αρχείο και ταυτόχρονη εμφάνιση στην κονσόλα
def log_event(message):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open("logs.txt", "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

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
            log_event(f"ΣΦΑΛΜΑ ΑΝΑΠΑΡΑΓΩΓΗΣ: {e}")
            await asyncio.sleep(10)

@bot.event
async def on_ready():
    log_event(f'Το Bot συνδέθηκε ως {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True)
            bot.loop.create_task(play_audio(vc))
            log_event(f"Επιτυχής σύνδεση στο κανάλι: {channel.name}")
        except Exception as e:
            log_event(f"Αποτυχία σύνδεσης στο κανάλι: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    # Αν το bot αποσυνδεθεί από το κανάλι
    if member.id == bot.user.id:
        if before.channel is not None and after.channel is None:
            log_event(f"ΑΠΟΣΥΝΔΕΣΗ: Το bot εκδιώχθηκε ή αποσυνδέθηκε από το κανάλι '{before.channel.name}'.")
        elif before.channel is not None and after.channel is not None and before.channel != after.channel:
            log_event(f"ΜΕΤΑΚΙΝΗΣΗ: Το bot μετακινήθηκε από το κανάλι '{before.channel.name}' στο '{after.channel.name}'.")

bot.run(TOKEN)