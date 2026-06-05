"""
Workout routes — webcam frame analysis, session save, workout page.
"""
import base64
import numpy as np
import cv2
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from config import Config
from backend.models import db
from backend.models.session import WorkoutSession
from ai.pose_detector import PoseDetector
from ai.exercise_analyzer import ExerciseAnalyzer
from ai.rep_counter import RepCounter

workout_bp = Blueprint('workout', __name__)

# One detector per process (shared across requests — MediaPipe is thread-safe for reads)
_pose_detector = PoseDetector()

# Per-user state: {user_id: {'counter': RepCounter, 'analyzer': ExerciseAnalyzer, 'exercise': str}}
_user_state: dict = {}


def _get_state(user_id: int, exercise: str):
    """Return (or create) per-user exercise state."""
    key = (user_id, exercise)
    if key not in _user_state:
        _user_state[key] = {
            'counter': RepCounter(),
            'analyzer': ExerciseAnalyzer(exercise),
        }
    return _user_state[key]


@workout_bp.route('/')
@login_required
def index():
    """Render the workout / webcam page."""
    return render_template('workout.html')


@workout_bp.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    """
    Receive a base64-encoded JPEG frame from the browser.
    Run MediaPipe pose detection + exercise analysis.
    Return rep count, feedback, accuracy, and annotated frame.
    """
    data = request.get_json(silent=True)
    if not data or 'frame' not in data:
        return jsonify({'error': 'No frame provided'}), 400

    exercise = data.get('exercise', 'squat').lower()

    # --- Decode base64 image ---
    try:
        img_data = base64.b64decode(data['frame'].split(',')[-1])
        np_arr = np.frombuffer(img_data, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({'error': f'Frame decode error: {str(e)}'}), 400

    if frame is None:
        return jsonify({'error': 'Invalid image data'}), 400

    # --- Pose detection ---
    landmarks, annotated_frame = _pose_detector.detect(frame)

    if landmarks is None:
        return jsonify({
            'reps': _get_state(current_user.id, exercise)['counter'].reps,
            'feedback': 'Stand in frame',
            'accuracy': 0,
            'stage': 'waiting',
            'frame': _encode_frame(annotated_frame),
        })

    # --- Exercise analysis ---
    state = _get_state(current_user.id, exercise)
    result = state['analyzer'].analyze(landmarks)
    state['counter'].update(result['stage'])

    return jsonify({
        'reps': state['counter'].reps,
        'feedback': result['feedback'],
        'accuracy': result['accuracy'],
        'stage': result['stage'],
        'frame': _encode_frame(annotated_frame),
    })


@workout_bp.route('/api/reset', methods=['POST'])
@login_required
def reset():
    """Reset the rep counter for a given exercise."""
    data = request.get_json(silent=True) or {}
    exercise = data.get('exercise', 'squat').lower()
    key = (current_user.id, exercise)
    if key in _user_state:
        del _user_state[key]
    return jsonify({'status': 'ok'})


@workout_bp.route('/api/save', methods=['POST'])
@login_required
def save_session():
    """Save a completed workout session to the database."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    exercise = data.get('exercise', 'squat').lower()
    reps = int(data.get('reps', 0))
    accuracy = float(data.get('accuracy', 0))
    duration = int(data.get('duration', 0))

    calories = reps * Config.CALORIES_PER_REP.get(exercise, 0.25)

    session = WorkoutSession(
        user_id=current_user.id,
        exercise_type=exercise,
        reps=reps,
        accuracy_score=accuracy,
        calories_burned=round(calories, 2),
        duration_seconds=duration,
    )
    db.session.add(session)
    db.session.commit()

    # Clear in-memory state after saving
    key = (current_user.id, exercise)
    if key in _user_state:
        del _user_state[key]

    return jsonify({'status': 'saved', 'session': session.to_dict()})


def _encode_frame(frame: np.ndarray) -> str:
    """Encode a numpy frame to base64 JPEG string."""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
    return 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode('utf-8')
