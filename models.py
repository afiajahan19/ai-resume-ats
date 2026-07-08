from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ResumeAnalysis(db.Model):

    __tablename__ = "resume_analysis"

    id = db.Column(db.Integer, primary_key=True)

    resume_name = db.Column(db.String(200), nullable=False)

    ats_score = db.Column(db.Integer, nullable=False)

    matched_skills = db.Column(db.Text)

    missing_skills = db.Column(db.Text)

    job_description = db.Column(db.Text)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ResumeAnalysis {self.resume_name}>"