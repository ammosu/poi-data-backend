"""應用程式配置管理"""
from typing import List
from pydantic import BaseSettings


class Settings(BaseSettings):
    """應用程式設定"""

    # API 設定
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False

    # CORS 設定
    cors_origins: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:8000"
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"

    # 檔案上傳設定
    max_upload_size_mb: int = 10
    allowed_extensions: str = ".csv"

    # 查詢設定
    default_k_nearest: int = 10
    max_k_nearest: int = 50

    # 日誌設定
    log_level: str = "INFO"

    # 環境
    environment: str = "development"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_allow_methods_list(self) -> List[str]:
        if self.cors_allow_methods == "*":
            return ["*"]
        return [method.strip() for method in self.cors_allow_methods.split(",")]

    @property
    def cors_allow_headers_list(self) -> List[str]:
        if self.cors_allow_headers == "*":
            return ["*"]
        return [header.strip() for header in self.cors_allow_headers.split(",")]

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
