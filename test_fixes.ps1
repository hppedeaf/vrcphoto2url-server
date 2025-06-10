# Test URL protocol fix and image serving
$SERVER_URL = "http://localhost:8080"
$API_KEY = "your-secret-api-key-change-this"

Write-Host "🚀 Testing VRCPhoto2URL Fixes..." -ForegroundColor Green

# Test server connection
Write-Host "`n🔌 Testing Server Connection..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$SERVER_URL/health" -Method GET -TimeoutSec 10
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "✅ Server is running and accessible" -ForegroundColor Green
        $serverRunning = $true
    } else {
        Write-Host "❌ Server health check failed: $($healthResponse.StatusCode)" -ForegroundColor Red
        $serverRunning = $false
    }
} catch {
    Write-Host "❌ Cannot connect to server: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "🔧 Make sure server is running at $SERVER_URL" -ForegroundColor Blue
    $serverRunning = $false
}

if (-not $serverRunning) {
    Write-Host "`n❌ Cannot connect to server. Please start the server and try again." -ForegroundColor Red
    exit 1
}

# Test protocol fix
Write-Host "`n🔗 Testing URL Protocol Fix..." -ForegroundColor Yellow

# Create test file content
$testContent = "Test content for protocol testing"
$testBytes = [System.Text.Encoding]::UTF8.GetBytes($testContent)

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"
$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"test_protocol.txt`"",
    "Content-Type: text/plain",
    "",
    $testContent,
    "--$boundary--"
)
$body = $bodyLines -join $LF

try {
    $headers = @{
        'Authorization' = "Bearer $API_KEY"
        'Content-Type' = "multipart/form-data; boundary=$boundary"
    }
    
    $uploadResponse = Invoke-WebRequest -Uri "$SERVER_URL/upload" -Method POST -Body $body -Headers $headers -TimeoutSec 30
    
    if ($uploadResponse.StatusCode -eq 200) {
        $responseData = $uploadResponse.Content | ConvertFrom-Json
        $fileUrl = $responseData.url
        
        Write-Host "✅ Upload successful!" -ForegroundColor Green
        Write-Host "🔗 Generated URL: $fileUrl" -ForegroundColor Cyan
        
        # Check if URL has protocol
        if ($fileUrl.StartsWith('https://') -or $fileUrl.StartsWith('http://')) {
            Write-Host "✅ Protocol fix working! URL includes protocol." -ForegroundColor Green
            $protocolOk = $true
        } else {
            Write-Host "❌ Protocol fix failed! URL missing protocol." -ForegroundColor Red
            $protocolOk = $false
        }
        
        # Test file download
        Write-Host "`n📥 Testing File Download..." -ForegroundColor Yellow
        try {
            $downloadResponse = Invoke-WebRequest -Uri $fileUrl -Method GET -TimeoutSec 10
            if ($downloadResponse.StatusCode -eq 200) {
                Write-Host "✅ File download working!" -ForegroundColor Green
                Write-Host "📊 Content-Type: $($downloadResponse.Headers.'Content-Type')" -ForegroundColor Cyan
                Write-Host "📏 Content-Length: $($downloadResponse.Content.Length) bytes" -ForegroundColor Cyan
                $downloadOk = $true
            } else {
                Write-Host "❌ Download failed: $($downloadResponse.StatusCode)" -ForegroundColor Red
                $downloadOk = $false
            }
        } catch {
            Write-Host "❌ Download test error: $($_.Exception.Message)" -ForegroundColor Red
            $downloadOk = $false
        }
        
    } else {
        Write-Host "❌ Upload failed: $($uploadResponse.StatusCode)" -ForegroundColor Red
        $protocolOk = $false
        $downloadOk = $false
    }
} catch {
    Write-Host "❌ Upload test error: $($_.Exception.Message)" -ForegroundColor Red
    $protocolOk = $false
    $downloadOk = $false
}

# Summary
Write-Host "`n" + "="*60 -ForegroundColor White
Write-Host "📋 TEST SUMMARY" -ForegroundColor White
Write-Host "="*60 -ForegroundColor White

if ($protocolOk) {
    Write-Host "🔗 URL Protocol Fix:      ✅ PASS" -ForegroundColor Green
} else {
    Write-Host "🔗 URL Protocol Fix:      ❌ FAIL" -ForegroundColor Red
}

if ($downloadOk) {
    Write-Host "📥 File Download:        ✅ PASS" -ForegroundColor Green
} else {
    Write-Host "📥 File Download:        ❌ FAIL" -ForegroundColor Red
}

if ($protocolOk -and $downloadOk) {
    Write-Host "`n🎉 All tests passed! Both issues appear to be fixed." -ForegroundColor Green
} else {
    Write-Host "`n⚠️ Some tests failed. Please check the server configuration." -ForegroundColor Yellow
}
