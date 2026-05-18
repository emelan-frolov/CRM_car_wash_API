"""CRM Car Wash API — точка входа."""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from extensions import db
from routes import register_blueprints

load_dotenv()


def create_app(config=None):
    """Фабрика Flask-приложения.

    Args:
        config: dict с переопределениями конфигурации (для тестов).
    """
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "postgresql://postgres:1234@localhost:5432/crm_car_wash"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET"] = os.getenv(
        "JWT_SECRET", "change-me-in-production-very-secret-key"
    )
    app.config["JWT_EXPIRATION_HOURS"] = 24 * 7  # 7 дней

    if config:
        app.config.update(config)

    # Настройка CORS - максимально простая и надёжная
    cors_origins = os.getenv("CORS_ORIGINS", "*")
    origins_list = [origin.strip() for origin in cors_origins.split(",")]
    
    # Используем максимально разрешающую конфигурацию
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

    db.init_app(app)
    register_blueprints(app)

    # Временный эндпоинт для инициализации БД на Vercel
    # УДАЛИТЬ ПОСЛЕ ПЕРВОГО ИСПОЛЬЗОВАНИЯ!
    @app.route("/api/init-db", methods=["GET"])
    def init_database():
        """Инициализация базы данных. Использовать ОДИН РАЗ после деплоя на Vercel!
        
        ВАЖНО: Удалите этот эндпоинт после использования для безопасности!
        """
        try:
            from models import Box, User

            db.create_all()

            # Создать боксы по умолчанию, если их нет
            boxes_created = False
            if Box.query.count() == 0:
                default_boxes = [
                    Box(name="Бокс 1", order_index=0),
                    Box(name="Бокс 2", order_index=1),
                    Box(name="Бокс 3", order_index=2),
                ]
                for box in default_boxes:
                    db.session.add(box)
                db.session.commit()
                boxes_created = True

            # Создать владельца по умолчанию, если его нет
            owner_created = False
            owner_data = {}
            if not User.query.filter_by(role="owner").first():
                default_owner_login = os.getenv("DEFAULT_OWNER_LOGIN", "owner")
                default_owner_password = os.getenv("DEFAULT_OWNER_PASSWORD", "owner123")
                owner = User(
                    login=default_owner_login,
                    full_name="Владелец",
                    role="owner",
                    is_active=True,
                )
                owner.set_password(default_owner_password)
                db.session.add(owner)
                db.session.commit()
                owner_created = True
                owner_data = {
                    "login": default_owner_login,
                    "password": default_owner_password
                }

            return jsonify({
                "status": "success",
                "message": "База данных инициализирована",
                "boxes_created": boxes_created,
                "owner_created": owner_created,
                "owner": owner_data if owner_created else {"message": "Владелец уже существует"},
                "warning": "⚠️ УДАЛИТЕ этот эндпоинт /api/init-db после использования!"
            })
        except Exception as e:
            import traceback
            return jsonify({
                "status": "error",
                "message": str(e),
                "traceback": traceback.format_exc()
            }), 500

    return app


app = create_app()

if __name__ == "__main__":
    # Для Railway и других облачных платформ
    port = int(os.environ.get("PORT", 5000))
    # use_reloader=False обязателен при использовании ProcessPoolExecutor на Windows
    app.run(host='0.0.0.0', port=port, debug=os.getenv("FLASK_ENV") != "production", use_reloader=False)
