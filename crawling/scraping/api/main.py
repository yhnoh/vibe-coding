import uvicorn
from fastapi import FastAPI

from api.routers import naversports_kbo_router

app = FastAPI(title="KBO Data API", description="네이버 스포츠 KBO 데이터 조회 API")

app.include_router(naversports_kbo_router.router)

if __name__ == "__main__":
    uvicorn.run(app, port=8000, log_level="info")
