"""CRM Car Wash API — точка входа для Vercel Serverless."""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from extensions import db
from routes import register_blueprints

load_dotenv()


def create_app(config=None):
    """Фабрика Flask-приложения для Vercel.

    Args:
        config: dict с переопределениями конфигурации (для тестов).
    """
    app = Flask(__name__)

    # Vercel Postgres выдаёт POSTGRES_URL, но SQLAlchemy требует postgresql://
    database_url = os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url or "postgresql://postgres:1234@localhost:5432/crm_car_wash"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET"] = os.getenv("JWT_SECRET", "change-me-in-production-very-secret-key")
    app.config["JWT_EXPIRATION_HOURS"] = 24 * 7  # 7 дней

    if config:
        app.config.update(config)

    # CORS для Vercel - фронтенд и бэкенд на одном домене
    CORS(app)

    db.init_app(app)
    register_blueprints(app)

    # Временный роут для инициализации БД (использовать один раз, потом удалить)
    @app.route("/api/init-db", methods=["GET"])
    def init_db():
        """Инициализация базы данных. Использовать ОДИН РАЗ после деплоя!"""
        try:
            from models import Box, User

            db.create_all()

            # Создать боксы по умолчанию, если их нет
            if Box.query.count() == 0:
                default_boxes = [
                    Box(name="Бокс 1", order_index=0),
                    Box(name="Бокс 2", order_index=1),
                    Box(name="Бокс 3", order_index=2),
                ]
                for box in default_boxes:
                    db.session.add(box)
                db.session.commit()

            # Создать владельца по умолчанию, если его нет
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

            return jsonify({
                "status": "success",
                "message": "База данных инициализирована",
                "owner": {
                    "login": default_owner_login,
                    "password": default_owner_password
                }
            })
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    return app


# Этот объект 'app' будет искать Vercel
app = create_app()

# Блок if __name__ == "__main__": на Vercel НЕ НУЖЕН
# Vercel запускает Flask как serverless функцию
