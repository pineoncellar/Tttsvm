@echo off
echo 🚀 TTS虚拟麦克风 - 管理员启动器
echo ================================
echo.
echo 正在以管理员权限启动程序...
echo 这是为了确保全局热键在游戏中正常工作。
echo.

cd /d "%~dp0"

REM 检查是否存在 uv
where uv >nul 2>nul
if %errorlevel% == 0 (
    echo 使用 uv 启动...
    uv run python app.py
) else (
    echo 使用 python 启动...
    python app.py
)

echo.
echo 程序已退出，按任意键关闭此窗口...
pause >nul
