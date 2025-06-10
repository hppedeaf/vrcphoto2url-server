# Simple test for URL protocol fix
$SERVER_URL = "http://localhost:8080"

Write-Host "Testing server connection..." -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "$SERVER_URL/health" -Method GET -TimeoutSec 5
    Write-Host "✅ Server is running!" -ForegroundColor Green
    Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Server not responding on port 8080, trying 8000..." -ForegroundColor Red
    
    try {
        $SERVER_URL = "http://localhost:8000"
        $response = Invoke-RestMethod -Uri "$SERVER_URL/health" -Method GET -TimeoutSec 5
        Write-Host "✅ Server is running on port 8000!" -ForegroundColor Green
        Write-Host "Response: $($response | ConvertTo-Json)" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ Server not responding on either port" -ForegroundColor Red
        Write-Host "Please start the server first" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "`nServer URL: $SERVER_URL" -ForegroundColor Green
