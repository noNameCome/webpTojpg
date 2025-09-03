@echo off
chcp 65001 >nul
echo 🔥 WebP JPG Converter HACKER 빌드 시작 🔥
echo =============================================
echo.

echo [1/4] 기존 빌드 파일 정리...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec
echo ✅ 정리 완료

echo.
echo [2/4] PyInstaller로 EXE 빌드 중...
echo 📦 포함 라이브러리: Pillow, tkinterdnd2, pathlib, tempfile, zipfile
echo 🎨 아이콘: icon.ico
echo 🚀 모드: 단일 파일, 창 모드, 콘솔 숨김

pyinstaller --onefile --windowed --noconsole ^
    --name "WebP_JPG_Converter_HACKER" ^
    --icon="icon.ico" ^
    --hidden-import tkinterdnd2 ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --hidden-import pathlib ^
    --hidden-import tempfile ^
    --hidden-import zipfile ^
    --hidden-import threading ^
    --hidden-import queue ^
    --add-data "icon.ico;." ^
    webp_to_jpg_gui.py

echo.
echo [3/4] 빌드 결과 확인...
if exist "dist\WebP_JPG_Converter_HACKER.exe" (
    echo ✅ EXE 파일 생성 성공!
    echo 📂 위치: dist\WebP_JPG_Converter_HACKER.exe
    echo 📊 파일 크기:
    dir "dist\WebP_JPG_Converter_HACKER.exe" | findstr "WebP_JPG_Converter_HACKER.exe"
) else (
    echo ❌ EXE 파일 생성 실패
    echo 오류 로그를 확인하세요.
)

echo.
echo [4/4] 정리 작업...
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec
echo ✅ 임시 파일 정리 완료

echo.
echo 🎉 빌드 완료! 🎉
echo =============================================
echo 📁 실행 파일: dist\WebP_JPG_Converter_HACKER.exe
echo 🔥 지원 기능:
echo   - ZIP 파일 변환 (WebP → JPG)
echo   - 단일 WebP 파일 변환
echo   - 폴더 일괄 변환 (구조 유지)
echo   - 드래그앤드롭 지원
echo   - 해커 스타일 UI
echo =============================================
pause

