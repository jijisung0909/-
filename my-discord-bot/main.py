import discord
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# --- [웹 서버 설정: Render용] ---
app = Flask('')
@app.route('/')
def home():
    return "봇이 살아있습니다!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- [봇 설정] ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user: return
    response = model.generate_content(message.content)
    await message.channel.send(response.text)

# --- [실행] ---
keep_alive() # 웹 서버 시작
client.run(DISCORD_TOKEN)
