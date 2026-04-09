# discord-bot-test

Google AI Studio의 Gemini API를 활용한 Python 기반 Discord 자동 응답 봇입니다.  
`#bot-chat` 채널에서 메시지를 입력하면, `char-description.txt`에 설정된 캐릭터로 AI가 자동 응답합니다.

---

## 필요 조건

- Python **3.10** 이상
- **Discord Bot Token** ([Discord Developer Portal](https://discord.com/developers/applications)에서 발급)
- **Google AI Studio Gemini API Key** ([aistudio.google.com](https://aistudio.google.com)에서 발급) — 봇 실행 후 DM으로 설정

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

### 3. 환경변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 만들고 값을 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채워주세요:

```env
DISCORD_TOKEN=your_discord_bot_token_here
OWNER_ID=your_discord_user_id_here
BOT_CHANNEL_NAME=bot-chat
MAX_HISTORY=50
```

> **OWNER_ID 확인 방법:**  
> Discord 설정 → 고급 → **개발자 모드** 활성화 → 본인 프로필 우클릭 → **사용자 ID 복사**

### 4. 캐릭터 설명 수정 (선택 사항)

`char-description.txt` 파일을 열어 AI의 말투와 성격을 원하는 대로 수정하세요.

---

## Discord Developer Portal 설정

봇이 메시지를 읽으려면 아래 설정이 필요합니다.

### Bot 권한 (Permissions)
- `Send Messages` (메시지 전송)
- `Read Message History` (메시지 기록 읽기)
- `View Channels` (채널 보기)

### Privileged Gateway Intents
[Discord Developer Portal](https://discord.com/developers/applications) → 봇 선택 → **Bot** 탭 → **Privileged Gateway Intents** 섹션에서 아래 항목을 **활성화**:

- ✅ `MESSAGE CONTENT INTENT`

---

## 실행 방법

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
봇이 준비되었습니다!
```

---

## Gemini API 키 설정 (DM 명령어)

봇을 실행한 후, **봇에게 DM(다이렉트 메시지)** 으로 아래 명령어를 전송하면 API 키가 설정됩니다.

```
!api YOUR_GEMINI_API_KEY_HERE
```

- `.env`의 `OWNER_ID`에 등록된 소유자만 API 키를 설정할 수 있습니다.
- API 키는 `config.json` 파일에 저장되며, 봇을 재시작해도 유지됩니다.
- `config.json`은 자동으로 생성되므로 직접 만들 필요가 없습니다.
- API 키가 설정되지 않은 상태에서 `#bot-chat`에 메시지가 오면 안내 메시지가 표시됩니다.

---

## 커스터마이징

### 캐릭터 변경

`char-description.txt` 파일을 수정하면 AI의 말투와 성격을 바꿀 수 있습니다.

예시:
```
당신은 츤데레 말투를 가진 AI야. 항상 반말로 대답하고, 솔직한 감정을 잘 표현하지 못해.
```

### 대화 기억 수 조정

`.env` 파일의 `MAX_HISTORY` 값을 변경하면 AI가 기억하는 대화 수를 조정할 수 있습니다.

```env
MAX_HISTORY=100  # 최근 100개의 대화를 기억
```

> ⚠️ 대화 기록은 메모리 기반이므로, 봇을 재시작하면 초기화됩니다.

---

## 파일 구조

```
discord-bot-test/
├── bot.py                  # 메인 봇 코드
├── char-description.txt    # 캐릭터 설명 (수정 가능)
├── config.json             # Gemini API 키 저장 (자동 생성, gitignore 처리됨)
├── .env.example            # 환경변수 예시 파일
├── .env                    # 실제 환경변수 파일 (gitignore 처리됨)
├── .gitignore
├── requirements.txt
└── README.md
```
