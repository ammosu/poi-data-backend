"""FastAPI 應用程式主入口"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from contextlib import asynccontextmanager

from app.api.routes import router
from app.core.config import settings
from app.core.exceptions import (
    http_exception_handler,
    value_error_handler,
    general_exception_handler,
)

# 設定日誌
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    logger.info("啟動 POI 資料後端服務")
    logger.info(f"環境: {settings.environment}")
    logger.info(f"CORS 允許來源: {settings.cors_origins}")
    logger.info(f"最大上傳檔案大小: {settings.max_upload_size_mb} MB")
    yield
    logger.info("關閉 POI 資料後端服務")


# 建立 FastAPI 應用程式
app = FastAPI(
    title="POI 資料後端 API",
    description="提供 POI（Points of Interest）資料管理和空間查詢服務",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods_list,
    allow_headers=settings.cors_allow_headers_list,
)

# 加入信任主機中間件（用於生產環境）
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware, allowed_hosts=["*.vercel.app", "localhost"]
    )

# 註冊異常處理器
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(Exception, general_exception_handler)

# 註冊路由
app.include_router(router)


@app.get("/", tags=["Root"])
async def root():
    """根路徑"""
    return {
        "message": "POI 資料後端 API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower(),
    )
