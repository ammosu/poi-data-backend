# POI 資料後端服務

提供 POI（Points of Interest）資料管理和空間查詢的 FastAPI 後端服務。

## 🚀 功能特色

- **高效空間索引**：使用 KD-tree 實現 O(log n) 的最近鄰查詢
- **安全性增強**：檔案大小限制、座標驗證、CORS 管理
- **完整錯誤處理**：詳細的錯誤訊息和異常處理
- **模組化架構**：清晰的分層結構，易於維護和擴展
- **型別安全**：使用 Pydantic 進行資料驗證
- **測試覆蓋**：包含單元測試和 API 測試

## 📁 專案結構

```
poi-data-backend/
├── app/
│   ├── api/           # API 路由定義
│   ├── core/          # 核心配置和異常處理
│   ├── models/        # Pydantic 資料模型
│   ├── services/      # 業務邏輯層
│   ├── utils/         # 工具函數
│   └── main.py        # 應用程式入口
├── tests/             # 測試檔案
├── .env.example       # 環境變數範例
├── requirements.txt   # 專案依賴
└── app.py            # Vercel 部署相容層
```

## 🛠️ 安裝與設定

### 1. 環境設定

```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 2. 環境變數配置

複製環境變數範例並修改：

```bash
cp .env.example .env
```

主要設定項：
- `CORS_ORIGINS`: 允許的跨域來源（逗號分隔）
- `MAX_UPLOAD_SIZE_MB`: 最大上傳檔案大小
- `DEFAULT_K_NEAREST`: 預設返回的 POI 數量

### 3. 執行應用程式

```bash
# 開發模式（自動重載）
python app/main.py

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API 文件

啟動服務後，可以透過以下網址查看互動式 API 文件：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要端點

1. **上傳 POI 資料**
   - `POST /api/v1/poi/upload`
   - 上傳 CSV 檔案，格式需包含：name, poi_type, lat, lng

2. **查詢最近的 POI**
   - `GET /api/v1/poi/nearest`
   - 參數：lat, lng, poi_type, k（可選）

3. **取得 POI 類型列表**
   - `GET /api/v1/poi/types`

4. **取得統計資訊**
   - `GET /api/v1/poi/statistics`

5. **清除資料**
   - `DELETE /api/v1/poi/clear`

## 🧪 測試

```bash
# 執行所有測試
pytest

# 執行測試並顯示覆蓋率
pytest --cov=app

# 執行特定測試
pytest tests/test_api.py
```

## 🔧 開發工具

### 程式碼格式化

```bash
# 使用 black 格式化
black app/ tests/

# 檢查格式
black --check app/ tests/
```

### 程式碼檢查

```bash
# 使用 flake8 檢查
flake8 app/ tests/

# 使用 mypy 進行型別檢查
mypy app/
```

### Pre-commit Hooks

```bash
# 安裝 pre-commit hooks
pip install pre-commit
pre-commit install

# 手動執行
pre-commit run --all-files
```

## 📦 CSV 檔案格式

上傳的 CSV 檔案必須包含以下欄位：

| 欄位 | 類型 | 說明 | 範圍 |
|------|------|------|------|
| name | string | POI 名稱 | 不可為空 |
| poi_type | string | POI 類型 | 不可為空 |
| lat | float | 緯度 | -90 到 90 |
| lng | float | 經度 | -180 到 180 |

範例：
```csv
name,poi_type,lat,lng
台北101,landmark,25.0339,121.5645
中正紀念堂,landmark,25.0347,121.5217
故宮博物院,museum,25.1023,121.5487
```

## 🚀 部署

### Docker 部署（推薦）

專案包含 Docker 配置，可輕鬆部署到各種平台：

#### 本地測試

```bash
# 建置映像
docker build -t poi-backend .

# 執行容器
docker run -d -p 8000:8000 --name poi-backend poi-backend

# 或使用 docker-compose
docker-compose up --build
```

#### 部署平台選擇

由於包含大型科學計算套件（pandas、numpy、scikit-learn），Docker 映像約 780MB，超過 Vercel 的 250MB 限制。推薦使用以下平台：

1. **Railway**（最推薦）
   - 類似 Vercel 的部署體驗
   - 無大小限制
   - 自動從 GitHub 部署
   ```bash
   railway login
   railway init
   railway up
   ```

2. **Render**
   - 免費方案：750小時/月
   - 支援 Docker 部署
   - 自動 SSL

3. **Google Cloud Run**
   - 企業級解決方案
   - 按使用量計費
   - 每月 200萬次免費請求
   ```bash
   gcloud run deploy poi-backend \
     --source . \
     --region asia-east1 \
     --allow-unauthenticated
   ```

4. **Fly.io**
   - 全球邊緣部署
   - 免費方案：3個小型VM
   ```bash
   fly launch
   fly deploy
   ```

詳細部署說明請參考 [DEPLOYMENT.md](./DEPLOYMENT.md)

### Vercel 部署（檔案大小限制）

⚠️ **注意**：Vercel 有 250MB 的函數大小限制，本專案因依賴套件較大可能無法直接部署。

若要在 Vercel 部署，需要：
1. 精簡依賴套件
2. 使用外部資料庫服務
3. 考慮使用 Vercel Edge Functions

## 📝 改進記錄

### v2.1.0 Docker 支援（2025-08-21）
- ✅ **Docker 配置**：新增 Dockerfile 和 docker-compose.yml
- ✅ **多平台部署**：支援 Railway、Render、Cloud Run、Fly.io
- ✅ **部署文件**：新增 DEPLOYMENT.md 詳細部署指南
- ✅ **解決 Vercel 限制**：提供替代部署方案應對 250MB 限制

### v2.0.0 主要改進
- ✅ **安全性增強**：加入檔案大小限制、座標驗證、CORS 管理
- ✅ **架構重構**：模組化設計，分離關注點
- ✅ **錯誤處理**：完整的異常處理和詳細錯誤訊息
- ✅ **型別安全**：Pydantic 模型驗證
- ✅ **效能優化**：改進 "all" 類型查詢邏輯
- ✅ **測試覆蓋**：加入單元測試和整合測試
- ✅ **開發工具**：配置 linting、formatting、pre-commit

## 📄 授權

MIT License