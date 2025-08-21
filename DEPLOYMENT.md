# POI Backend 部署指南

## Docker 本地測試

```bash
# 建立並執行容器
docker-compose up --build

# 僅建立映像
docker build -t poi-backend .

# 執行容器
docker run -p 8000:8000 --env-file .env poi-backend
```

## Railway 部署

1. 安裝 Railway CLI
```bash
npm install -g @railway/cli
```

2. 部署
```bash
railway login
railway init
railway up
```

## Render 部署

1. 連接 GitHub 儲存庫
2. 選擇 "New Web Service"
3. 選擇 Docker 環境
4. 設定環境變數
5. 部署

## Google Cloud Run 部署

```bash
# 建立映像
gcloud builds submit --tag gcr.io/PROJECT-ID/poi-backend

# 部署到 Cloud Run
gcloud run deploy poi-backend \
  --image gcr.io/PROJECT-ID/poi-backend \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated
```

## Fly.io 部署

```bash
# 安裝 Fly CLI
curl -L https://fly.io/install.sh | sh

# 初始化
fly launch

# 部署
fly deploy
```

## 環境變數設定

所有平台都需要設定以下環境變數：

- `PROJECT_NAME`: POI-Backend
- `API_VERSION`: 1.0.0
- `ALLOW_ORIGINS`: * (生產環境請設定具體網域)
- `MAX_FILE_SIZE_MB`: 10
- `MAX_POI_PER_FILE`: 10000
- `DEFAULT_SEARCH_RADIUS_M`: 1000
- `MAX_SEARCH_RADIUS_M`: 50000

## 成本比較

| 平台 | 免費方案 | 適合場景 |
|------|---------|---------|
| Railway | $5 額度/月 | 快速部署、開發測試 |
| Render | 750小時/月 | 小型專案、個人使用 |
| Cloud Run | 200萬請求/月 | 企業級、自動擴展 |
| Fly.io | 3個小型VM | 全球部署、低延遲 |