@echo off
echo ==========================================
echo    WebP to JPG 변환기 시작 중...
echo ==========================================
echo.
echo Python으로 GUI 실행 중...
echo.

cd /d "%~dp0"
python webp_to_jpg_gui.py

if errorlevel 1 (
    echo.
    echo 오류가 발생했습니다.
    echo 설치.bat를 먼저 실행해주세요.
    echo.
)

pause
