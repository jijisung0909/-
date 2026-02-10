import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# 1. 가짜 웹 서버 설정
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render는 기본적으로 10000번 포트를 사용하거나 
    # 환경 변수로 지정된 포트를 사용합니다.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. 봇 설정 (기존 코드 유지)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# ... 기존의 나머지 코드들 ...

# 3. 실행 부분
if __name__ == "__main__":
    keep_alive()  # 웹 서버 먼저 실행
    bot.run('YOUR_TOKEN_HERE') # 봇 실행

# 🔹 환경 변수에서 불러오기
TOKEN = os.getenv("TOKEN")  # Render 환경 변수에 넣을 것
MEMORY_CHANNEL_NAME = "ai-memory"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

memory = {}  # {질문: 대답}

BAD_WORDS = ["씨발", "병신", "좆", "fuck", "shit"]

def has_bad_word(text):
    return any(bad in text.lower() for bad in BAD_WORDS)

@client.event
async def on_ready():
    print("AI 봇 실행됨")

    # 메모리 채널 찾기
    for guild in client.guilds:
        channel = discord.utils.get(guild.text_channels, name=MEMORY_CHANNEL_NAME)
        if channel:
            async for msg in channel.history(limit=1000):
                if "::" in msg.content:
                    q, a = msg.content.split("::", 1)
                    memory[q] = a

    await tree.sync()
    print("슬래시 명령어 동기화 완료")

# 🔹 계산
@tree.command(name="계산", description="계산을 합니다")
async def calc(interaction: discord.Interaction, 식: str):
    if has_bad_word(식):
        await interaction.response.send_message("욕은 안돼 😐", ephemeral=True)
        return
    try:
        result = eval(식)
        await interaction.response.send_message(f"🧮 결과: **{result}**")
    except:
        await interaction.response.send_message("계산식이 이상해 😅")

# 🔹 학습
@tree.command(name="학습", description="AI에게 기억을 가르칩니다")
async def learn(interaction: discord.Interaction, 질문: str, 대답: str):
    if has_bad_word(질문) or has_bad_word(대답):
        await interaction.response.send_message("욕 포함된 건 학습 못 해 🚫", ephemeral=True)
        return

    memory[질문] = 대답

    channel = discord.utils.get(interaction.guild.text_channels, name=MEMORY_CHANNEL_NAME)
    if channel:
        await channel.send(f"{질문}::{대답}")

    await interaction.response.send_message("🧠 학습 완료!")

# 🔹 AI 대화
@tree.command(name="ai", description="AI와 대화합니다")
async def ai(interaction: discord.Interaction, 메시지: str):
    if has_bad_word(메시지):
        await interaction.response.send_message("욕은 필터링됨 😑")
        return

    if 메시지 in memory:
        await interaction.response.send_message(memory[메시지])
    else:
        await interaction.response.send_message("그건 아직 몰라… `/학습` 시켜줘 🤖")

# 🔹 종료 (관리자만)
@tree.command(name="종료", description="봇을 종료합니다 (관리자 전용)")
async def shutdown(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("관리자만 가능함 ❌", ephemeral=True)
        return

    await interaction.response.send_message("봇 종료 중…")
    await client.close()

client.run(TOKEN)
