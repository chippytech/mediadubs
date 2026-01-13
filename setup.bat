@echo off
setlocal ENABLEDELAYEDEXPANSION

echo =====================================
echo        MediaDubs Setup
echo =====================================
echo.

REM =============================
REM 1. Python check
REM =============================
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.9+ not found.
    echo Install from:
    echo https://www.python.org/downloads/windows/
    echo Make sure "Add Python to PATH" is checked.
    pause
    exit /b 1
)

echo [OK] Python detected:
python --version
echo.

REM =============================
REM 2. pip + Python deps
REM =============================
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install numpy soundfile openai-whisper argostranslate piper-tts
echo.

REM =============================
REM 3. FFmpeg check
REM =============================
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not found.
    echo MediaDubs REQUIRES ffmpeg and ffprobe.
    echo Download from:
    echo https://ffmpeg.org/download.html
    echo Ensure ffmpeg and ffprobe are in PATH.
    echo.
) else (
    echo [OK] FFmpeg detected.
)
echo.

REM =============================
REM 4. Whisper model selection
REM =============================
echo =====================================
echo Whisper model selection
echo =====================================
echo.

choice /C BSM L /M "Choose Whisper model: [B]ase  [S]mall  [M]edium  [L]arge"
set WHISPER_CHOICE=%errorlevel%

if %WHISPER_CHOICE%==1 set WHISPER_MODEL=base
if %WHISPER_CHOICE%==2 set WHISPER_MODEL=small
if %WHISPER_CHOICE%==3 set WHISPER_MODEL=medium
if %WHISPER_CHOICE%==4 set WHISPER_MODEL=large

echo Selected Whisper model: %WHISPER_MODEL%
echo Pre-downloading Whisper model...
python - <<EOF
import whisper
whisper.load_model("%WHISPER_MODEL%")
EOF
echo.

REM =============================
REM 5. Argos language selection
REM =============================
echo =====================================
echo Argos Translate language models
echo =====================================
echo.
set /p SRC_LANG=Enter source language code (e.g. en):
set /p TGT_LANG=Enter target language code (e.g. es):

echo Installing Argos model %SRC_LANG% -> %TGT_LANG%
argos-translate-cli --install-language %SRC_LANG% %TGT_LANG%
echo.

REM =============================
REM 6. Piper voices (MANUAL)
REM =============================
echo =====================================
echo Piper Voice Models (MANUAL STEP)
echo =====================================
echo.
echo MediaDubs does NOT download Piper voices automatically.
echo.
echo Please download ONE OR MORE Piper voice models manually from:
echo.
echo   https://huggingface.co/rhasspy/piper-voices/
echo.
echo Steps:
echo   1. Open the link above
echo   2. Choose a language and voice (e.g. es_ES-davefx-medium.onnx)
echo   3. Download the .onnx file
echo   4. Place it anywhere on your system
echo.
echo You will pass the model path at runtime:
echo.
echo   mediadubs video.mp4 --src %SRC_LANG% --tgt %TGT_LANG% --voice PATH\TO\voice.onnx
echo.

REM =============================
REM Done
REM =============================
echo =====================================
echo MediaDubs setup complete.
echo =====================================
pause
