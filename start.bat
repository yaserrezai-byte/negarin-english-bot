@echo off
title ربات آموزش زبان - Appwrite
color 0a

echo ==========================================
echo  🤖 ربات آموزش زبان انگلیسی
echo  ==========================================
echo.

echo [1/3] در حال نصب کتابخانه‌ها...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ خطا در نصب کتابخانه‌ها. مطمئن شوید پایتون نصب است.
    pause
    exit /b
)
echo ✅ کتابخانه‌ها نصب شدند.
echo.

echo [2/3] در حال ورود داده‌های اولیه به Appwrite...
python seed.py
if %errorlevel% neq 0 (
    echo ❌ خطا در ورود داده‌ها. Appwrite Key را بررسی کنید.
    pause
    exit /b
)
echo ✅ داده‌ها وارد شدند.
echo.

echo [3/3] در حال روشن کردن ربات...
echo ✅ ربات روشن شد! این پنجره را نبندید.
echo.
python src\main.py

pause
