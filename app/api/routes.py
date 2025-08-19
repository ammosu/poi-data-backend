"""API 路由定義"""
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Query, HTTPException

from app.models.poi import POIResponse, UploadResponse, ErrorResponse
from app.services.poi_service import poi_service
from app.utils.validators import CSVValidator, validate_coordinates
from app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["POI"])


@router.post(
    "/poi/upload",
    response_model=UploadResponse,
    responses={
        400: {"model": ErrorResponse, "description": "無效的檔案或資料"},
        413: {"model": ErrorResponse, "description": "檔案太大"},
        500: {"model": ErrorResponse, "description": "伺服器錯誤"},
    },
    summary="上傳 POI 資料",
    description="上傳包含 POI 資料的 CSV 檔案並建立空間索引",
)
async def upload_poi(file: UploadFile = File(..., description="POI 資料 CSV 檔案")):
    """上傳 POI 資料並建立 KD-tree 索引"""
    # 驗證檔案
    await CSVValidator.validate_file(file)

    # 讀取檔案內容
    content = await file.read()

    try:
        result = await poi_service.upload_poi_data(content)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理檔案時發生錯誤：{str(e)}")


@router.get(
    "/poi/nearest",
    response_model=List[POIResponse],
    responses={
        400: {"model": ErrorResponse, "description": "無效的參數或未載入資料"},
        404: {"model": ErrorResponse, "description": "找不到 POI"},
    },
    summary="查詢最近的 POI",
    description="根據座標查詢最近的 POI",
)
def get_nearest_poi(
    lat: float = Query(..., ge=-90, le=90, description="緯度"),
    lng: float = Query(..., ge=-180, le=180, description="經度"),
    poi_type: str = Query(..., description="POI 類型，使用 'all' 查詢所有類型"),
    k: Optional[int] = Query(None, ge=1, le=50, description="返回的 POI 數量"),
):
    """查詢最近的 POI"""
    # 驗證座標
    lat, lng = validate_coordinates(lat, lng)

    try:
        results = poi_service.find_nearest_pois(lat, lng, poi_type, k)

        if not results:
            raise HTTPException(status_code=404, detail="找不到符合條件的 POI")

        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/poi/types",
    response_model=List[str],
    summary="取得 POI 類型列表",
    description="取得目前載入資料中的所有 POI 類型",
)
def get_poi_types():
    """取得所有 POI 類型"""
    stats = poi_service.get_statistics()

    if not stats["loaded"]:
        raise HTTPException(status_code=400, detail="尚未載入 POI 資料")

    return stats["poi_types"]


@router.get("/poi/statistics", summary="取得資料統計", description="取得目前載入的 POI 資料統計資訊")
def get_statistics():
    """取得 POI 資料統計"""
    return poi_service.get_statistics()


@router.delete("/poi/clear", summary="清除資料", description="清除所有 POI 資料和索引")
def clear_data():
    """清除所有 POI 資料"""
    return poi_service.clear_data()


@router.get("/health", summary="健康檢查", description="檢查服務是否正常運作")
def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy",
        "data_loaded": poi_service.is_data_loaded(),
        "environment": settings.environment,
    }
