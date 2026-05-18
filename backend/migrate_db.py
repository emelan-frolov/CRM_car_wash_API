"""
Скрипт для пересоздания базы данных с новой структурой
"""
import os
import sys
from app import app
from extensions import db
from models import Box
from sqlalchemy import text

def recreate_database():
    with app.app_context():
        print("Удаление старых таблиц...")
        
        # Удаляем все таблицы
        db.drop_all()
        print("✓ Старые таблицы удалены")
        
        # Создаем новые таблицы
        print("\nСоздание новых таблиц...")
        db.create_all()
        print("✓ Новые таблицы созданы")
        
        # Создаем боксы по умолчанию
        print("\nСоздание боксов по умолчанию...")
        default_boxes = [
            Box(name='Бокс 1', order_index=0, is_active=True),
            Box(name='Бокс 2', order_index=1, is_active=True),
            Box(name='Бокс 3', order_index=2, is_active=True),
        ]
        for box in default_boxes:
            db.session.add(box)
        db.session.commit()
        print("✓ Созданы боксы: Бокс 1, Бокс 2, Бокс 3")
        
        print("\n✅ База данных успешно пересоздана!")
        print("\nТеперь можно запустить сервер: python app.py")

if __name__ == '__main__':
    print("=" * 50)
    print("ПЕРЕСОЗДАНИЕ БАЗЫ ДАННЫХ")
    print("=" * 50)
    print("\n⚠️  ВНИМАНИЕ: Все данные будут удалены!")
    
    # 1. Проверяем переменную окружения (для Railway)
    force_run = os.getenv('FORCE_RECREATE_DB', 'false').lower() == 'true'

    if force_run:
        print("\nАвтоматическое подтверждение получено (FORCE_RECREATE_DB=true)")
        recreate_database()
    else:
        # 2. Обычный режим для локального запуска
        try:
            confirm = input("\nПродолжить? (yes/no): ")
            if confirm.lower() == 'yes':
                recreate_database()
            else:
                print("Операция отменена")
        except EOFError:
            # Если скрипт запущен на Railway без переменной окружения
            print("\n❌ ОШИБКА: Скрипт запущен в среде без возможности ввода данных.")
            print("Чтобы запустить пересоздание базы на Railway, добавьте переменную FORCE_RECREATE_DB = true в настройках проекта.")
            sys.exit(1)
