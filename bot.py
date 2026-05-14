import discord
import os
import asyncio
import requests
import sys
from datetime import datetime

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
FILENAME = "music.mp3"
GH_TOKEN = os.getenv('GH_TOKEN')
REPO = "DimitrisSKG/frmcradio"

intents = discord.Intents.all()
bot = discord.Client(intents=intents)

def log_event(message):
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"[{timestamp}] {message}")

@bot.event
async def on_ready():
    log_event(f'Το Bot συνδέθηκε στο Discord: {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    
    if channel:
        voice_states = channel.voice_states
        if bot.user.id in voice_states:
            log_event("⚠️ Το bot παίζει ήδη. Κλείνω τη νέα προσπάθεια.")
            await bot.close()
            sys.exit(0)
            
        try:
            log_event(f"Προσπάθεια σύνδεσης στο κανάλι: {channel.name}")
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
async def on_voice_state_update(member, before, after):
    # Ελέγχουμε αν η αλλαγή αφορά το ίδιο το Bot
    if member.id == bot.user.id:
        # ΣΕΝΑΡΙΟ 1: Κάποιος έκανε KICK το bot (βγήκε τελείως από τη φωνή)
        if before.channel is not None and after.channel is None:
            log_event(f"🚨 Το bot απομακρύνθηκε από το κανάλι φωνής σκόπιμα. Κλείνω το workflow.")
            await bot.close()
            # Επιστρέφουμε exit code 1. Αυτό θα κάνει το GitHub Actions να βγάλει ΚΟΚΚΙΝΟ σφάλμα 
            # και θα ΣΤΑΜΑΤΗΣΕΙ να προσπαθεί κάθε 5 λεπτά, μέχρι να πατήσεις εσύ !restart.
            sys.exit(1) 
            
        # ΣΕΝΑΡΙΟ 2: Κάποιος ΜΕΤΑΚΙΝΗΣΕ το bot σε άλλο κανάλι
        elif before.channel is not None and after.channel is not None and before.channel.id != after.channel.id:
            if after.channel.id != CHANNEL_ID:
                log_event(f"🚨 Το bot μετακινήθηκε σε λάθος κανάλι ({after.channel.name}). Κλείνω το workflow.")
                await bot.close()
                sys.exit(1)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content == "!restart":
        await message.channel.send("🔄 Λήφθηκε εντολή εναρξης/restart. Ξεκινάω το ραδιόφωνο...")
        if not GH_TOKEN:
            await message.channel.send("❌ Σφάλμα: Το GH_TOKEN λείπει!")
            return

        url = f"https://api.github.com/repos/{REPO}/actions/workflows/main.yml/dispatches"
        headers = {"Authorization": f"token {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
        response = requests.post(url, headers=headers, json={"ref": "main"})
        
        if response.status_code == 204:
            await bot.close()
            sys.exit(0)
        else:
            await message.channel.send(f"❌ Σφάλμα API ({response.status_code})")

bot.run(TOKEN)