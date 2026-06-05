"""
Dashboard routes — main page, stats API, history API.
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from backend.models.session import WorkoutSession
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Render the main dashboard."""
    return render_template('dashboard.html', now=datetime.utcnow())


@dashboard_bp.route('/api/stats')
@login_required
def stats():
    """Return aggregate workout statistics for the current user."""
    sessions = WorkoutSession.query.filter_by(user_id=current_user.id).all()

    total_reps = sum(s.reps for s in sessions)
    total_sessions = len(sessions)
    total_calories = round(sum(s.calories_burned for s in sessions), 1)
    avg_accuracy = round(
        sum(s.accuracy_score for s in sessions) / total_sessions, 1
    ) if total_sessions > 0 else 0

    # Streak: consecutive days with at least one session
    streak = _calculate_streak(sessions)

    # Last 7 days reps per day
    week_data = _weekly_reps(sessions)

    # Exercise breakdown
    breakdown = {}
    for s in sessions:
        breakdown[s.exercise_type] = breakdown.get(s.exercise_type, 0) + s.reps

    return jsonify({
        'total_reps': total_reps,
        'total_sessions': total_sessions,
        'total_calories': total_calories,
        'avg_accuracy': avg_accuracy,
        'streak': streak,
        'week_labels': week_data['labels'],
        'week_reps': week_data['reps'],
        'exercise_breakdown': breakdown,
    })


@dashboard_bp.route('/api/history')
@login_required
def history():
    """Return the last 20 workout sessions for the current user."""
    sessions = (
        WorkoutSession.query
        .filter_by(user_id=current_user.id)
        .order_by(WorkoutSession.created_at.desc())
        .limit(20)
        .all()
    )
    return jsonify([s.to_dict() for s in sessions])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _calculate_streak(sessions):
    """Count consecutive days (ending today) that have at least one session."""
    if not sessions:
        return 0
    session_dates = {s.created_at.date() for s in sessions}
    streak = 0
    today = datetime.utcnow().date()
    day = today
    while day in session_dates:
        streak += 1
        day -= timedelta(days=1)
    return streak


def _weekly_reps(sessions):
    """Aggregate reps by day for the last 7 days."""
    today = datetime.utcnow().date()
    labels = []
    reps = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_reps = sum(s.reps for s in sessions if s.created_at.date() == day)
        labels.append(day.strftime('%a'))
        reps.append(day_reps)
    return {'labels': labels, 'reps': reps}
