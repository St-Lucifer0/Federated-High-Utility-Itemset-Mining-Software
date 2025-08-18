@echo off
echo Starting HUI Federated Learning - Node.js Backend
echo ================================================

cd backend_node

echo Installing dependencies...
call npm install

echo Setting up environment...
if not exist .env (
    copy .env.example .env
    echo Created .env file from template
)

echo Creating logs directory...
if not exist logs mkdir logs

echo Starting server in development mode...
call npm run dev

pause
