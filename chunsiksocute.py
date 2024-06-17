import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio

from config import bot_token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"안녕~ 나는 지금 {channel} 서버에 들어왔어!")
    else:
        await ctx.send("엥! 너 지금 음성서버에 없는데? 들어가고나서 나도 초대해줘~")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("나 음성채널에서 쫓겨났당,, 담에 또 만나!")
    else:
        await ctx.send("나 이미 음성채널에 없는데?? 또 내보내지마라..")

@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        await ctx.send("엥! 너 지금 음성서버에 없는데? 들어가고나서 나도 초대해줘~")
        return

    if not ctx.voice_client:
        await join(ctx)
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            URL = info['url']
            title = info['title']

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -loglevel debug',
            'options': '-vn'
        }

        def after_playing(error):
            coro = ctx.send(f"나 이 노래 재생 다 끝냈어!! >> {title}")
            fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            try:
                fut.result()
            except Exception as e:
                print(f"Error sending message: {e}")

        audio_source = discord.FFmpegPCMAudio(URL, **ffmpeg_options)
        ctx.voice_client.play(audio_source, after=after_playing)
        await ctx.send(f'지금 이 노래 재생할게! >> {title}')
    except Exception as e:
        error_message = f"An error occurred: {e}"
        await ctx.send(error_message)
        print(error_message)

@bot.command()
async def test(ctx):
    await ctx.send("김경민바보")
    print("경미닝 바보")

bot.run(bot_token)
