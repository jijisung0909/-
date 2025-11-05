import discord
from discord.ext import commands
import yt_dlp
import os

# 봇 기본 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 반복 재생 상태 저장
repeat = False
current_audio_url = None

@bot.event
async def on_ready():
    print(f"✅ 로그인 완료: {bot.user}")

# 채팅 명령어
@bot.command()
async def 안녕(ctx):
    await ctx.send("안녕하세요! 👋")

# 반복 재생 토글
@bot.command()
async def 반복(ctx):
    global repeat
    repeat = not repeat
    await ctx.send("🔁 반복 재생을 시작합니다!" if repeat else "▶ 반복 재생을 종료합니다!")

# 음악 재생
@bot.command()
async def play(ctx, url=None):
    global current_audio_url
    if url is None:
        await ctx.send("⚠️ 재생할 링크를 입력해주세요! 예: !play <유튜브 링크>")
        return

    if not ctx.author.voice:
        await ctx.send("🎧 먼저 음성채널에 들어가주세요!")
        return

    channel = ctx.author.voice.channel
    vc = ctx.voice_client or await channel.connect()

    # yt_dlp로 스트리밍 URL 추출
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        current_audio_url = info['url']
        title = info['title']

    def after_play(error):
        if error:
            print(f"⚠️ 재생 중 오류 발생: {error}")
        if repeat:
            vc.play(
                discord.FFmpegPCMAudio(
                    current_audio_url,
                    executable="ffmpeg",
                    options='-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
                ),
                after=after_play
            )
        else:
            print("🎵 재생 완료")

    if vc.is_playing():
        vc.stop()

    vc.play(
        discord.FFmpegPCMAudio(
            current_audio_url,
            executable="ffmpeg",
            options='-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        ),
        after=after_play
    )

    await ctx.send(f"🎵 지금 재생 중: {title}")

# 음악 정지 및 채널 나가기
@bot.command()
async def stop(ctx):
    global repeat
    repeat = False
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 음악 정지 및 음성채널에서 나갑니다.")

# 봇 로그아웃/종료
@bot.command()
async def logout(ctx):
    await ctx.send("👋 봇을 로그아웃합니다.")
    await bot.close()

# Render 환경 변수에서 토큰 불러오기
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    print("⚠️ DISCORD_TOKEN 환경 변수가 설정되지 않았습니다.")
else:
    bot.run(DISCORD_TOKEN)

