import discord
from discord.ext import commands
import yt_dlp
import os
import threading
from flask import Flask

# -------------------------
# Flask 웹 서버 설정 (Render용)
# -------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "🎵 Discord Music Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))  # Render 환경 변수 PORT 사용
    app.run(host="0.0.0.0", port=port)

# -------------------------
# Discord 봇 설정
# -------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

repeat = False
current_audio_url = None

@bot.event
async def on_ready():
    print(f"✅ 로그인 완료: {bot.user}")

# 간단 인사
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

    # yt_dlp 스트리밍 URL 추출
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        # 쿠키 사용 시:
        # 'cookiefile': 'cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            current_audio_url = info['url']
            title = info['title']
    except Exception as e:
        await ctx.send(f"⚠️ 재생 중 오류 발생: {e}")
        return

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

# -------------------------
# 메인 실행
# -------------------------
if __name__ == "__main__":
    # Flask 서버를 별 쓰레드에서 실행
    threading.Thread(target=run_flask).start()

    # Discord 봇 실행
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if not DISCORD_TOKEN:
        print("⚠️ DISCORD_TOKEN 환경 변수가 설정되지 않았습니다.")
    else:
        bot.run(DISCORD_TOKEN)
