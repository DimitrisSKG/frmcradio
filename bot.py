import discord
import os
import asyncio
import requests
from datetime import datetime

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
FILENAME = "music.mp3"
GH_TOKEN = os.getenv('GH_TOKEN')
REPO = "DimitrisSKG/frmcradio"

# Ενεργοποίηση ΟΛΩΝ των intents για σιγουριά
intents = discord.Intents.all() 
bot = discord.Client(intents=intents)

def log_event(message):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{timestamp}] {message}")

@bot.event
async def on_ready():
    log_event(f'Το Bot είναι online: {bot.user}')
    # Εκτύπωση των intents για επιβεβαίωση στα logs
    log_event(f"Message Content Intent: {bot.intents.message_content}")
    
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            vc = await channel.connect(timeout=60.0, reconnect=True)
            bot.loop.create_task(play_audio(vc))
        except Exception as e:
            log_event(f"ΑΠΟΤΥΧΙΑ ΣΥΝΔΕΣΗΣ: {e}")

async def play_audio(vc):
    while True:
        try:
            if vc.is_connected() and not vc.is_playing():
                source = discord.FFmpegPCMAudio(FILENAME)
                transformed = discord.PCMVolumeTransformer(source, volume=0.02)
                vc.play(transformed)
                log_event("Η αναπαραγωγή ξεκίνησε.")
            await asyncio.sleep(5)
        except Exception as e:
            log_event(f"ΣΦΑΛΜΑ AUDIO: {e}")
            await asyncio.sleep(10)

@bot.event
async def on_message(message):
    # Αυτό ΠΡΕΠΕΙ να εμφανιστεί στα logs του GitHub όποτε γράφεις ΟΤΙΔΗΠΟΤΕ
    log_event(f"Μήνυμα από {message.author}: {message.content}")

    if message.author == bot.user:
        return

    if message.content == "!restart":
        await message.channel.send("🔄 Λήφθηκε εντολή restart...")
        if not GH_TOKEN:
            await message.channel.send("❌ Σφάλμα: Το GH_TOKEN λείπει από τα Secrets!")
            return

        url = f"https://api.github.com/repos/{REPO}/actions/workflows/main.yml/dispatches"
        headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        response = requests.post(url, headers=headers, json={"ref": "main"})
        
        if response.status_code == 204:
            await message.channel.send("✅ Το GitHub ξεκίνησε νέο workflow. Κλείνω...")
        else:
            await message.channel.send(f"❌ Σφάλμα API ({response.status_code}): {response.text}")

bot.run(TOKEN)