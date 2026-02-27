from flask import Flask, render_template
from flask_login import LoginManager, login_required
from flask_wtf.csrf import CSRFProtect
from pathlib import Path
from dotenv import load_dotenv
import os

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"]       = str(HERE / "uploads")
app.config["MAX_CONTENT_LENGTH"]  = 10 * 1024 * 1024   # 10 MB
app.config["SECRET_KEY"]          = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["WTF_CSRF_TIME_LIMIT"] = 3600  

csrf = CSRFProtect(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

from models import init_db, User
init_db()

login_manager = LoginManager(app)
login_manager.login_view    = "auth.login"
login_manager.login_message = "Please log in to access the full dashboard."
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))

from routes import resume_bp
from auth   import auth_bp

app.register_blueprint(resume_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return render_template("landing.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)