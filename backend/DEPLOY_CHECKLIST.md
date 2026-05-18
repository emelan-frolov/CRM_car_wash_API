# ✅ Чеклист деплоя на Railway

## 🔥 КРИТИЧЕСКАЯ ПРОБЛЕМА: Цикл перезагрузки

**Если сервер постоянно перезапускается:**

Это происходит из-за `FORCE_RECREATE_DB=true` в Railway Variables.

**Симптомы:**
- Логи показывают: `Stopping Container` → `Starting Container` → повторяется
- Браузер пишет: "Response to preflight request doesn't pass access control check"
- Сервер не отвечает на запросы

**Решение:**
1. Railway → Variables → **УДАЛИТЕ** `FORCE_RECREATE_DB`
2. Перезапустите сервис
3. Проверьте логи — должно быть `🔐 СОЗДАН ВЛАДЕЛЕЦ` без `Stopping Container`

Подробнее: см. `RESTART_LOOP_FIX.md`

## Что было исправлено

- ✅ **CORS упрощён**: Максимально разрешающая конфигурация `r"/*"` + `supports_credentials`
- ✅ **Инициализация БД**: Перенесена в `create_app()` — работает под Gunicorn
- ✅ **Порт**: Используется `PORT` из окружения + `host='0.0.0.0'`
- ✅ **Gunicorn**: Уже есть в `requirements.txt`

## ⚠️ ПЕРВЫМ ДЕЛОМ: Удалите FORCE_RECREATE_DB!

Если в Railway есть переменная `FORCE_RECREATE_DB`, **удалите её немедленно**!

Она стирает всю базу данных при каждом перезапуске сервера.

**Как удалить:**
1. Railway → ваш проект → Variables
2. Найдите `FORCE_RECREATE_DB`
3. Нажмите на крестик справа
4. Сохраните изменения

## Что нужно сделать в Railway

### 1. Переменные окружения (Variables)

```bash
# Обязательно
DATABASE_URL=<автоматически создастся при добавлении PostgreSQL>
JWT_SECRET=<минимум-32-случайных-символа>

# Рекомендуется
CORS_ORIGINS=https://crm-car-wash-api.vercel.app
FLASK_ENV=production
```

**Важно:** В `CORS_ORIGINS` НЕ должно быть:
- ❌ Слеша в конце: `https://example.com/`
- ❌ Пробелов: `https://example.com , https://other.com`
- ✅ Правильно: `https://example.com` или `https://example.com,https://other.com`

### 2. Start Command

```bash
gunicorn app:app
```

### 3. Добавить PostgreSQL

В Railway:
1. New → Database → Add PostgreSQL
2. `DATABASE_URL` появится автоматически

## Проверка работы

### 1. Логи Railway должны показать:

```
✅ Созданы боксы по умолчанию
🔐 СОЗДАН ВЛАДЕЛЕЦ ПО УМОЛЧАНИЮ
   Логин:  owner
   Пароль: owner123
```

### 2. Проверьте API:

```bash
# Health check
curl https://ваш-домен.railway.app/api/health

# Логин
curl -X POST https://ваш-домен.railway.app/api/login \
  -H "Content-Type: application/json" \
  -d '{"login":"owner","password":"owner123"}'
```

## Если CORS всё ещё не работает

### Вариант 1: Временно разрешить всё
Удалите переменную `CORS_ORIGINS` из Railway → перезапустите → проверьте

### Вариант 2: Проверьте адрес фронтенда
```bash
# В браузере откройте консоль и выполните:
console.log(window.location.origin)

# Скопируйте результат ТОЧНО в CORS_ORIGINS
```

### Вариант 3: Проверьте, что сервер вообще отвечает
Если браузер пишет "CORS error", но `curl` работает → проблема в настройке CORS
Если `curl` тоже не работает → проблема в самом сервере (смотрите логи Railway)

## Частые ошибки

| Ошибка | Причина | Решение |
|--------|---------|---------|
| **CORS blocked** | Неправильное регулярное выражение `r"/api/*"` | ✅ Исправлено на `r"/*"` |
| CORS blocked | Неправильный `CORS_ORIGINS` | Проверьте на пробелы/слеши |
| **База стирается** | `FORCE_RECREATE_DB=true` | ⚠️ **УДАЛИТЕ эту переменную!** |
| 500 при старте | Нет `DATABASE_URL` | Добавьте PostgreSQL в Railway |
| Владелец не создался | Старая версия кода | Теперь невозможно — исправлено |
| Connection refused | Неправильный порт | Используйте `gunicorn app:app` |

## Следующие шаги

1. Задеплойте код на Railway
2. Проверьте логи на наличие сообщений о создании владельца
3. Попробуйте залогиниться с фронтенда
4. Если CORS ошибка — проверьте `CORS_ORIGINS` на точность
