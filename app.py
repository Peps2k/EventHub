
from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_mail import Mail
from models import db, User

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'views.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from views import views
    app.register_blueprint(views)

    return app

app = create_app()