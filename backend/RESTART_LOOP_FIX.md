# 🔥 Исправление цикла перезагрузки Railway

## Проблема

Ваш сервер попал в **бесконечный цикл перезагрузки**:

1. Сервер запускается
2. `FORCE_RECREATE_DB=true` заставляет его удалять и пересоздавать всю БД
3. Это долгий процесс (10-30 секунд)
4. Railway не получает ответа на health checks → убивает контейнер
5. Railway запускает контейнер снова → цикл повторяется

**Симптомы в логах:**
```
⚠️ ВНИМАНИЕ: Все данные будут удалены!
Удаление старых таблиц...
Stopping Container
Starting Container
```

**Симптомы в браузере:**
```
Response to preflight request doesn't pass access control check
```

Это **НЕ проблема CORS** — это проблема стабильности сервера!

Когда браузер отправляет `OPTIONS` запрос, сервер либо:
- Падает в этот момент
- Занят удалением БД
- Не успевает ответить до таймаута

## Решение

### ⚠️ ШАГ 1: Удалите FORCE_RECREATE_DB (КРИТИЧЕСКИ ВАЖНО!)

**В Railway:**
1. Откройте ваш проект
2. Перейдите на вкладку **Variables**
3. Найдите переменную `FORCE_RECREATE_DB`
4. Нажмите на **крестик** справа от неё
5. Сохраните изменения

**Почему это важно:**
- База уже создана при первом запуске
- Пересоздание БД при каждом запуске **стирает все данные**
- Это занимает много времени и убивает контейнер

### ✅ ШАГ 2: Проверьте CORS_ORIGINS

В Railway → Variables должна быть:

```bash
CORS_ORIGINS=https://crm-car-wash-api.vercel.app
```

**Важно:**
- ✅ Точный адрес фронтенда
- ✅ Без слеша в конце
- ✅ Без пробелов
- ✅ С `https://` (не `http://`)

### ✅ ШАГ 3: Проверьте другие переменные

Убедитесь, что есть:

```bash
DATABASE_URL=<автоматически создаётся Railway>
JWT_SECRET=<минимум-32-случайных-символа>
FLASK_ENV=production
```

### ✅ ШАГ 4: Проверьте Start Command

В Railway → Settings → Deploy должно быть:

```bash
gunicorn app:app
```

Или с параметрами:

```bash
gunicorn app:app --workers 2 --timeout 120
```

## Проверка после исправления

### 1. Логи Railway должны показать:

```
✅ Созданы боксы по умолчанию
🔐 СОЗДАН ВЛАДЕЛЕЦ ПО УМОЛЧАНИЮ
   Логин:  owner
   Пароль: owner123
[INFO] Listening at: http://0.0.0.0:XXXX
```

**НЕ должно быть:**
- ❌ `⚠️ ВНИМАНИЕ: Все данные будут удалены!`
- ❌ `Stopping Container` сразу после старта
- ❌ Циклических перезапусков

### 2. Health check должен работать:

```bash
curl https://ваш-домен.railway.app/api/health
```

Ответ:
```json
{"status":"ok","message":"CRM Car Wash API is running"}
```

### 3. Логин с фронтенда должен работать

Откройте фронтенд и попробуйте войти:
- Логин: `owner`
- Пароль: `owner123`

**Не должно быть CORS ошибок!**

## Если проблема осталась

### Проверьте логи Railway

1. Railway → ваш проект → Deployments → последний деплой → View Logs

2. Найдите строки:
   - ✅ `🔐 СОЗДАН ВЛАДЕЛЕЦ` — хорошо, сервер запустился
   - ✅ `Listening at:` — хорошо, Gunicorn работает
   - ❌ `Stopping Container` — плохо, сервер падает
   - ❌ `Error` или `Traceback` — есть ошибка в коде

### Проверьте домен фронтенда

В браузере откройте консоль (F12) и выполните:

```javascript
console.log(window.location.origin)
```

Скопируйте результат **ТОЧНО** в `CORS_ORIGINS` в Railway.

### Временно разрешите все источники

Для теста можете временно установить:

```bash
CORS_ORIGINS=*
```

Если после этого логин работает → проблема была в неправильном адресе в `CORS_ORIGINS`.

## Что изменилось в коде

### app.py — упрощённая конфигурация CORS

```python
# Максимально разрешающая конфигурация
cors_origins = os.getenv("CORS_ORIGINS", "*")
origins_list = [origin.strip() for origin in cors_origins.split(",")]

CORS(
    app,
    resources={
        r"/*": {
            "origins": origins_list,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Disposition"],
            "supports_credentials": True,
        }
    },
)
```

### Инициализация БД внутри create_app()

```python
def create_app(config=None):
    # ... настройка ...
    
    # Инициализация БД (работает под Gunicorn)
    with app.app_context():
        db.create_all()
        # создание боксов и владельца...
    
    return app
```

Это гарантирует, что БД создастся один раз при старте, а не при каждом запросе.

## Итоговый чеклист

- [ ] Удалена переменная `FORCE_RECREATE_DB` в Railway
- [ ] Проверена переменная `CORS_ORIGINS` (точный адрес, без слеша)
- [ ] Start Command: `gunicorn app:app`
- [ ] Код задеплоен: `git push`
- [ ] Логи показывают `🔐 СОЗДАН ВЛАДЕЛЕЦ` без `Stopping Container`
- [ ] Health check работает: `curl https://домен/api/health`
- [ ] Логин с фронтенда работает без CORS ошибок

После выполнения всех пунктов сервер должен работать стабильно!
