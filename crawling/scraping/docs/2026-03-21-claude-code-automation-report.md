# Claude Code 자동화 리포트

이번 세션에서 반복적으로 지시한 내용을 분석하고, CLAUDE.md 설정으로 자동화하는 방법을 정리합니다.

---

## 1. 반복된 지시 패턴 분석

### 패턴 A: 코딩 컨벤션

| 반복 지시 | 횟수 | 예시 |
|-----------|------|------|
| 타입 힌트 추가해줘 | 1회 | "타입 힌트가 너무 없는 것 같아" |
| 파라미터 전부 필수로 해줘 | 2회 | "선택도 선택이 아닌거야", "미안한데 파라미터는 전부 필수값이라고" |
| 네이밍 변경해줘 | 4회 | "games로 변경", "seasons_players로 변경", "seasons_teams로 변경" |
| 파이썬 컨벤션에 맞춰줘 | 1회 | "fromDate 이런식으로 인자를 받을 수도 있어? 파이썬이라 맞지 않아서" |

### 패턴 B: Git 작업

| 반복 지시 | 횟수 |
|-----------|------|
| 커밋해줘 | 3회 |
| 커밋 및 푸시해줘 | 4회 |
| .idea 제외해줘 | 1회 |

### 패턴 C: 문서화

| 반복 지시 | 횟수 |
|-----------|------|
| README 업데이트해줘 | 2회 |
| API 명세 만들어줘 | 1회 |
| 작업 정리해줘 | 1회 |

### 패턴 D: 코드 품질

| 반복 지시 | 횟수 |
|-----------|------|
| 불필요한 import 제거 | 자동 감지 필요 |
| URL 가독성 개선 | 1회 ("base64encoding으로 하니까 보기가 힘들잔아") |
| parse에서 파싱하지 마 | 1회 ("원본 데이터를 볼 수 없잔아") |

---

## 2. CLAUDE.md로 자동화하는 방법

`CLAUDE.md`는 프로젝트별 지시사항을 저장하는 파일입니다. Claude Code는 대화 시작 시 이 파일을 자동으로 읽습니다.

### 프로젝트 CLAUDE.md (프로젝트 루트)

현재 프로젝트에만 적용됩니다.

```markdown
# CLAUDE.md

## 코딩 컨벤션
- 모든 함수에 타입 힌트 필수 (파라미터, 반환값)
- 클래스 변수에도 타입 명시
- 파이썬 네이밍 컨벤션: snake_case (fromDate X → from_date O)
- Spider 파라미터는 모든 값 필수, 기본값 사용 금지, 미지정 시 ValueError
- Spider의 parse()에서 데이터 가공하지 않고 원본 그대로 CrawledItem에 전달
- URL 파라미터는 딕셔너리로 관리 (URL 인코딩 문자열 직접 작성 금지)

## 네이밍 규칙
- Spider 파일명: {데이터소스}_{종목}_{API경로}.py
- Spider name: 파일명과 동일
- Spider 클래스: PascalCase + Spider 접미사
- data_type: Spider name과 동일

## Git
- .idea/ 는 항상 .gitignore에 포함
- 커밋 메시지는 한국어로 작성
- 커밋 시 Co-Authored-By 포함

## 문서
- Spider 추가 시 docstring에 실행 방법과 동작 흐름 작성
- API 엔드포인트 발견 시 docs/api-analysis/ 에 명세 추가
```

### 글로벌 CLAUDE.md (~/.claude/CLAUDE.md)

모든 프로젝트에 공통으로 적용됩니다.

```markdown
# 글로벌 CLAUDE.md

## 코딩 컨벤션
- 타입 힌트 필수 (파이썬)
- 파이썬 네이밍: snake_case 엄수
- 불필요한 import 자동 정리

## Git
- .idea/, .vscode/, __pycache__/ 는 .gitignore에 포함
- 커밋 메시지는 한국어

## 응답 스타일
- 작업 완료 후 요약은 간결하게
- 선택지를 줄 때는 표로 비교
```

---

## 3. 설정 방법

### 프로젝트 CLAUDE.md 적용

프로젝트 루트에 `CLAUDE.md` 파일을 수정하면 됩니다 (이미 존재).

### 글로벌 CLAUDE.md 적용

```bash
# 글로벌 설정 파일 생성/편집
vi ~/.claude/CLAUDE.md
```

### hooks (자동 실행)

`settings.json`에서 특정 이벤트에 명령어를 자동 실행할 수 있습니다:

```json
// ~/.claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "echo 'lint check'"
      }
    ]
  }
}
```

---

## 4. 이 프로젝트 CLAUDE.md 개선 제안

현재 CLAUDE.md에 없지만 추가하면 반복 지시가 줄어드는 항목:

| 추가 항목 | 효과 |
|-----------|------|
| 타입 힌트 필수 | "타입 힌트 추가해줘" 반복 제거 |
| 파라미터 필수 정책 | "파라미터 전부 필수로 해줘" 반복 제거 |
| snake_case 강제 | "파이썬 컨벤션에 맞춰줘" 반복 제거 |
| URL 딕셔너리 방식 | "URL 보기 안좋아" 반복 제거 |
| parse에서 원본 전달 | "파싱하지 마" 반복 제거 |
| .gitignore 정책 | ".idea 제외해줘" 반복 제거 |
| 네이밍 규칙 명시 | 이름 변경 요청 반복 제거 |

---

## 5. 다른 프로젝트에서도 적용하려면

`~/.claude/CLAUDE.md` (글로벌 설정)에 공통 규칙을 넣으면 **모든 프로젝트에서 자동 적용**됩니다.

프로젝트별 특화 규칙은 각 프로젝트의 `CLAUDE.md`에 작성합니다.

```
~/.claude/CLAUDE.md          ← 글로벌 (모든 프로젝트 공통)
프로젝트/CLAUDE.md            ← 프로젝트별 (해당 프로젝트만)
프로젝트/서브폴더/CLAUDE.md    ← 디렉토리별 (해당 폴더만)
```

우선순위: 디렉토리별 > 프로젝트별 > 글로벌 (모두 합쳐서 적용)

---

## 6. 세션 마무리 자동화

CLAUDE.md에 "세션 마무리 규칙"을 추가하면, 매 세션 종료 시 Claude가 자동으로:

1. 반복된 지시 패턴 분석
2. CLAUDE.md 추가 항목 제안
3. 글로벌 설정으로 빼야 할 항목 제안
4. Claude Code 설정(hooks, 스킬, MCP)으로 자동화 가능한 항목 제안
5. Claude Code 외적인 자동화 방법 제안 (CI/CD, lint, pre-commit 등)

이를 통해 **세션을 거듭할수록 반복 지시가 줄어드는 선순환** 구조를 만들 수 있다.

---

## 7. Claude Code 외적 자동화 방법

| 방법 | 자동화 내용 | 설정 위치 |
|------|------------|----------|
| **ruff** (Python linter) | 불필요한 import 제거, snake_case 강제, 코드 포맷팅 | `pyproject.toml` `[tool.ruff]` |
| **pre-commit hooks** | 커밋 전 lint, format 자동 실행 | `.pre-commit-config.yaml` |
| **GitHub Actions** | PR 시 자동 테스트, lint 체크 | `.github/workflows/` |
| **mypy** | 타입 힌트 누락 검출 | `pyproject.toml` `[tool.mypy]` |
| **Makefile** | 반복 명령어 단축 | `Makefile` |

### pyproject.toml에 ruff 설정 예시

```toml
[tool.ruff]
target-version = "py314"
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "N"]  # E: 에러, F: pyflakes, I: import 정렬, N: 네이밍

[tool.ruff.lint.isort]
known-first-party = ["scrapying", "api"]
```

### pre-commit 설정 예시

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```
