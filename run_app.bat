@echo off
cd /d "%~dp0"
python -m pip install -r requirements.txt
if not exist backend\emergency.exe (
  gcc backend\main.c backend\incident.c backend\priority.c backend\heap.c backend\vehicle.c backend\graph.c backend\dijkstra.c -o backend\emergency.exe
  if errorlevel 1 pause & exit /b 1
)
python -m streamlit run frontend\app.py
pause
