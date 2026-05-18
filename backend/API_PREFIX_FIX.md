# Исправление префиксов API роутов

## Проблема

Фронтенд на Vercel отправлял запросы на `/api/boxes`, `/api/auth/login` и т.д., но бэкенд на Railway возвращал 404, что приводило к CORS ошибкам.

## Причина

В `routes/__init__.py` блюпринты регистрировались **без префикса** `/api`:
```python
app.register_blueprint(blueprint)  # ❌ Неправильно
```

Но в самих роутах (например, `routes/auth.py`, `routes/boxes.py`) пути были прописаны с префиксом:
```python
@bp.route("/api/auth/login", methods=["POST"])  # ❌ Двойной префикс
```

## Решение

1. **Добавлен префикс `/api` при регистрации блюпринтов** в `routes/__init__.py`:
```python
app.register_blueprint(blueprint, url_prefix='/api')  # ✅ Правильно
```

2. **Удален префикс `/api` из всех роутов** в файлах `routes/*.py`:
```python
@bp.route("/auth/login", methods=["POST"])  # ✅ Правильно
```

Теперь Flask автоматически складывает:
- Префикс блюпринта: `/api`
- Путь роута: `/auth/login`
- Итоговый URL: `/api/auth/login` ✅

## Результат

Все API-эндпоинты теперь доступны по правильным путям:
- `/api/auth/login`
- `/api/boxes`
- `/api/clients`
- `/api/orders`
- и т.д.

## Проверка

Для проверки работоспособности:
```bash
# Локально
python app.py
curl http://localhost:5000/api/health

# На Railway
curl https://your-app.railway.app/api/health
```

Должен вернуться JSON:
```json
{"status": "ok", "message": "CRM Car Wash API is running"}
```

## Дата исправления

18 мая 2026
