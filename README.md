# 채용공고 모니터

현대자동차, 현대로템, SK Careers, 삼성 커리어스를 매일 정해진 시간에 확인해서 경력, 정규직, SW 개발 관련 공고만 골라 텔레그램으로 보내는 Python 프로그램입니다.

원격으로 안정적으로 돌리는 기본 방식은 GitHub Actions 스케줄 실행 + 텔레그램 알림입니다. 집 밖에 있어도 스마트폰에서 텔레그램 메시지를 받고, GitHub 모바일 앱이나 브라우저에서 수동 실행도 할 수 있습니다.

## 동작 방식

- 현대자동차: 브라우저 컨텍스트 내부 API 호출로 목록 수집
- 현대로템: 렌더링된 채용 카드 DOM 파싱
- SK Careers: `더보기` 버튼을 눌러 목록 확장 후 DOM 파싱
- 삼성 커리어스: 경력 페이지 DOM 파싱
- 상태 저장: `data/seen_jobs.json`
- 알림: 텔레그램 봇

초기 실행에서 상태 파일이 비어 있으면 현재 공고를 먼저 저장만 하고 알림은 보내지 않습니다. 다음 실행부터 새 공고만 알립니다. 현재 공고도 바로 받아보고 싶으면 `--include-existing` 옵션으로 실행하면 됩니다.

## 로컬 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
copy .env.example .env
python -m job_monitor --dry-run --include-existing
```

`TELEGRAM_BOT_TOKEN`과 `TELEGRAM_CHAT_ID`를 `.env`에 넣은 뒤, 실제 실행은 아래처럼 하면 됩니다.

```bash
python -m job_monitor
```

## 텔레그램 설정

1. 텔레그램에서 `@BotFather`를 열고 봇을 생성합니다.
2. 발급된 봇 토큰을 `TELEGRAM_BOT_TOKEN`에 넣습니다.
3. 생성한 봇과 대화를 한 번 시작합니다.
4. 브라우저에서 `https://api.telegram.org/bot<토큰>/getUpdates`를 열어 `chat.id` 값을 확인합니다.
5. 그 값을 `TELEGRAM_CHAT_ID`에 넣습니다.

## GitHub Actions로 원격 실행

1. 이 폴더를 GitHub 저장소에 올립니다.
2. 저장소를 가능하면 private으로 둡니다.
3. 저장소 `Settings > Secrets and variables > Actions`에 아래 시크릿을 추가합니다.

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

4. 워크플로 기본 스케줄은 매일 한국시간 오전 7시입니다.
5. 시간을 바꾸고 싶으면 `.github/workflows/job-monitor.yml`의 cron 값을 수정합니다.

GitHub Actions는 UTC 기준으로 동작합니다. 현재 설정값 `0 22 * * *`는 한국시간 오전 7시입니다.

## 필터 조정

기본 필터는 아래 조건을 모두 만족하는 공고만 통과시킵니다.

- 경력
- 정규직
- SW 관련 키워드 포함
- 기획, 영업, 생산, 설비 같은 제외 키워드 미포함

필터를 바꾸고 싶으면 `.env`에서 아래 값을 수정하면 됩니다.

```text
INCLUDE_KEYWORDS=...
EXCLUDE_KEYWORDS=...
```

## 자주 쓰는 명령

```bash
python -m job_monitor --dry-run --include-existing
python -m job_monitor --source hyundai_motor --dry-run --include-existing
pytest
```