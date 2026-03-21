.PHONY: api api-dev api-stop

## FastAPI 서버 실행
api:
	-lsof -ti:8000 | xargs kill 2>/dev/null
	uv run uvicorn api.main:app --host 0.0.0.0 --port 8000

## FastAPI 서버 실행 (코드 변경 시 자동 재시작)
api-dev:
	-lsof -ti:8000 | xargs kill 2>/dev/null
	uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

## FastAPI 서버 종료
api-stop:
	-lsof -ti:8000 | xargs kill 2>/dev/null
	@echo "서버 종료 완료"
