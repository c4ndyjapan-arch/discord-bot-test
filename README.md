# discord-bot-test

Google AI Studio의 Gemini API를 활용한 Python 기반 Discord 자동 응답 봇입니다.  
`#bot-chat` 채널에서 메시지를 입력하면, `char-description.txt`에 설정된 캐릭터로 AI가 자동 응답합니다.

---

## 기능

- `#bot-chat` 채널에서 봇을 제외한 모든 메시지에 자동으로 reply
- 답장 형태(`message.reply`)로 응답 — 어떤 메시지에 대한 답변인지 명확히 표시
- 응답 생성 중 타이핑 인디케이터 표시
- 채널별로 최근 대화 기록을 유지 (기본 50개)
- 봇 소유자가 DM으로 `!api <키>` 명령어를 전송해 Gemini API 키를 설정
- API 키는 `config.json`에 저장되어 봇 재시작 후에도 유지

---

## 필요 조건

- Python **3.10** 이상
- **Discord Bot Token** ([Discord Developer Portal](https://discord.com/developers/applications)에서 발급)
- **Google AI Studio Gemini API Key** ([aistudio.google.com](https://aistudio.google.com)에서 발급)

---

## 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/c4ndyjapan-arch/discord-bot-test.git
cd discord-bot-test
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

---

## Discord Developer Portal 설정

봇이 메시지를 읽고 응답하려면 아래 설정이 필요합니다.

### Privileged Gateway Intents 활성화

[Discord Developer Portal](https://discord.com/developers/applications) → 봇 선택 → **Bot** 탭 → **Privileged Gateway Intents** 섹션에서 아래 항목을 **모두 ON**:

- ✅ `Presence Intent`
- ✅ `Server Members Intent`
- ✅ `Message Content Intent` ← **필수!**

### 봇 초대 URL 생성

1. 왼쪽 메뉴 **"OAuth2"** → **"URL Generator"** 클릭
2. **Scopes**: `bot` 체크
3. **Bot Permissions**: `Send Messages`, `Read Messages/View Channels`, `Read Message History` 체크
4. 생성된 URL로 봇을 내 Discord 서버에 초대

---

## .env 파일 설정

`.env.example` 파일을 복사하여 `.env` 파일을 만든 뒤 실제 값을 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
DISCORD_TOKEN=실제_봇_토큰_입력
OWNER_ID=실제_Discord_유저_ID_입력
BOT_CHANNEL_NAME=bot-chat
MAX_HISTORY=50
```

> **OWNER_ID 확인 방법:**  
> Discord 설정 → **고급** → **개발자 모드** ON → 본인 프로필 우클릭 → **"사용자 ID 복사"**

`.env` 파일은 `.gitignore`에 등록되어 있어 GitHub에 업로드되지 않습니다. ✅

---

## char-description.txt 수정 방법

`char-description.txt` 파일을 열어 AI의 말투, 성격, 설정을 원하는 대로 수정하세요.

예시:

```
당신은 츤데레 말투를 가진 AI야. 항상 반말로 대답하고, 솔직한 감정을 잘 표현하지 못해.
```

---

## 봇 실행

```bash
python bot.py
```

정상 실행 시 아래와 같은 메시지가 출력됩니다:

```
캐릭터 설명 파일 로드 완료: 'char-description.txt'
Discord 봇을 시작합니다...
봇 로그인 완료: BotName#1234 (ID: 123456789)
응답 채널: #bot-chat
최대 대화 기록: 50개
사용 모델: gemini-2.5-pro-preview-03-25
Gemini API 키: 미설정 ⚠️  봇에게 DM으로 '!api YOUR_KEY'를 전송해주세요.
봇이 준비되었습니다!
```

---

## Gemini API 키 등록 방법

봇 실행 후, API 키를 DM으로 등록해야 `#bot-chat` 채널에서 응답이 가능합니다.

1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급
2. Discord에서 **봇에게 DM**으로 아래 명령어 전송:
   ```
   !api YOUR_GEMINI_API_KEY
   ```
3. 봇이 "✅ API 키가 성공적으로 저장되었습니다." 응답하면 완료!

> API 키는 `config.json`에 저장되어 봇을 재시작해도 유지됩니다.  
> `config.json`은 `.gitignore`에 등록되어 있어 GitHub에 업로드되지 않습니다. ✅

---

## 커스터마이징

### 캐릭터 변경

`char-description.txt` 파일을 수정하면 AI의 말투와 성격을 바꿀 수 있습니다.

### 대화 기억 수 조정

`.env` 파일의 `MAX_HISTORY` 값을 변경하면 AI가 기억하는 대화 수를 조정할 수 있습니다.

```env
MAX_HISTORY=100  # 최근 100개의 대화를 기억
```

> ⚠️ 대화 기록은 메모리 기반이므로, 봇을 재시작하면 초기화됩니다.

### 응답 채널 변경

`.env` 파일의 `BOT_CHANNEL_NAME` 값을 변경하면 봇이 응답할 채널을 바꿀 수 있습니다.

```env
BOT_CHANNEL_NAME=ai-chat
```

---

## 파일 구조

```
discord-bot-test/
├── bot.py                  # 메인 봇 코드
├── char-description.txt    # 캐릭터 설명 (수정 가능)
├── .env.example            # 환경변수 예시 파일
├── .env                    # 실제 환경변수 파일 (gitignore 처리됨)
├── config.json             # Gemini API 키 저장 파일 (자동 생성, gitignore 처리됨)
├── .gitignore
├── requirements.txt
└── README.md
```
