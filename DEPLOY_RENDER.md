# Деплой Django на Render с PostgreSQL

## Что уже настроено:

✅ settings.py - настроен для production
✅ requirements.txt - PostgreSQL зависимости
✅ build.sh - скрипт для сборки
✅ .env - локальные переменные окружения
✅ .gitignore - исключены ненужные файлы

## Шаги для деплоя:

### 1. Создайте репозиторий на GitHub

```bash
git init
git add .
git commit -m "Initial commit for Render deploy"
git branch -M main
git remote add origin https://github.com/ваш-username/ваш-репозиторий.git
git push -u origin main
```

### 2. Создайте PostgreSQL базу на Render

1. Зайдите на https://render.com
2. New → PostgreSQL
3. Выберите Free план
4. Скопируйте **Internal Database URL** (формат: postgres://user:pass@host:port/db)

### 3. Создайте Web Service на Render

1. New → Web Service
2. Подключите ваш GitHub репозиторий
3. Настройки:
   - **Name**: ваше-имя-приложения
   - **Root Directory**: CATVID
   - **Build Command**: `chmod +x ../build.sh && ../build.sh`
   - **Start Command**: `gunicorn CATVID.wsgi:application --bind 0.0.0.0:$PORT`
   - **Environment**: Python 3

### 4. Добавьте Environment Variables

В настройках Web Service добавьте:

```
SECRET_KEY=ваш-секретный-ключ-django
DEBUG=False
ALLOWED_HOSTS=*
DATABASE_URL=postgres://user:password@host:port/database
```

**Важно**: DATABASE_URL берите из Internal Database URL вашей PostgreSQL базы на Render

### 5. Деплой

После сохранения настроек Render автоматически:
- Склонирует репозиторий
- Установит зависимости
- Соберет статические файлы
- Выполнит миграции
- Запустит приложение

### 6. Проверка

Ваше приложение будет доступно по URL: `https://ваше-имя-приложения.onrender.com`

## Локальная разработка

Для локальной работы используйте файл `.env`:

```bash
cd CATVID
python manage.py runserver
```

## Обновление приложения

Просто пушьте изменения в GitHub:

```bash
git add .
git commit -m "Update"
git push
```

Render автоматически задеплоит изменения.

## Troubleshooting

Если возникли проблемы:
1. Проверьте логи в Render Dashboard
2. Убедитесь что DATABASE_URL правильный (postgres://, не postgresql://)
3. Проверьте что все зависимости в requirements.txt
4. Убедитесь что build.sh исполняемый: `chmod +x build.sh`
