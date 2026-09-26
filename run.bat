@echo off
cd /d %~dp0
where python >nul 2>&1
if errorlevel 1 (
  echo 未找到 Python。请先安装 Python 3.11+ 并勾选 Add to PATH。
  echo https://www.python.org/downloads/
  exit /b 1
)
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if not exist .env copy .env.example .env
echo 请确认 .env 里已填写 OPENAI_API_KEY
uvicorn app.main:app --reload --port 8765
