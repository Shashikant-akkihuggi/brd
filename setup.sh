#!/bin/bash

echo "Setting up BRD Generation Platform..."

# Backend setup
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cp .env.example .env
echo "Backend setup complete!"

# Frontend setup
echo "Setting up frontend..."
cd ../frontend
npm install
echo "Frontend setup complete!"

echo ""
echo "Setup complete! To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Then visit http://localhost:3000"
