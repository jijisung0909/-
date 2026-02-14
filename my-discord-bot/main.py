import discord
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# --- Render 웹 서버 ---
app = Flask('')
@app.route('/')
def home(): return "I'm Alive!"

def run():
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 8080))

def keep_alive():
    Thread(target=run).start()

# --- 제미나이 설정 ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 디스코드 설정 (기본 인텐트만 사용) ---
intents = discord.Intents.default() 
# intents.message_content = True  <-- 이걸 아예 삭제하거나 주석 처리하세요!
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'봇 로그인 완료: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user: return

    # 봇이 언급되었거나, 개인 메시지(DM)인 경우에만 반응
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # 태그된 부분을 지우고 질문 내용만 추출
        clean_content = message.content.replace(f'<@!{client.user.id}>', '').replace(f'<@{client.user.id}>', '')
        
        try:
            response = model.generate_content(f"공포 게임 전문가로서 대답해줘: {clean_content}")
            await message.channel.send(response.text)
        except Exception as e:
            await message.channel.send(f"오류가 발생했어요: {e}")

keep_alive()
client.run(os.getenv("DISCORD_TOKEN"))
