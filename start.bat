@echo off
REM Start the AI Shorts Factory GUI on Windows (local use).
REM Double-click this file, or run:  start.bat
python -c "import gradio" 2>NUL || pip install -r requirements.txt
echo Starting AI Shorts Factory GUI...
echo Open the link printed below in your browser.
python app.py
pause
