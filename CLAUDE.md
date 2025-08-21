# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend service for POI (Points of Interest) data management with spatial indexing using KD-trees for efficient nearest neighbor searches. Deployed on Vercel.

## Commands

### Running the Application
```bash
# Local development
python app/main.py
# Or with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API documentation available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api.py
```

### Code Quality
```bash
# Format code with black
black app/ tests/

# Lint with flake8
flake8 app/ tests/

# Type checking
mypy app/

# Run pre-commit hooks
pre-commit run --all-files
```

### Development Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

### Docker Operations
```bash
# Build Docker image
docker build -t poi-backend .

# Run container locally
docker run -d -p 8000:8000 --name poi-backend poi-backend

# Use docker-compose for development
docker-compose up --build

# View container logs
docker logs poi-backend

# Stop and remove container
docker stop poi-backend && docker rm poi-backend

# Check image size
docker images poi-backend
```

### Deployment
```bash
# Railway deployment (recommended)
railway login
railway init
railway up

# Google Cloud Run deployment
gcloud run deploy poi-backend \
  --source . \
  --region asia-east1 \
  --allow-unauthenticated

# Fly.io deployment
fly launch
fly deploy

# Vercel (NOT recommended due to 250MB limit)
vercel --prod
```

## Architecture

Modular FastAPI application with clear separation of concerns:

```
app/
├── api/           # API routes and endpoints
├── core/          # Core configuration and exception handling
├── models/        # Pydantic data models
├── services/      # Business logic layer (POI service)
├── utils/         # Utility functions (validators)
└── main.py        # Application entry point
```

Key components:
- **POIService**: Singleton service managing POI data and KD-trees
- **Pydantic Models**: Type-safe request/response validation
- **Configuration**: Environment-based settings using pydantic BaseSettings
- **Exception Handling**: Centralized error handling with detailed responses

## Code Conventions

- **Naming**: snake_case for functions/variables, kebab-case for API endpoints
- **Type Hints**: Use type hints for all function signatures
- **Comments**: Traditional Chinese for inline comments
- **Error Handling**: Custom exception handlers with detailed error responses
- **Validation**: Pydantic for API validation, custom validators for business logic
- **Testing**: pytest with coverage, separate unit and integration tests

## Key Implementation Details

- **Spatial Indexing**: KD-trees per POI type for O(log n) queries
- **Distance Calculation**: Geodesic distance using geopy for accuracy
- **Security**: File size limits, coordinate validation, configurable CORS
- **Performance**: Optimized "all" type queries, efficient batch processing
- **Configuration**: Environment variables for all settings (see .env.example)
- **Docker Support**: Multi-stage build for optimized image size (~780MB)
- **CSV Format**: Required columns: name, poi_type, lat, lng

## Deployment Considerations

- **Vercel**: Limited by 250MB serverless function size, not suitable for this project
- **Recommended**: Use Docker-based platforms (Railway, Render, Cloud Run, Fly.io)
- **Testing**: Always test locally with Docker before deploying
- **Environment**: Ensure all environment variables are configured in deployment platform