@echo off
echo ========================================
echo Деплой Django на Render - Быстрый старт
echo ========================================
echo.

echo [1/5] Инициализация Git репозитория...
git init
git add .
git commit -m "Initial commit for Render deploy"
git branch -M main

echo.
echo [2/5] Теперь создайте репозиторий на GitHub
echo Перейдите на https://github.com/new
echo.
pause

echo.
echo [3/5] Введите URL вашего GitHub репозитория:
set /p REPO_URL="URL (например: https://github.com/username/repo.git): "

git remote add origin %REPO_URL%
git push -u origin main

echo.
echo [4/5] Теперь настройте Render:
echo.
echo 1. Зайдите на https://render.com
echo 2. New → MySQL (создайте базу данных)
echo 3. Скопируйте Internal Database URL
echo 4. New → Web Service (подключите GitHub репозиторий)
echo.
echo Настройки Web Service:
echo - Root Directory: CATVID
echo - Build Command: chmod +x ../build.sh ^&^& ../build.sh
echo - Start Command: gunicorn CATVID.wsgi:application --bind 0.0.0.0:$PORT
echo.
echo Environment Variables:
echo - SECRET_KEY=ваш-секретный-ключ
echo - DEBUG=False
echo - ALLOWED_HOSTS=*
echo - DATABASE_URL=mysql://user:pass@host:port/db (из MySQL Internal URL)
echo.
pause

echo.
echo [5/5] Готово! Ваше приложение будет задеплоено автоматически.
echo.
pause
