# 🚀 Деплой на Vercel (Фронтенд + Бэкенд + БД)

## Преимущества Vercel

✅ **Всё в одном месте** — фронтенд, бэкенд и БД на одной платформе
✅ **Нет проблем с CORS** — фронтенд и бэкенд на одном домене
✅ **Автоматическое масштабирование** — нет ошибок 502
✅ **Бесплатный тариф** — достаточно для большинства проектов
✅ **Простой деплой** — git push и готово

## Шаг 1: Создание базы данных Vercel Postgres

### 1.1. Создайте БД

1. Откройте ваш проект на Vercel
2. Перейдите на вкладку **Storage**
3. Нажмите **Create Database**
4. Выберите **Postgres**
5. Выберите регион (рекомендуется `iad1` — Washington, D.C.)
6. Нажмите **Create**

### 1.2. Подключите БД к проекту

1. После создания БД нажмите **Connect to Project**
2. Выберите ваш проект
3. Vercel автоматически добавит переменные окружения:
   - `POSTGRES_URL`
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DATABASE`
   - и другие

## Шаг 2: Подготовка кода

### 2.1. Структура проекта

Ваш проект должен выглядеть так:

```
CRM_car_wash_API/
├── backend/
│   ├── app.py              # Основной файл (будет адаптирован)
│   ├── vercel.json         # Конфигурация Vercel
│   ├── requirements.txt    # Зависимости Python
│   ├── extensions.py
│   ├── models.py
│   ├── auth.py
│   ├── utils.py
│   └── routes/
│       └── ...
└── frontend/
    ├── package.json
    ├── src/
    └── ...
```

### 2.2. Файл vercel.json

Уже создан в `backend/vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "FLASK_ENV": "production"
  }
}
```

### 2.3. Адаптация app.py

**Вариант 1: Использовать app_vercel.py**

Переименуйте текущий `app.py` в `app_railway.py` (для бэкапа), а `app_vercel.py` в `app.py`:

```bash
cd CRM_car_wash_API/backend
mv app.py app_railway.py
mv app_vercel.py app.py
```

**Вариант 2: Изменить текущий app.py**

Внесите следующие изменения в `app.py`:

1. **Замените строку подключения к БД:**

```python
# Было:
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "postgresql://postgres:1234@localhost:5432/crm_car_wash"
)

# Стало:
database_url = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "postgresql://postgres:1234@localhost:5432/crm_car_wash"
```

2. **Упростите CORS:**

```python
# Было: сложная конфигурация с origins_list
# Стало:
CORS(app)  # Фронтенд и бэкенд на одном домене
```

3. **Уберите инициализацию БД из create_app()**

Переместите блок `with app.app_context():` в отдельный роут `/api/init-db` (см. `app_vercel.py`)

4. **Удалите блок `if __name__ == "__main__":`**

На Vercel он не нужен.

### 2.4. Проверьте requirements.txt

Убедитесь, что есть все зависимости:

```txt
Flask==3.1.1
Flask-CORS==5.0.1
Flask-SQLAlchemy==3.1.1
SQLAlchemy==2.0.41
psycopg2-binary>=2.9.9
python-dotenv==1.0.0
pytz==2023.3
requests==2.31.0
openpyxl==3.1.2
PyJWT==2.8.0
bcrypt==4.1.2
```

**Важно:** Уберите `gunicorn` из `requirements.txt` для Vercel (он не нужен).

## Шаг 3: Настройка переменных окружения

### 3.1. В Vercel

Перейдите в **Settings → Environment Variables** и добавьте:

```bash
# Обязательные
JWT_SECRET=<минимум-32-случайных-символа>
DEFAULT_OWNER_LOGIN=owner
DEFAULT_OWNER_PASSWORD=owner123

# Опциональные
FLASK_ENV=production
```

**Важно:** `POSTGRES_URL` уже добавлена автоматически при подключении БД.

### 3.2. Для фронтенда

Если фронтенд на том же проекте Vercel:

```bash
REACT_APP_API_URL=/api
```

Или оставьте пустым — фронтенд будет обращаться к `/api/*` на том же домене.

## Шаг 4: Деплой

### 4.1. Деплой бэкенда

**Вариант 1: Через Vercel CLI**

```bash
cd CRM_car_wash_API/backend
vercel
```

**Вариант 2: Через Git**

1. Закоммитьте изменения:
   ```bash
   git add .
   git commit -m "feat: адаптация для Vercel"
   git push
   ```

2. Vercel автоматически задеплоит изменения

### 4.2. Инициализация БД

После успешного деплоя:

1. Откройте в браузере:
   ```
   https://ваш-домен.vercel.app/api/init-db
   ```

2. Вы должны увидеть:
   ```json
   {
     "status": "success",
     "message": "База данных инициализирована",
     "owner": {
       "login": "owner",
       "password": "owner123"
     }
   }
   ```

3. **ВАЖНО:** После инициализации удалите роут `/api/init-db` из кода (в целях безопасности)

### 4.3. Проверка работы

1. **Health check:**
   ```bash
   curl https://ваш-домен.vercel.app/api/health
   ```

2. **Логин:**
   ```bash
   curl -X POST https://ваш-домен.vercel.app/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"login":"owner","password":"owner123"}'
   ```

3. **Фронтенд:**
   Откройте фронтенд и попробуйте войти — не должно быть CORS ошибок!

## Шаг 5: Деплой фронтенда (если отдельно)

Если фронтенд на отдельном проекте Vercel:

1. Обновите `REACT_APP_API_URL` в переменных окружения:
   ```bash
   REACT_APP_API_URL=https://ваш-бэкенд.vercel.app/api
   ```

2. Задеплойте фронтенд:
   ```bash
   cd CRM_car_wash_API/frontend
   vercel
   ```

## Особенности Vercel Serverless

### ⚠️ Важные ограничения

1. **Время выполнения:** Максимум 10 секунд на бесплатном тарифе
2. **Холодный старт:** Первый запрос может быть медленным (1-2 секунды)
3. **Нет фоновых задач:** ProcessPoolExecutor для Excel не будет работать
4. **Нет постоянного хранилища:** Файлы не сохраняются между запросами

### 🔧 Решения

**Для экспорта Excel:**
- Используйте Vercel Blob Storage для хранения файлов
- Или используйте синхронный экспорт (без ProcessPoolExecutor)

**Для фоновых задач:**
- Используйте Vercel Cron Jobs
- Или внешний сервис (Celery + Redis)

## Troubleshooting

### Ошибка: "Module not found"

**Причина:** Не все зависимости установлены

**Решение:** Проверьте `requirements.txt` и убедитесь, что все импорты есть

### Ошибка: "Database connection failed"

**Причина:** Неправильная строка подключения

**Решение:** 
1. Проверьте, что `POSTGRES_URL` есть в переменных окружения
2. Убедитесь, что код заменяет `postgres://` на `postgresql://`

### CORS ошибка

**Причина:** Фронтенд и бэкенд на разных доменах

**Решение:**
1. Разместите фронтенд и бэкенд на одном проекте Vercel
2. Или настройте CORS с правильным origin

### Таймаут (10 секунд)

**Причина:** Запрос выполняется слишком долго

**Решение:**
1. Оптимизируйте запросы к БД (добавьте индексы)
2. Используйте пагинацию
3. Перенесите тяжёлые операции в фоновые задачи

## Миграция с Railway

После успешного деплоя на Vercel:

1. Экспортируйте данные из Railway (если нужно):
   ```bash
   pg_dump $DATABASE_URL > backup.sql
   ```

2. Импортируйте в Vercel Postgres:
   ```bash
   psql $POSTGRES_URL < backup.sql
   ```

3. Удалите проект на Railway

## Итоговый чеклист

- [ ] Создана БД Vercel Postgres
- [ ] БД подключена к проекту
- [ ] Создан `vercel.json`
- [ ] Адаптирован `app.py` (или используется `app_vercel.py`)
- [ ] Проверен `requirements.txt` (без gunicorn)
- [ ] Добавлены переменные окружения в Vercel
- [ ] Код задеплоен: `git push` или `vercel`
- [ ] Выполнена инициализация БД: `/api/init-db`
- [ ] Удалён роут `/api/init-db` из кода
- [ ] Health check работает
- [ ] Логин работает без CORS ошибок
- [ ] Фронтенд подключён к бэкенду

Готово! Ваше приложение работает на Vercel! 🎉
