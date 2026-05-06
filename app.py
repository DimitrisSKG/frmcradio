import discord
from discord.ext import commands
import asyncio

TOKEN = 'MTUwMTU2ODYxMTUzMjI3NTcxMg.GUaMX3.yXtTuoDfUvaahbVmFxe3SC74FOi23RD7Ua5jXg'
VOICE_CHANNEL_ID = 1498020493377409114  # Βάλε το ID του καναλιού σου
MP3_URL = 'https://cdn.discordapp.com/attachments/563364086046523393/1501569952748929175/Free_Riders_official.mp3?ex=69fc8d7e&is=69fb3bfe&hm=337eff604af55f22c62f1565674376a3b67ec40298f94b71802df74cb17c6cd9&'

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def play_audio(vc):
    while True:
        try:
            if not vc.is_playing() and vc.is_connected():
                options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                
                # 1. Δημιουργία της πηγής
                source = discord.FFmpegPCMAudio(MP3_URL, **options)
                
                # 2. Μετατροπή σε πηγή με έλεγχο έντασης
                # Το volume=0.5 σημαίνει 50% ένταση. 
                # Μπορείς να το βάλεις από 0.1 έως 2.0 (αν και πάνω από 1.0 μπορεί να παραμορφώνει)
                transformed_source = discord.PCMVolumeTransformer(source, volume=0.02)
                
                # 3. Αναπαραγωγή της μετασχηματισμένης πηγής
                vc.play(transformed_source)
                print(f"Ξεκίνησε η αναπαραγωγή με ένταση {transformed_source.volume*100}%")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Σφάλμα κατά την αναπαραγωγή: {e}")
            await asyncio.sleep(10)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel:
        vc = await channel.connect()
        bot.loop.create_task(play_audio(vc))

bot.run(TOKEN)