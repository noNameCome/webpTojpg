@echo off
chcp 949 >nul
cls
echo ====================================
echo WebP to JPG 변환기 설치 스크립트
echo ====================================
echo.

echo 1단계: 기본 라이브러리 설치 중...
pip install Pillow
if errorlevel 1 (
    echo 오류: Pillow 설치에 실패했습니다.
    echo Python이 설치되어 있는지 확인해주세요.
    pause
    exit /b 1
)

echo.
echo 2단계: 드래그 앤 드롭 라이브러리 설치 중...
pip install tkinterdnd2
if errorlevel 1 (
    echo 경고: tkinterdnd2 설치에 실패했습니다.
    echo 파일 선택 버튼을 사용하시면 됩니다.
)

echo.
echo 3단계: 설치 확인 중...
python -c "import PIL; print('✅ Pillow 설치 완료')" 2>nul
if errorlevel 1 (
    echo ❌ Pillow 설치 실패
) else (
    echo ✅ Pillow 설치 성공
)

python -c "try: import tkinterdnd2; print('✅ tkinterdnd2 설치 완료'); except: print('⚠️ tkinterdnd2 설치 실패 - 파일 선택 버튼 사용')" 2>nul

echo.
echo ====================================
echo 설치가 완료되었습니다!
echo 실행.bat 를 눌러서 프로그램을 시작하세요.
echo ====================================
echo.
pause
