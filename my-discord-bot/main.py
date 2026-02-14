import discord
import google.generativeai as genai

# 1. 가짜 웹 서버 설정
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

# 1. 설정 (여기에 본인의 키를 넣으세요)
DISCORD_TOKEN = '여기에_디스코드_봇_토큰'
GEMINI_API_KEY = '여기에_제미나이_API_키'

# 2. 제미나이 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'봇 로그인 완료: {client.user}')

@client.event
async def on_message(message):
    # 봇이 쓴 채팅은 무시
    if message.author == client.user:
        return

    # 채팅 채널에 메시지가 올라오면 제미나이에게 물어보기
    try:
        response = model.generate_content(message.content)
        await message.channel.send(response.text)
    except Exception as e:
        await message.channel.send(f"오류 발생: {e}")

client.run(DISCORD_TOKEN)
