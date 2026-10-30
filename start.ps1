Write-Host "==================================================================" -ForegroundColor Magenta
Write-Host "Starting AISIA — Medical AI Orchestration Platform..." -ForegroundColor Magenta
Write-Host "Evidence-Grounded Medical Intelligence" -ForegroundColor Magenta
Write-Host "==================================================================" -ForegroundColor Magenta

Write-Host "[1/3] Starting Neo4j Medical Knowledge Graph (Docker)..." -ForegroundColor Yellow
docker-compose up -d neo4j

Write-Host "[2/3] Starting AISIA FastAPI Backend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "[3/3] Starting AISIA Medical Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "==================================================================" -ForegroundColor Green
Write-Host "AISIA MEDICAL PLATFORM INITIALIZED" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000/docs"
Write-Host "Frontend UI: http://localhost:5173"
Write-Host "==================================================================" -ForegroundColor Green
