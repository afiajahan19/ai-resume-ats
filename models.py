from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    # Stores the securely hashed password
    password = db.Column(db.String(255), nullable=True)

    google_id = db.Column(
        db.String(255),
        unique=True,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    analyses = db.relationship(
        "ResumeAnalysis",
        backref="user",
        lazy=True
    )


class ResumeAnalysis(db.Model):

    __tablename__ = "resume_analysis"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    resume_name = db.Column(db.String(200), nullable=False)

    ats_score = db.Column(db.Integer, nullable=False)

    matched_skills = db.Column(db.Text)

    missing_skills = db.Column(db.Text)

    job_description = db.Column(db.Text)

    uploaded_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<ResumeAnalysis {self.resume_name}>"
