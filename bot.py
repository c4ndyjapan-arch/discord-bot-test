"""
Discord AI Bot - Gemini API 자동 응답 봇

기능:
- #bot-chat 채널에서 봇 제외 모든 메시지에 자동 응답 (reply 형태)
- 봇 소유자가 DM으로 !api <키> 명령어로 Gemini API 키 설정
- char-description.txt를 AI 시스템 프롬프트로 사용
- 채널별 최근 N개 대화 기록 유지
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

# 설정값 로드
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID_STR = os.getenv("OWNER_ID", "0")
BOT_CHANNEL_NAME = os.getenv("BOT_CHANNEL_NAME", "bot-chat")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "50"))
GEMINI_MODEL = "gemini-2.5-pro-preview-03-25"
CHAR_DESCRIPTION_FILE = "char-description.txt"
CONFIG_FILE = "config.json"

# 필수 환경변수 확인
if not DISCORD_TOKEN:
    print("오류: DISCORD_TOKEN이 설정되지 않았습니다. .env 파일을 확인해주세요.")
    sys.exit(1)

try:
    OWNER_ID = int(OWNER_ID_STR)
    if OWNER_ID == 0:
        raise ValueError
except ValueError:
    print("오류: OWNER_ID가 올바르게 설정되지 않았습니다. .env 파일을 확인해주세요.")
    sys.exit(1)


def load_char_description() -> str:
    """char-description.txt 파일을 읽어 시스템 프롬프트로 반환합니다."""
    if not os.path.exists(CHAR_DESCRIPTION_FILE):
        print(f"오류: '{CHAR_DESCRIPTION_FILE}' 파일을 찾을 수 없습니다.")
        print("char-description.txt 파일을 생성하고 봇을 다시 시작해주세요.")
        sys.exit(1)
    with open(CHAR_DESCRIPTION_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
    print(f"캐릭터 설명 파일 로드 완료: '{CHAR_DESCRIPTION_FILE}'")
    return content


def load_config() -> dict:
    """config.json을 읽어 반환합니다. 파일이 없으면 기본값을 반환합니다."""
    if not os.path.exists(CONFIG_FILE):
        return {"gemini_api_key": ""}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    """config.json에 설정을 저장합니다."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    # 인메모리 캐시 갱신
    _config_cache.update(config)
    _apply_api_key()


def _apply_api_key():
    """캐시된 API 키로 Gemini를 설정합니다."""
    api_key = _config_cache.get("gemini_api_key", "").strip()
    if api_key:
        genai.configure(api_key=api_key)


# 봇 시작 시 캐릭터 설명 로드
system_prompt = load_char_description()

# 설정 인메모리 캐시 (파일 반복 읽기 방지)
_config_cache: dict = load_config()
_apply_api_key()

# 채널별 대화 기록: {channel_id: deque(maxlen=MAX_HISTORY)}
conversation_history: dict[int, deque] = {}


def get_channel_history(channel_id: int) -> deque:
    """채널 ID에 해당하는 대화 기록 deque를 반환합니다."""
    if channel_id not in conversation_history:
        conversation_history[channel_id] = deque(maxlen=MAX_HISTORY)
    return conversation_history[channel_id]


def build_gemini_contents(history: deque, new_message: str) -> list:
    """Gemini API에 전달할 대화 contents 리스트를 구성합니다."""
    contents = []
    for entry in history:
        contents.append({
            "role": entry["role"],
            "parts": [{"text": entry["content"]}]
        })
    contents.append({
        "role": "user",
        "parts": [{"text": new_message}]
    })
    return contents


async def get_gemini_response(channel_id: int, user_message: str) -> str | None:
    """
    Gemini API를 호출하여 응답을 생성합니다.
    API 키가 설정되지 않은 경우 None을 반환합니다.
    """
    api_key = _config_cache.get("gemini_api_key", "").strip()
    if not api_key:
        return None

    # 대화 기록 및 contents 구성
    history = get_channel_history(channel_id)
    contents = build_gemini_contents(history, user_message)

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

    # 대화 기록 업데이트
    history.append({"role": "user", "content": user_message})
    history.append({"role": "model", "content": assistant_reply})

    return assistant_reply


# Discord 인텐트 설정 (message_content 필수)
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)


@bot.event
async def on_ready():
    """봇이 Discord에 연결되면 실행됩니다."""
    print(f"봇 로그인 완료: {bot.user} (ID: {bot.user.id})")
    print(f"응답 채널: #{BOT_CHANNEL_NAME}")
    print(f"최대 대화 기록: {MAX_HISTORY}개")
    print(f"사용 모델: {GEMINI_MODEL}")
    if _config_cache.get("gemini_api_key"):
        print("Gemini API 키: 설정됨 ✅")
    else:
        print("Gemini API 키: 미설정 ⚠️")
        print("  → 봇에게 DM으로 '!api YOUR_GEMINI_API_KEY'를 전송해주세요.")
    print("봇이 준비되었습니다!")


@bot.event
async def on_message(message: discord.Message):
    """메시지 수신 시 실행됩니다."""
    # 봇 자신의 메시지 무시
    if message.author == bot.user:
        return

    # DM 채널 처리: 소유자의 !api 명령어만 허용
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == OWNER_ID:
            if message.content.startswith("!api "):
                new_key = message.content[5:].strip()
                if new_key:
                    config = _config_cache.copy()
                    config["gemini_api_key"] = new_key
                    save_config(config)
                    await message.reply(
                        "✅ Gemini API 키가 성공적으로 저장되었습니다.",
                        mention_author=False
                    )
                    print("Gemini API 키가 업데이트되었습니다.")
                else:
                    await message.reply(
                        "⚠️ API 키를 입력해주세요.\n사용법: `!api YOUR_GEMINI_API_KEY`",
                        mention_author=False
                    )
        return  # DM은 !api 명령어 외 모두 무시

    # 텍스트 채널만 처리 (DM, 그룹채널 등 제외)
    if not isinstance(message.channel, discord.TextChannel):
        return

    # 지정된 채널(#bot-chat)만 처리
    if message.channel.name != BOT_CHANNEL_NAME:
        return

    # 빈 메시지 무시
    if not message.content.strip():
        return

    # 타이핑 인디케이터를 표시하면서 AI 응답 생성
    async with message.channel.typing():
        try:
            reply = await get_gemini_response(message.channel.id, message.content)
            if reply is None:
                # API 키 미설정 안내
                await message.reply(
                    "⚠️ Gemini API 키가 설정되지 않았습니다. 봇 관리자에게 문의하세요.",
                    mention_author=False
                )
            else:
                await message.reply(reply, mention_author=False)
        except Exception as e:
            print(f"오류 발생: {e}")
            await message.reply(
                f"오류가 발생했습니다: {str(e)}",
                mention_author=False
            )


if __name__ == "__main__":
    print("Discord 봇을 시작합니다...")
    bot.run(DISCORD_TOKEN)
