
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, abort
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from flask_wtf.csrf import CSRFProtect
from authlib.integrations.flask_client import OAuth
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from werkzeug.utils import secure_filename
from sqlalchemy import func
from urllib.parse import urlparse, urljoin
from dotenv import load_dotenv

from utils import extract_text, analyze
from models import db, User, ResumeAnalysis

import os
import uuid
import re


# --------------------------------------------------
# 1. INITIAL CONFIGURATION
# --------------------------------------------------

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key-for-local-development"
)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

if os.getenv("FLASK_ENV") == "production":
    app.config["SESSION_COOKIE_SECURE"] = True


# --------------------------------------------------
# 2. DATABASE CONFIGURATION
# --------------------------------------------------

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL is missing from .env")

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://",
        "postgresql://",
        1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)


# --------------------------------------------------
# 3. LOGIN AND SECURITY CONFIGURATION
# --------------------------------------------------

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "Please sign in to continue."
login_manager.login_message_category = "info"

csrf = CSRFProtect(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# --------------------------------------------------
# 4. GOOGLE OAUTH CONFIGURATION
# --------------------------------------------------

oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/.well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)


# --------------------------------------------------
# 5. DATABASE INITIALIZATION
# --------------------------------------------------

with app.app_context():
    db.create_all()


# --------------------------------------------------
# 6. HELPER FUNCTIONS
# --------------------------------------------------

def get_dashboard_data():

    total_screenings = ResumeAnalysis.query.filter_by(
        user_id=current_user.id
    ).count()

    average_score = db.session.query(
        func.avg(ResumeAnalysis.ats_score)
    ).filter(
        ResumeAnalysis.user_id == current_user.id
    ).scalar()

    strong_matches = ResumeAnalysis.query.filter(
        ResumeAnalysis.user_id == current_user.id,
        ResumeAnalysis.ats_score >= 70
    ).count()

    recent_analyses = ResumeAnalysis.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ResumeAnalysis.uploaded_at.desc()
    ).limit(5).all()

    history_records = ResumeAnalysis.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ResumeAnalysis.uploaded_at.desc()
    ).all()

    return {
        "total_screenings": total_screenings,
        "average_score": round(float(average_score or 0)),
        "strong_matches": strong_matches,
        "recent_analyses": recent_analyses,
        "history_records": history_records
    }


def safe_next_url(target):

    if not target:
        return None

    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))

    if (
        redirect_url.scheme in ("http", "https")
        and host_url.netloc == redirect_url.netloc
    ):
        return target

    return None


# --------------------------------------------------
# 7. PUBLIC HOMEPAGE
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        # Resume screening requires authentication
        if not current_user.is_authenticated:
            flash(
                "Please sign in to screen resumes.",
                "info"
            )
            return redirect(url_for("login"))

        result = None
        error_message = None

        uploaded_file = request.files.get("resume")

        job_description = request.form.get(
            "job_description", ""
        ).strip()

        if not uploaded_file or uploaded_file.filename == "":
            error_message = "Please select a resume file."

        elif not job_description:
            error_message = "Please enter a job description."

        else:

            original_name = secure_filename(
                uploaded_file.filename
            )

            extension = (
                original_name.rsplit(".", 1)[-1].lower()
                if "." in original_name else ""
            )

            if extension not in {"pdf", "docx"}:

                error_message = (
                    "Please upload a PDF or DOCX resume."
                )

            else:

                unique_name = (
                    f"{uuid.uuid4().hex}_{original_name}"
                )

                file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    unique_name
                )

                try:

                    uploaded_file.save(file_path)

                    resume_text = extract_text(file_path)

                    if not resume_text.strip():
                        raise ValueError(
                            "No readable text was found in this resume."
                        )

                    result = analyze(
                        resume_text,
                        job_description
                    )

                    analysis = ResumeAnalysis(
                        user_id=current_user.id,
                        resume_name=original_name,
                        ats_score=result["score"],
                        matched_skills=", ".join(
                            result["matched"]
                        ),
                        missing_skills=", ".join(
                            result["missing"]
                        ),
                        job_description=job_description
                    )

                    db.session.add(analysis)
                    db.session.commit()

                except Exception as error:

                    db.session.rollback()

                    app.logger.exception(
                        "Resume analysis failed"
                    )

                    error_message = str(error)

                finally:

                    if os.path.exists(file_path):
                        os.remove(file_path)

        dashboard_data = get_dashboard_data()

        return render_template(
            "index.html",
            result=result,
            error_message=error_message,
            **dashboard_data
        )

    # Public visitors do not see another user's dashboard data.
    dashboard_data = {
        "total_screenings": 0,
        "average_score": 0,
        "strong_matches": 0,
        "recent_analyses": [],
        "history_records": []
    }

    if current_user.is_authenticated:
        dashboard_data = get_dashboard_data()

    return render_template(
        "index.html",
        result=None,
        error_message=None,
        **dashboard_data
    )


# --------------------------------------------------
# 8. PRIVATE DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    dashboard_data = get_dashboard_data()

    return render_template(
        "index.html",
        result=None,
        error_message=None,
        **dashboard_data
    )


# --------------------------------------------------
# 9. EMAIL REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")

        confirm_password = request.form.get(
            "confirm_password", ""
        )

        if not name or not email or not password:
            flash("Please fill in all required fields.", "error")

        elif not re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email
        ):
            flash("Please enter a valid email address.", "error")

        elif len(password) < 8:
            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        elif User.query.filter_by(email=email).first():
            flash(
                "An account with this email already exists.",
                "error"
            )

        else:

            user = User(
                name=name,
                email=email,
                password=generate_password_hash(password)
            )

            try:

                db.session.add(user)
                db.session.commit()

                login_user(user)

                flash(
                    "Your account has been created successfully!",
                    "success"
                )

                return redirect(url_for("dashboard"))

            except Exception:

                db.session.rollback()

                app.logger.exception(
                    "Registration failed"
                )

                flash(
                    "Unable to create your account. Please try again.",
                    "error"
                )

    return render_template("register.html")


# --------------------------------------------------
# 10. EMAIL LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get("password", "")

        user = User.query.filter_by(
            email=email
        ).first()

        if (
            user
            and user.password
            and check_password_hash(user.password, password)
        ):

            login_user(user)

            flash("Welcome back!", "success")

            next_page = safe_next_url(
                request.args.get("next")
            )

            return redirect(
                next_page or url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template("login.html")


# --------------------------------------------------
# 11. GOOGLE SIGN-IN
# --------------------------------------------------

@app.route("/auth/google")
def google_login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if not os.getenv("GOOGLE_CLIENT_ID") or not os.getenv(
        "GOOGLE_CLIENT_SECRET"
    ):
        abort(
            503,
            description="Google Sign-In has not been configured yet."
        )

    redirect_uri = url_for(
        "google_callback",
        _external=True
    )

    return google.authorize_redirect(redirect_uri)


@app.route("/auth/google/callback")
def google_callback():

    try:

        token = google.authorize_access_token()

        user_info = token.get("userinfo")

        if not user_info:
            user_info = google.userinfo()

        email = user_info.get("email", "").strip().lower()

        google_id = user_info.get("sub")

        name = user_info.get("name") or email.split("@")[0]

        email_verified = user_info.get("email_verified", False)

        if not email or not google_id or not email_verified:
            flash(
                "Google account email could not be verified.",
                "error"
            )
            return redirect(url_for("login"))

        user = User.query.filter_by(
            google_id=google_id
        ).first()

        if not user:

            # Link an existing email account only when
            # Google's email has been verified.
            user = User.query.filter_by(
                email=email
            ).first()

            if user:

                user.google_id = google_id

                if not user.name:
                    user.name = name

            else:

                user = User(
                    name=name,
                    email=email,
                    google_id=google_id,
                    password=None
                )

                db.session.add(user)

            db.session.commit()

        login_user(user)

        flash("Signed in successfully with Google!", "success")

        return redirect(url_for("dashboard"))

    except Exception:

        db.session.rollback()

        app.logger.exception(
            "Google authentication failed"
        )

        flash(
            "Google Sign-In failed. Please try again.",
            "error"
        )

        return redirect(url_for("login"))


# --------------------------------------------------
# 12. LOGOUT
# --------------------------------------------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    logout_user()

    flash("You have been signed out.", "success")

    return redirect(url_for("index"))


# --------------------------------------------------
# 13. ERROR HANDLERS
# --------------------------------------------------

@app.errorhandler(413)
def file_too_large(error):

    return (
        "File is too large. Maximum upload size is 10 MB.",
        413
    )


# --------------------------------------------------
# 14. RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
