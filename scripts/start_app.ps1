$host.ui.RawUI.WindowTitle = "GP2MIDI Launcher"
Write-Host "Starting GP2MIDI..." -ForegroundColor Cyan

# Start Backend
Write-Host "Starting Backend (New Window)..." -ForegroundColor Green
Start-Process -FilePath "python" -ArgumentList "-m uvicorn main:app --reload --port 8000" -WorkingDirectory "..\backend"

# Wait a bit for backend to initialize
Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Starting Frontend (New Window)..." -ForegroundColor Green
# Use npm.cmd to ensure Windows executes it correctly
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "..\frontend"

Write-Host "Services started! Check the two new terminal windows." -ForegroundColor Cyan
