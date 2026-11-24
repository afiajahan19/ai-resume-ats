
from flask import Flask, render_template, request
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from utils import extract_text, analyze
from models import db, ResumeAnalysis
from sqlalchemy import func
from datetime import datetime
import os
import uuid

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "evaluate-pro-local-key")
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

database_url = os.getenv("DATABASE_URL")

if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql://", 1
    )

app.config["SQLALCHEMY_DATABASE_URI"] = database_url

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db.init_app(app)

with app.app_context():
    db.create_all()


def get_dashboard_data():
    total_screenings = ResumeAnalysis.query.count()

    average_score = db.session.query(
        func.avg(ResumeAnalysis.ats_score)
    ).scalar()

    strong_matches = ResumeAnalysis.query.filter(
        ResumeAnalysis.ats_score >= 70
    ).count()

    recent_analyses = ResumeAnalysis.query.order_by(
        ResumeAnalysis.uploaded_at.desc()
    ).limit(5).all()

    history_records = ResumeAnalysis.query.order_by(
        ResumeAnalysis.uploaded_at.desc()
    ).all()

    return {
        "total_screenings": total_screenings,
        "average_score": round(float(average_score or 0)),
        "strong_matches": strong_matches,
        "recent_analyses": recent_analyses,
        "history_records": history_records
    }


@app.route("/", methods=["GET", "POST"])
def index():

    result = None
    error_message = None

    if request.method == "POST":

        uploaded_file = request.files.get("resume")
        job_description = request.form.get(
            "job_description", ""
        ).strip()

        if not uploaded_file or uploaded_file.filename == "":
            error_message = "Please select a resume file."

        elif not job_description:
            error_message = "Please enter a job description."

        else:
            original_name = secure_filename(uploaded_file.filename)
            extension = original_name.rsplit(".", 1)[-1].lower()

            if extension not in {"pdf", "docx"}:
                error_message = "Please upload a PDF or DOCX resume."

            else:
                unique_name = f"{uuid.uuid4().hex}_{original_name}"
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

                    result = analyze(resume_text, job_description)

                    analysis = ResumeAnalysis(
                        resume_name=original_name,
                        ats_score=result["score"],
                        matched_skills=", ".join(result["matched"]),
                        missing_skills=", ".join(result["missing"]),
                        job_description=job_description
                    )

                    db.session.add(analysis)
                    db.session.commit()

                except Exception as error:
                    db.session.rollback()
                    app.logger.exception("Resume analysis failed")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
