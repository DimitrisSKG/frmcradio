import discord
import os
import asyncio
import requests
from datetime import datetime

# Ρυθμίσεις
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
FILENAME = "music.mp3"
GH_TOKEN = os.getenv('GH_TOKEN') # Το νέο secret
REPO = "DimitrisSKG/frmcradio" # Το όνομα του repo σου

intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
intents.message_content = True # Απαραίτητο για να διαβάζει εντολές
intents = discord.Intents.default()


bot = discord.Client(intents=intents)

def log_event(message):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{timestamp}] {message}")

async def play_audio(vc):
    while True:
        try:
            if vc.is_connected() and not vc.is_playing():
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

@bot.event
async def on_message(message):
    # Μην απαντάς στον εαυτό σου
    if message.author == bot.user:
        return

    if message.content == "!restart":
        if GH_TOKEN:
            await message.channel.send("🔄 Γίνεται επανεκκίνηση του Workflow στο GitHub...")
            
            # Εντολή στο GitHub API να ξεκινήσει το workflow
            url = f"https://api.github.com/repos/{REPO}/actions/workflows/main.yml/dispatches"
            headers = {
                "Authorization": f"token {GH_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            }
            data = {"ref": "main"}
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 204:
                log_event(f"Το workflow επανεκκινήθηκε από τον χρήστη {message.author}")
                # Το GitHub Actions θα κλείσει αυτό το bot αυτόματα λόγω του concurrency group
            else:
                await message.channel.send(f"❌ Σφάλμα GitHub API: {response.status_code}")
        else:
            await message.channel.send("❌ Δεν έχει ρυθμιστεί το GH_TOKEN στα Secrets!")

bot.run(TOKEN)