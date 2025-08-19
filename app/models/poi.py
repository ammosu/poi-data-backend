"""POI 資料模型定義"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class Coordinates(BaseModel):
    """座標模型"""

    latitude: float = Field(..., ge=-90, le=90, description="緯度")
    longitude: float = Field(..., ge=-180, le=180, description="經度")

    @validator("latitude")
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError(f"緯度必須在 -90 到 90 之間，當前值：{v}")
        return v

    @validator("longitude")
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError(f"經度必須在 -180 到 180 之間，當前值：{v}")
        return v


class POIData(BaseModel):
    """POI 資料模型"""

    name: str = Field(..., min_length=1, max_length=200, description="POI 名稱")
    poi_type: str = Field(..., min_length=1, max_length=50, description="POI 類型")
    lat: float = Field(..., ge=-90, le=90, description="緯度")
    lng: float = Field(..., ge=-180, le=180, description="經度")

    class Config:
        schema_extra = {
            "example": {
                "name": "台北 101",
                "poi_type": "landmark",
                "lat": 25.0339,
                "lng": 121.5645,
            }
        }


class POIResponse(BaseModel):
    """POI 查詢回應模型"""

    name: str
    poi_type: str
    distance: float = Field(..., ge=0, description="距離（公尺）")
    latitude: float
    longitude: float

    class Config:
        schema_extra = {
            "example": {
                "name": "台北 101",
                "poi_type": "landmark",
                "distance": 1234.56,
                "latitude": 25.0339,
                "longitude": 121.5645,
            }
        }


class NearestPOIQuery(BaseModel):
    """最近 POI 查詢參數"""

    lat: float = Field(..., ge=-90, le=90, description="查詢點緯度")
    lng: float = Field(..., ge=-180, le=180, description="查詢點經度")
    poi_type: str = Field(..., description="POI 類型，'all' 表示所有類型")
    k: Optional[int] = Field(None, ge=1, le=50, description="返回的 POI 數量")


class UploadResponse(BaseModel):
    """檔案上傳回應"""

    message: str
    total_records: int
    poi_types: List[str]
    upload_time: datetime

    class Config:
        schema_extra = {
            "example": {
                "message": "POI 資料上傳成功",
                "total_records": 1000,
                "poi_types": ["restaurant", "hotel", "landmark"],
                "upload_time": "2024-01-01T12:00:00",
            }
        }


class ErrorResponse(BaseModel):
    """錯誤回應模型"""

    error: str
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "緯度必須在 -90 到 90 之間",
                "status_code": 400,
                "timestamp": "2024-01-01T12:00:00",
            }
        }
