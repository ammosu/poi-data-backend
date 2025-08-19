"""POI 服務層"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from sklearn.neighbors import KDTree
from geopy.distance import geodesic
from datetime import datetime
import logging

from app.models.poi import POIResponse, UploadResponse
from app.utils.validators import CSVValidator
from app.core.config import settings

logger = logging.getLogger(__name__)


class POIService:
    """POI 資料管理服務"""

    def __init__(self):
        self.poi_data: Optional[pd.DataFrame] = None
        self.trees: Dict[str, KDTree] = {}
        self.upload_time: Optional[datetime] = None
        self._poi_types: List[str] = []

    def is_data_loaded(self) -> bool:
        """檢查是否已載入資料"""
        return self.poi_data is not None and len(self.trees) > 0

    def get_statistics(self) -> Dict:
        """取得資料統計"""
        if not self.is_data_loaded():
            return {
                "loaded": False,
                "total_records": 0,
                "poi_types": [],
                "upload_time": None,
            }

        return {
            "loaded": True,
            "total_records": len(self.poi_data),
            "poi_types": self._poi_types,
            "upload_time": self.upload_time,
        }

    async def upload_poi_data(self, file_content: bytes) -> UploadResponse:
        """上傳並處理 POI 資料"""
        try:
            # 讀取 CSV
            df = pd.read_csv(pd.io.common.BytesIO(file_content))

            # 驗證資料
            df = CSVValidator.validate_dataframe(df)

            # 儲存資料
            self.poi_data = df
            self.poi_data["coordinates"] = list(zip(df.lat, df.lng))

            # 建立 KD-trees
            self._build_kdtrees()

            # 更新元資料
            self.upload_time = datetime.now()
            self._poi_types = sorted(self.poi_data["poi_type"].unique().tolist())

            logger.info(f"成功載入 {len(df)} 筆 POI 資料，包含 {len(self._poi_types)} 種類型")

            return UploadResponse(
                message="POI 資料上傳並建立索引成功",
                total_records=len(df),
                poi_types=self._poi_types,
                upload_time=self.upload_time,
            )

        except pd.errors.EmptyDataError:
            raise ValueError("CSV 檔案是空的或格式不正確")
        except pd.errors.ParserError as e:
            raise ValueError(f"CSV 解析錯誤：{str(e)}")
        except Exception as e:
            logger.error(f"處理 POI 資料時發生錯誤：{str(e)}")
            raise

    def _build_kdtrees(self) -> None:
        """建立 KD-trees 索引"""
        self.trees = {}

        for poi_type, group in self.poi_data.groupby("poi_type"):
            if len(group) > 0:
                coords = np.array(list(group["coordinates"]))
                # 確保 leaf_size 至少為 1，對於小數據集使用較小的 leaf_size
                leaf_size = max(1, min(30, len(group) // 10))
                tree = KDTree(coords, leaf_size=leaf_size)
                self.trees[poi_type] = tree
                logger.debug(
                    f"為 {poi_type} 建立 KD-tree，包含 {len(group)} 個點，leaf_size={leaf_size}"
                )

    def find_nearest_pois(
        self, lat: float, lng: float, poi_type: str, k: Optional[int] = None
    ) -> List[POIResponse]:
        """尋找最近的 POI"""
        if not self.is_data_loaded():
            raise ValueError("尚未載入 POI 資料")

        k = k or settings.default_k_nearest
        k = min(k, settings.max_k_nearest)

        query_point = np.array([[lat, lng]])

        if poi_type == "all":
            return self._find_nearest_all_types(lat, lng, query_point, k)
        else:
            return self._find_nearest_single_type(lat, lng, query_point, poi_type, k)

    def _find_nearest_all_types(
        self, lat: float, lng: float, query_point: np.ndarray, k: int
    ) -> List[POIResponse]:
        """從所有類型中尋找最近的 POI"""
        all_candidates = []

        # 為了效率，每個類型先找 k 個候選
        for tree_poi_type, tree in self.trees.items():
            # 確保不會超過該類型的 POI 總數
            type_data = self.poi_data[self.poi_data["poi_type"] == tree_poi_type]
            actual_k = min(k, len(type_data))

            if actual_k == 0:
                continue

            try:
                dist, inds = tree.query(query_point, k=actual_k)

                for i in range(actual_k):
                    poi = type_data.iloc[inds[0][i]]
                    distance = geodesic((lat, lng), (poi["lat"], poi["lng"])).meters

                    all_candidates.append(
                        {
                            "distance": distance,
                            "data": POIResponse(
                                name=poi["name"],
                                poi_type=tree_poi_type,
                                distance=round(distance, 2),
                                latitude=poi["lat"],
                                longitude=poi["lng"],
                            ),
                        }
                    )
            except Exception as e:
                logger.error(f"查詢 {tree_poi_type} 類型時發生錯誤：{str(e)}")
                continue

        # 排序並返回前 k 個
        all_candidates.sort(key=lambda x: x["distance"])
        return [candidate["data"] for candidate in all_candidates[:k]]

    def _find_nearest_single_type(
        self, lat: float, lng: float, query_point: np.ndarray, poi_type: str, k: int
    ) -> List[POIResponse]:
        """從特定類型中尋找最近的 POI"""
        if poi_type not in self.trees:
            available_types = ", ".join(self._poi_types)
            raise ValueError(f"POI 類型 '{poi_type}' 不存在。可用類型：{available_types}")

        tree = self.trees[poi_type]
        type_data = self.poi_data[self.poi_data["poi_type"] == poi_type]

        # 確保不會超過該類型的 POI 總數
        actual_k = min(k, len(type_data))

        dist, inds = tree.query(query_point, k=actual_k)
        results = []

        for i in range(actual_k):
            poi = type_data.iloc[inds[0][i]]
            distance = geodesic((lat, lng), (poi["lat"], poi["lng"])).meters

            results.append(
                POIResponse(
                    name=poi["name"],
                    poi_type=poi_type,
                    distance=round(distance, 2),
                    latitude=poi["lat"],
                    longitude=poi["lng"],
                )
            )

        return results

    def clear_data(self) -> Dict[str, str]:
        """清除所有資料"""
        self.poi_data = None
        self.trees = {}
        self.upload_time = None
        self._poi_types = []

        logger.info("已清除所有 POI 資料和索引")
        return {"message": "POI 資料和索引已成功清除"}


# 建立單例服務實例
poi_service = POIService()
