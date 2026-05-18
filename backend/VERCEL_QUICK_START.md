# ⚡ Vercel Quick Start

## За 5 минут

### 1. Создайте БД в Vercel

```
Vercel → Storage → Create Database → Postgres → Connect to Project
```

### 2. Переименуйте файлы

```bash
cd CRM_car_wash_API/backend
mv app.py app_railway.py
mv app_vercel.py app.py
```

### 3. Добавьте переменные окружения

```
Vercel → Settings → Environment Variables:

JWT_SECRET=<минимум-32-символа>
DEFAULT_OWNER_LOGIN=owner
DEFAULT_OWNER_PASSWORD=owner123
```

### 4. Задеплойте

```bash
git add .
git commit -m "feat: миграция на Vercel"
git push
```

### 5. Инициализируйте БД

Откройте в браузере:
```
https://ваш-домен.vercel.app/api/init-db
```

### 6. Удалите роут init-db

В `app.py` удалите функцию `init_db()` и её декоратор `@app.route("/api/init-db")`.

Закоммитьте:
```bash
git add app.py
git commit -m "security: удалён временный роут init-db"
git push
```

### 7. Проверьте

```bash
# Health check
curl https://ваш-домен.vercel.app/api/health

# Логин
curl -X POST https://ваш-домен.vercel.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"owner","password":"owner123"}'
```

## Готово! 🎉

Теперь:
- ✅ Фронтенд и бэкенд на одном домене
- ✅ Нет проблем с CORS
- ✅ Автоматическое масштабирование
- ✅ Бесплатно

## Что дальше?

- Обновите фронтенд: `REACT_APP_API_URL=/api`
- Удалите проект на Railway (если больше не нужен)
- Настройте кастомный домен в Vercel (опционально)

Подробная инструкция: `VERCEL_DEPLOY.md`
