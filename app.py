"""
相容層 - 用於 Vercel 部署
保留此檔案以確保 Vercel 配置可以正常運作
"""
from app.main import app

# 匯出 app 給 Vercel 使用
__all__ = ["app"]