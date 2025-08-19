"""POI 服務測試"""
import pytest
import pandas as pd
from io import BytesIO

from app.services.poi_service import POIService
from app.utils.validators import CSVValidator


@pytest.fixture
def poi_service():
    """建立 POI 服務實例"""
    return POIService()


@pytest.fixture
def sample_csv_data():
    """建立範例 CSV 資料"""
    data = {
        "name": ["台北101", "中正紀念堂", "故宮博物院", "西門町", "士林夜市"],
        "poi_type": ["landmark", "landmark", "museum", "shopping", "market"],
        "lat": [25.0339, 25.0347, 25.1023, 25.0420, 25.0880],
        "lng": [121.5645, 121.5217, 121.5487, 121.5073, 121.5241],
    }
    df = pd.DataFrame(data)

    # 轉換為 CSV bytes
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()


@pytest.fixture
def invalid_csv_data():
    """建立無效的 CSV 資料"""
    data = {
        "name": ["Invalid POI"],
        "poi_type": ["test"],
        "lat": [200],  # 無效的緯度
        "lng": [121.5],
    }
    df = pd.DataFrame(data)

    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()


class TestPOIService:
    """POI 服務測試類"""

    @pytest.mark.asyncio
    async def test_upload_valid_data(self, poi_service, sample_csv_data):
        """測試上傳有效資料"""
        result = await poi_service.upload_poi_data(sample_csv_data)

        assert result.total_records == 5
        assert len(result.poi_types) == 4
        assert "landmark" in result.poi_types
        assert poi_service.is_data_loaded()

    @pytest.mark.asyncio
    async def test_upload_invalid_coordinates(self, poi_service, invalid_csv_data):
        """測試上傳無效座標"""
        with pytest.raises(Exception) as exc_info:
            await poi_service.upload_poi_data(invalid_csv_data)

        # 檢查錯誤訊息，可能是 HTTPException 或其他異常
        error_msg = getattr(exc_info.value, "detail", str(exc_info.value))
        assert "無效緯度" in error_msg or "必須在 -90 到 90 之間" in error_msg

    @pytest.mark.asyncio
    async def test_find_nearest_single_type(self, poi_service, sample_csv_data):
        """測試查詢單一類型 POI"""
        await poi_service.upload_poi_data(sample_csv_data)

        results = poi_service.find_nearest_pois(25.0340, 121.5640, "landmark", k=2)

        assert len(results) == 2
        assert results[0].poi_type == "landmark"
        assert results[0].distance < results[1].distance

    @pytest.mark.asyncio
    async def test_find_nearest_all_types(self, poi_service, sample_csv_data):
        """測試查詢所有類型 POI"""
        await poi_service.upload_poi_data(sample_csv_data)

        results = poi_service.find_nearest_pois(25.0340, 121.5640, "all", k=3)

        assert len(results) == 3
        assert results[0].distance < results[1].distance < results[2].distance

    def test_find_nearest_without_data(self, poi_service):
        """測試在未載入資料時查詢"""
        with pytest.raises(ValueError) as exc_info:
            poi_service.find_nearest_pois(25.0340, 121.5640, "landmark")

        assert "尚未載入 POI 資料" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_clear_data(self, poi_service, sample_csv_data):
        """測試清除資料"""
        # 先載入資料
        await poi_service.upload_poi_data(sample_csv_data)
        assert poi_service.is_data_loaded()

        # 清除資料
        result = poi_service.clear_data()
        assert "清除" in result["message"]
        assert not poi_service.is_data_loaded()


class TestCSVValidator:
    """CSV 驗證器測試"""

    def test_validate_dataframe_missing_columns(self):
        """測試缺少必要欄位"""
        df = pd.DataFrame({"name": ["Test"], "lat": [25.0]})

        with pytest.raises(Exception) as exc_info:
            CSVValidator.validate_dataframe(df)

        assert "缺少必要欄位" in exc_info.value.detail

    def test_validate_dataframe_invalid_coordinates(self):
        """測試無效座標"""
        df = pd.DataFrame(
            {"name": ["Test"], "poi_type": ["test"], "lat": [95], "lng": [121]}  # 無效
        )

        with pytest.raises(Exception) as exc_info:
            CSVValidator.validate_dataframe(df)

        assert "無效緯度" in exc_info.value.detail

    def test_validate_dataframe_empty_values(self):
        """測試空值處理"""
        df = pd.DataFrame(
            {
                "name": ["Test", ""],
                "poi_type": ["test", "test2"],
                "lat": [25.0, 26.0],
                "lng": [121.0, 122.0],
            }
        )

        with pytest.raises(Exception) as exc_info:
            CSVValidator.validate_dataframe(df)

        assert "空的 POI 名稱" in exc_info.value.detail
