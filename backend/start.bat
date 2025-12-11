@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Initializing database...
python seed_data.py

echo.
echo Starting Flask server...
python app.py
