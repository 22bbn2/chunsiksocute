import discord
from discord.ext import commands
import yt_dlp as youtube_dl
import asyncio
from collections import deque

from config import bot_token

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

queue = deque()  # 재생 대기 큐

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    if not bot.voice_clients:  # 봇이 현재 음성 채널에 연결되어 있지 않으면 종료
        return
    
    voice_client = bot.voice_clients[0]  # 첫 번째 음성 클라이언트를 가져옴
    channel = voice_client.channel

    # 음성 채널에 더 이상 아무도 없을 때
    if len(channel.members) == 1:  # 봇 자신도 포함되므로 1로 체크
        if voice_client.is_playing():
            voice_client.stop()
        await voice_client.disconnect()
        print("음성 채널에 아무도 없어서 나갔어!")

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

# 재생 대기 큐
async def play_next(ctx):
    if queue:
        URL, title = queue.popleft()
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        def after_playing(error):
            # coro = ctx.send(f"나 이 노래 재생 다 끝냈어!! >> {title}")
            # fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
            # try:
            #     fut.result()
            # except Exception as e:
            #     print(f"Error sending message: {e}")

            asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)

        audio_source = discord.FFmpegPCMAudio(URL, **ffmpeg_options)
        ctx.voice_client.play(audio_source, after=after_playing)
        await ctx.send(f'지금 이 노래 재생할게! >> {title}')
    else:
        # 아무도 없어서 나간 경우에는 메시지 출력안함 그 외의 경우만 출력
        if len(bot.voice_clients[0].channel.members) > 1:
            await ctx.send("재생 대기열에 노래가 없어!")

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

        queue.append((URL, title))
        await ctx.send(f"'{title}'를 재생 대기열에 추가했어!!")

        if not ctx.voice_client.is_playing():
            await play_next(ctx)
    except Exception as e:
        error_message = f"An error occurred: {e}"
        await ctx.send(error_message)
        print(error_message)

@bot.command()
async def test(ctx):
    await ctx.send("김경민바보")
    print("경미닝 바보")

bot.run(bot_token)
