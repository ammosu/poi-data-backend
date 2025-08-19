"""輸入驗證工具"""
import pandas as pd
from typing import Tuple
from fastapi import HTTPException, UploadFile
from app.core.config import settings


class CSVValidator:
    """CSV 檔案驗證器"""

    REQUIRED_COLUMNS = ["name", "poi_type", "lat", "lng"]

    @classmethod
    async def validate_file(cls, file: UploadFile) -> None:
        """驗證上傳的檔案"""
        # 檢查檔案副檔名
        if not file.filename.endswith(tuple(settings.allowed_extensions_list)):
            raise HTTPException(
                status_code=400,
                detail=f"不支援的檔案格式。允許的格式：{', '.join(settings.allowed_extensions_list)}",
            )

        # 檢查檔案大小
        file.file.seek(0, 2)  # 移到檔案結尾
        file_size = file.file.tell()
        file.file.seek(0)  # 重設到開頭

        if file_size > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=400, detail=f"檔案太大。最大允許大小：{settings.max_upload_size_mb} MB"
            )

        if file_size == 0:
            raise HTTPException(status_code=400, detail="檔案是空的")

    @classmethod
    def validate_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """驗證 DataFrame 內容"""
        # 檢查必要欄位
        missing_columns = set(cls.REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            raise HTTPException(
                status_code=400, detail=f"CSV 缺少必要欄位：{', '.join(missing_columns)}"
            )

        # 檢查是否有資料
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV 檔案沒有資料")

        # 檢查並移除空值
        null_counts = df[cls.REQUIRED_COLUMNS].isnull().sum()
        if null_counts.any():
            null_columns = null_counts[null_counts > 0].index.tolist()
            # 記錄警告並移除含有空值的行
            df = df.dropna(subset=cls.REQUIRED_COLUMNS)
            if df.empty:
                raise HTTPException(
                    status_code=400,
                    detail=f"移除空值後沒有有效資料。含空值欄位：{', '.join(null_columns)}",
                )

        # 驗證座標範圍
        invalid_lat = df[(df["lat"] < -90) | (df["lat"] > 90)]
        if not invalid_lat.empty:
            raise HTTPException(
                status_code=400, detail=f"發現 {len(invalid_lat)} 筆無效緯度（必須在 -90 到 90 之間）"
            )

        invalid_lng = df[(df["lng"] < -180) | (df["lng"] > 180)]
        if not invalid_lng.empty:
            raise HTTPException(
                status_code=400,
                detail=f"發現 {len(invalid_lng)} 筆無效經度（必須在 -180 到 180 之間）",
            )

        # 驗證名稱和類型不是空字串
        df["name"] = df["name"].astype(str).str.strip()
        df["poi_type"] = df["poi_type"].astype(str).str.strip()

        empty_names = df[df["name"] == ""]
        if not empty_names.empty:
            raise HTTPException(
                status_code=400, detail=f"發現 {len(empty_names)} 筆空的 POI 名稱"
            )

        empty_types = df[df["poi_type"] == ""]
        if not empty_types.empty:
            raise HTTPException(
                status_code=400, detail=f"發現 {len(empty_types)} 筆空的 POI 類型"
            )

        # 確保資料類型正確
        try:
            df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
            df["lng"] = pd.to_numeric(df["lng"], errors="coerce")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"座標轉換失敗：{str(e)}")

        # 再次檢查轉換後是否有 NaN
        if df[["lat", "lng"]].isnull().any().any():
            raise HTTPException(status_code=400, detail="座標包含無法轉換為數字的值")

        return df


def validate_coordinates(lat: float, lng: float) -> Tuple[float, float]:
    """驗證座標"""
    if not -90 <= lat <= 90:
        raise HTTPException(status_code=400, detail=f"無效的緯度：{lat}（必須在 -90 到 90 之間）")

    if not -180 <= lng <= 180:
        raise HTTPException(status_code=400, detail=f"無效的經度：{lng}（必須在 -180 到 180 之間）")

    return lat, lng
