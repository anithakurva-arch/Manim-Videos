@echo off
cd /d "%~dp0"
".venv311\Scripts\python.exe" watch_downloads_and_render.py --folder "C:\Users\Coschool\Downloads\scripts" --quality m --render-existing
pause
