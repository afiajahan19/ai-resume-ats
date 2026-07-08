from flask import Flask, render_template, request
from dotenv import load_dotenv
import os

from utils import extract_text, analyze
from models import db, ResumeAnalysis

# Load environment variables
load_dotenv()

app = Flask(__name__)

# PostgreSQL Connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
db.init_app(app)

# Create Tables
with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():

    result = None

    if request.method == "POST":

        f = request.files["resume"]
        jd = request.form["job_description"]

        path = "uploads/" + f.filename
        f.save(path)

        resume = extract_text(path)

        result = analyze(resume, jd)

        # Save to Database
        analysis = ResumeAnalysis(
            resume_name=f.filename,
            ats_score=result["score"],
            matched_skills=", ".join(result["matched"]),
            missing_skills=", ".join(result["missing"]),
            job_description=jd
        )

        db.session.add(analysis)
        db.session.commit()

    return render_template("index.html", result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)