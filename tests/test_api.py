"""API 端點測試"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
import pandas as pd

from app.main import app


@pytest.fixture
def client():
    """建立測試客戶端"""
    return TestClient(app)


@pytest.fixture
def sample_csv_file():
    """建立範例 CSV 檔案"""
    data = {
        "name": ["台北101", "中正紀念堂", "故宮博物院"],
        "poi_type": ["landmark", "landmark", "museum"],
        "lat": [25.0339, 25.0347, 25.1023],
        "lng": [121.5645, 121.5217, 121.5487],
    }
    df = pd.DataFrame(data)

    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    return ("test.csv", csv_buffer, "text/csv")


class TestAPIEndpoints:
    """API 端點測試"""

    def test_root_endpoint(self, client):
        """測試根路徑"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self, client):
        """測試健康檢查"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "data_loaded" in data

    def test_upload_poi(self, client, sample_csv_file):
        """測試上傳 POI"""
        response = client.post("/api/v1/poi/upload", files={"file": sample_csv_file})
        assert response.status_code == 200
        data = response.json()
        assert data["total_records"] == 3
        assert "landmark" in data["poi_types"]

    def test_upload_invalid_file(self, client):
        """測試上傳無效檔案"""
        response = client.post(
            "/api/v1/poi/upload",
            files={"file": ("test.txt", b"invalid content", "text/plain")},
        )
        assert response.status_code == 400
        assert "不支援的檔案格式" in response.json()["detail"]

    def test_query_nearest_without_data(self, client):
        """測試在未載入資料時查詢"""
        # 先清除資料
        client.delete("/api/v1/poi/clear")

        response = client.get(
            "/api/v1/poi/nearest",
            params={"lat": 25.0339, "lng": 121.5645, "poi_type": "landmark"},
        )
        assert response.status_code == 400
        assert "尚未載入 POI 資料" in response.json()["detail"]

    def test_query_nearest_with_data(self, client, sample_csv_file):
        """測試查詢最近 POI"""
        # 先上傳資料
        client.post("/api/v1/poi/upload", files={"file": sample_csv_file})

        # 查詢
        response = client.get(
            "/api/v1/poi/nearest",
            params={"lat": 25.0339, "lng": 121.5645, "poi_type": "landmark"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["poi_type"] == "landmark"

    def test_query_all_types(self, client, sample_csv_file):
        """測試查詢所有類型"""
        # 先上傳資料
        client.post("/api/v1/poi/upload", files={"file": sample_csv_file})

        # 查詢
        response = client.get(
            "/api/v1/poi/nearest",
            params={"lat": 25.0339, "lng": 121.5645, "poi_type": "all", "k": 2},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_query_invalid_coordinates(self, client):
        """測試無效座標"""
        response = client.get(
            "/api/v1/poi/nearest",
            params={"lat": 200, "lng": 121.5645, "poi_type": "landmark"},
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_get_poi_types(self, client, sample_csv_file):
        """測試取得 POI 類型"""
        # 先上傳資料
        client.post("/api/v1/poi/upload", files={"file": sample_csv_file})

        response = client.get("/api/v1/poi/types")
        assert response.status_code == 200
        types = response.json()
        assert "landmark" in types
        assert "museum" in types

    def test_get_statistics(self, client, sample_csv_file):
        """測試取得統計資訊"""
        # 先上傳資料
        client.post("/api/v1/poi/upload", files={"file": sample_csv_file})

        response = client.get("/api/v1/poi/statistics")
        assert response.status_code == 200
        stats = response.json()
        assert stats["loaded"] is True
        assert stats["total_records"] == 3

    def test_clear_data(self, client, sample_csv_file):
        """測試清除資料"""
        # 先上傳資料
        client.post("/api/v1/poi/upload", files={"file": sample_csv_file})

        # 清除
        response = client.delete("/api/v1/poi/clear")
        assert response.status_code == 200

        # 確認已清除
        stats_response = client.get("/api/v1/poi/statistics")
        stats = stats_response.json()
        assert stats["loaded"] is False
