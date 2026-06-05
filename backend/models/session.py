"""
WorkoutSession model — stores completed exercise sessions.
"""
from backend.models import db
from datetime import datetime


class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    exercise_type = db.Column(db.String(50), nullable=False)   # 'squat', 'pushup', 'bicep_curl'
    reps = db.Column(db.Integer, default=0)
    accuracy_score = db.Column(db.Float, default=0.0)          # 0-100 percentage
    calories_burned = db.Column(db.Float, default=0.0)
    duration_seconds = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Serialize session to JSON-safe dict."""
        return {
            'id': self.id,
            'exercise_type': self.exercise_type,
            'exercise_label': self.exercise_type.replace('_', ' ').title(),
            'reps': self.reps,
            'accuracy_score': round(self.accuracy_score, 1),
            'calories_burned': round(self.calories_burned, 1),
            'duration_seconds': self.duration_seconds,
            'created_at': self.created_at.strftime('%b %d, %Y %H:%M'),
            'date_short': self.created_at.strftime('%b %d'),
        }

    def __repr__(self):
        return f'<WorkoutSession {self.exercise_type} {self.reps} reps>'
