#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "=================================================="
echo " Starting Render Production Build Pipeline"
echo "=================================================="

# 1. Install Python backend & ML dependencies
echo ">>> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 2. Build React frontend
echo ">>> Installing and building React production bundle..."
cd frontend
npm install
npm run build
cd ..

echo "=================================================="
echo " Render Build Pipeline Completed Successfully!"
echo "=================================================="
