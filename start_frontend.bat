@echo off
echo Starting HUI Federated Learning - React Frontend
echo ===============================================

cd frontend

echo Installing dependencies...
call npm install

echo Starting development server...
call npm run dev

pause
