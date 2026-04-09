"""
Discord AI 봇 - Gemini API를 활용한 자동 응답 봇
채널: #bot-chat에서 메시지를 감지하고 AI가 자동으로 응답합니다.
"""

import os
import sys
import json
import discord
from collections import deque
from dotenv import load_dotenv
import google.generativeai as genai

# 환경변수 로드
load_dotenv()

# 환경변수에서 설정 읽기
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
BOT_CHANNEL_NAME = os.getenv("BOT_CHANNEL_NAME", "bot-chat")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "50"))

# 봇 소유자의 Discord 사용자 ID (필수)
try:
    OWNER_ID = int(os.getenv("OWNER_ID", ""))
except ValueError:
    OWNER_ID = None

# 필수 환경변수 확인
if not DISCORD_TOKEN:
    print("오류: DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인해주세요.")
    sys.exit(1)

if not OWNER_ID:
    print("오류: OWNER_ID가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    sys.exit(1)

# config.json 파일 경로 (Gemini API 키 저장)
CONFIG_FILE = "config.json"

# 메모리 캐시: config.json 재읽기 횟수 최소화
_config_cache: dict | None = None

def load_config() -> dict:
    """config.json 파일을 읽어 설정을 반환합니다. 캐시를 우선 사용합니다."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            _config_cache = json.load(f)
    else:
        _config_cache = {}
    return _config_cache

def save_config(config: dict) -> None:
    """설정을 config.json 파일에 저장하고 캐시를 갱신합니다."""
    global _config_cache
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    _config_cache = config

def get_gemini_api_key() -> str:
    """저장된 Gemini API 키를 반환합니다. 없으면 빈 문자열을 반환합니다."""
    config = load_config()
    return config.get("gemini_api_key", "")

# 사용할 Gemini 모델명
GEMINI_MODEL = "gemini-2.5-pro-preview-03-25"

# DM에서 API 키를 설정하는 명령어 접두사
API_COMMAND = "!api "

# char-description.txt 파일 읽기 (AI 시스템 프롬프트로 사용)
CHAR_DESCRIPTION_FILE = "char-description.txt"

def load_char_description() -> str:
    """캐릭터 설명 파일을 읽어 반환합니다."""
    if not os.path.exists(CHAR_DESCRIPTION_FILE):
        print(f"오류: '{CHAR_DESCRIPTION_FILE}' 파일을 찾을 수 없습니다.")
        print("캐릭터 설명 파일을 생성하고 봇을 다시 시작해주세요.")
        sys.exit(1)

    with open(CHAR_DESCRIPTION_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print(f"경고: '{CHAR_DESCRIPTION_FILE}' 파일이 비어있습니다.")

    print(f"캐릭터 설명 파일 로드 완료: '{CHAR_DESCRIPTION_FILE}'")
    return content

# 봇 시작 시 캐릭터 설명 로드
system_prompt = load_char_description()

# 채널별 대화 기록 딕셔너리: {channel_id: deque(maxlen=MAX_HISTORY)}
# 각 채널은 독립적인 대화 기록을 유지합니다.
conversation_history: dict[int, deque] = {}

def get_channel_history(channel_id: int) -> deque:
    """채널 ID에 해당하는 대화 기록을 반환합니다. 없으면 새로 생성합니다."""
    if channel_id not in conversation_history:
        conversation_history[channel_id] = deque(maxlen=MAX_HISTORY)
    return conversation_history[channel_id]

def build_gemini_contents(history: deque, new_message: str) -> list:
    """Gemini API에 전달할 대화 내용을 구성합니다."""
    contents = []

    # 기존 대화 기록 추가
    for entry in history:
        contents.append({
            "role": entry["role"],
            "parts": [{"text": entry["content"]}]
        })

    # 새로운 사용자 메시지 추가
    contents.append({
        "role": "user",
        "parts": [{"text": new_message}]
    })

    return contents

async def get_gemini_response(channel_id: int, user_message: str) -> str:
    """Gemini API를 호출하여 응답을 생성합니다."""
    history = get_channel_history(channel_id)

    # 대화 내용 구성
    contents = build_gemini_contents(history, user_message)

    # 저장된 API 키로 Gemini 설정
    api_key = get_gemini_api_key()
    if not api_key:
        return "⚠️ API 키가 설정되지 않았습니다. 봇 관리자에게 문의하세요."
    genai.configure(api_key=api_key)

    # Gemini 모델 초기화 (시스템 프롬프트 포함)
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=system_prompt,
    )

    # API 호출
    response = model.generate_content(contents)

    # 안전 필터 등으로 응답이 차단된 경우 처리
    if not response.candidates or not response.text:
        return "죄송합니다, 해당 요청에 대한 응답을 생성할 수 없습니다."

    assistant_reply = response.text

    # 대화 기록에 사용자 메시지와 AI 응답 추가
    history.append({"role": "user", "content": user_message})
    history.append({"role": "model", "content": assistant_reply})

    return assistant_reply

# Discord 봇 설정
# message_content 인텐트 활성화 필요
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    """봇이 Discord에 연결되었을 때 실행됩니다."""
    print(f"봇 로그인 완료: {bot.user} (ID: {bot.user.id})")
    print(f"응답 채널: #{BOT_CHANNEL_NAME}")
    print(f"최대 대화 기록: {MAX_HISTORY}개")
    print(f"사용 모델: {GEMINI_MODEL}")
    print("봇이 준비되었습니다!")

@bot.event
async def on_message(message: discord.Message):
    """메시지를 수신했을 때 실행됩니다."""
    # 봇 자신의 메시지는 무시
    if message.author == bot.user:
        return

    # DM 채널 처리: 봇 소유자의 !api 명령어 처리
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == OWNER_ID and message.content.startswith(API_COMMAND):
            new_key = message.content.removeprefix(API_COMMAND).strip()
            if new_key:
                config = load_config()
                config["gemini_api_key"] = new_key
                save_config(config)
                await message.channel.send("✅ API 키가 성공적으로 저장되었습니다.")
            else:
                await message.channel.send(f"❌ API 키를 입력해주세요. 예시: `{API_COMMAND}YOUR_API_KEY_HERE`")
        return

    # DM이나 그룹 채널은 name 속성이 없으므로 텍스트 채널인지 확인
    if not isinstance(message.channel, discord.TextChannel):
        return

    # 지정된 채널이 아니면 무시
    if message.channel.name != BOT_CHANNEL_NAME:
        return

    # 빈 메시지는 무시
    if not message.content.strip():
        return

    # API 키가 설정되지 않은 경우 안내 메시지 전송
    if not get_gemini_api_key():
        await message.channel.send("⚠️ API 키가 설정되지 않았습니다. 봇 관리자에게 문의하세요.")
        return

    # 타이핑 인디케이터를 표시하면서 응답 생성
    async with message.channel.typing():
        try:
            reply = await get_gemini_response(message.channel.id, message.content)
            await message.reply(reply, mention_author=False)
        except Exception as e:
            # 오류 발생 시 사용자에게 에러 메시지 전송
            error_msg = f"오류가 발생했습니다: {str(e)}"
            print(f"Gemini API 오류: {e}")
            await message.reply(error_msg, mention_author=False)

# 봇 실행
if __name__ == "__main__":
    print("Discord 봇을 시작합니다...")
    bot.run(DISCORD_TOKEN)
