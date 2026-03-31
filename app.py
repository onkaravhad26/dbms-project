from flask import Flask
from config import Config
import db as database
from routes.student_routes import student_bp
from routes.admin_routes import admin_bp

app = Flask(__name__)
app.config.from_object(Config)

database.init_app(app)

app.register_blueprint(student_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)
