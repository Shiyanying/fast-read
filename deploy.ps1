# ReadSmart Deploy Script
# Rebuild database and redeploy application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ReadSmart Rebuild & Deploy" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop and remove containers
Write-Host "[1/5] Stopping containers and removing data..." -ForegroundColor Yellow
docker compose down -v
Write-Host ""

# Step 2: Rebuild images
Write-Host "[2/5] Rebuilding Docker images..." -ForegroundColor Yellow
docker compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 3: Start containers
Write-Host "[3/5] Starting containers..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Start failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Wait for database
Write-Host "[4/5] Waiting for database..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Step 5: Run migrations
Write-Host "[5/5] Running database migrations..." -ForegroundColor Yellow
docker compose exec -T backend alembic upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Migration may have failed" -ForegroundColor Red
} else {
    Write-Host "Migration successful!" -ForegroundColor Green
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access URLs:" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "View logs:" -ForegroundColor White
Write-Host "  docker compose logs -f" -ForegroundColor Gray
Write-Host ""
