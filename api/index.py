"""
Vercel Serverless Function для Flask API.
Этот файл является точкой входа для всех /api/* запросов на Vercel.
"""

import sys
import os

# Добавляем backend в путь поиска модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import create_app

# Создаем приложение
app = create_app()

# Vercel ищет переменную 'app' или функцию-обработчик
# Flask app уже является WSGI-приложением, поэтому просто экспортируем его
