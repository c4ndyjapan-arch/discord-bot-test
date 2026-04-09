# discord-bot-test

Google AI Studio의 Gemini API를 활용한 Python 기반 Discord 자동 응답 봇입니다.  
`#bot-chat` 채널에서 메시지를 입력하면, `char-description.txt`에 설정된 캐릭터로 AI가 자동 응답합니다.  
Gemini API 키는 봇에게 DM으로 등록하므로 `.env` 파일에 포함되지 않습니다.

---

## 필요 조건

- Python **3.10** 이상
- **Discord Bot Token** ([Discord Developer Portal](https://discord.com/developers/applications)에서 발급)
- **Google AI Studio Gemini API Key** ([aistudio.google.com](https://aistudio.google.com/app/apikey)에서 발급)
- 봇 소유자의 **Discord 유저 ID** (OWNER_ID)

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

봇이 메시지를 읽으려면 아래 설정이 필요합니다.

### Privileged Gateway Intents

[Discord Developer Portal](https://discord.com/developers/applications) → 봇 애플리케이션 선택 → **Bot** 탭 → **Privileged Gateway Intents** 섹션에서 아래 항목을 **모두 활성화**:

- ✅ `PRESENCE INTENT`
- ✅ `SERVER MEMBERS INTENT`
- ✅ `MESSAGE CONTENT INTENT`

### Bot 권한 (OAuth2 초대 시)

- `Send Messages` (메시지 전송)
- `Read Message History` (메시지 기록 읽기)
- `View Channels` (채널 보기)

---

## .env 파일 설정

`.env.example` 파일을 복사하여 `.env` 파일을 만들고 값을 입력합니다.

```bash
cp .env.example .env
```

`.env` 파일을 열어 아래 값을 채워주세요:

```env
DISCORD_TOKEN=여기에_봇_토큰_입력
OWNER_ID=여기에_내_Discord_유저ID_입력
BOT_CHANNEL_NAME=bot-chat
MAX_HISTORY=50
```

> **OWNER_ID 확인 방법:**  
> Discord 설정 → **고급** → **개발자 모드** ON → 본인 프로필 우클릭 → **"사용자 ID 복사"**

---

## char-description.txt 수정

`char-description.txt` 파일을 열어 AI의 말투와 성격을 원하는 대로 수정하세요.

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
봇 로그인 완료: BotName#0000 (ID: 123456789)
응답 채널: #bot-chat
최대 대화 기록: 50개
사용 모델: gemini-2.5-pro-preview-03-25
Gemini API 키: 미설정 ⚠️  봇에게 DM으로 '!api YOUR_KEY'를 전송해주세요.
봇이 준비되었습니다!
```

---

## Gemini API 키 DM 등록

봇이 실행된 후, **봇 소유자(OWNER_ID)** 만 API 키를 등록할 수 있습니다.

### 1. Google AI Studio에서 API 키 발급

[https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) 에서 API 키를 발급받으세요.

### 2. 봇에게 DM으로 API 키 전송

Discord에서 봇을 직접 DM하여 아래 명령어를 입력하세요:

```
!api 여기에_API_키_입력
```

### 3. 저장 확인

봇이 아래 메시지로 응답하면 등록 완료입니다:

```
✅ API 키가 성공적으로 저장되었습니다.
```

API 키는 `config.json`에 자동 저장되어 **봇 재시작 후에도 유지**됩니다.

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

---

## 파일 구조

```
discord-bot-test/
├── bot.py                  # 메인 봇 코드
├── char-description.txt    # 캐릭터 설명 (수정 가능)
├── .env.example            # 환경변수 예시 파일
├── .env                    # 실제 환경변수 파일 (gitignore 처리됨)
├── config.json             # API 키 저장 파일 (봇 실행 시 자동 생성, gitignore 처리됨)
├── .gitignore
├── requirements.txt
└── README.md
```
