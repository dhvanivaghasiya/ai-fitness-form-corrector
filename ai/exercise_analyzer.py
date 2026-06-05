"""
Exercise Analyzer — per-exercise form checking and stage detection.

Supported exercises:
  - squat
  - pushup
  - bicep_curl

Each analyzer returns:
  {
    'stage':    'up' | 'down' | 'waiting',
    'feedback': str,
    'accuracy': float   # 0–100
  }
"""
from ai.angle_calculator import calculate_angle


# ── Thresholds ────────────────────────────────────────────────────────────────

SQUAT_THRESHOLDS = {
    'down_angle':    90,   # knee angle ≤ this → "down" position
    'up_angle':     160,   # knee angle ≥ this → "up" position
    'back_angle_ok': 160,  # hip-shoulder angle (standing) — checks back
}

PUSHUP_THRESHOLDS = {
    'down_angle':  90,    # elbow angle ≤ this → "down"
    'up_angle':   160,    # elbow angle ≥ this → "up"
    'body_angle':  160,   # hip-shoulder-ankle alignment for body straight check
}

BICEP_THRESHOLDS = {
    'up_angle':    50,    # elbow angle ≤ this → "up" (curl complete)
    'down_angle': 160,    # elbow angle ≥ this → "down" (arm extended)
}


class ExerciseAnalyzer:
    """
    Stateless per-exercise form analyzer.
    Instantiate once per exercise type, call analyze() each frame.
    """

    def __init__(self, exercise: str):
        supported = {'squat', 'pushup', 'bicep_curl'}
        if exercise not in supported:
            raise ValueError(f"Unsupported exercise '{exercise}'. Choose from {supported}")
        self.exercise = exercise
        self._prev_stage = 'waiting'

    def analyze(self, landmarks: dict) -> dict:
        """
        Analyze one frame of landmarks.

        Returns dict with 'stage', 'feedback', 'accuracy'.
        """
        dispatch = {
            'squat': self._analyze_squat,
            'pushup': self._analyze_pushup,
            'bicep_curl': self._analyze_bicep_curl,
        }
        result = dispatch[self.exercise](landmarks)
        self._prev_stage = result['stage']
        return result

    # ── Squat ─────────────────────────────────────────────────────────────────

    def _analyze_squat(self, lm: dict) -> dict:
        """
        Key joints: hip → knee → ankle (knee angle).
        Also checks torso angle (shoulder → hip → knee) for back straightness.
        """
        try:
            # Prefer left side landmarks
            hip = lm.get('left_hip') or lm.get('right_hip')
            knee = lm.get('left_knee') or lm.get('right_knee')
            ankle = lm.get('left_ankle') or lm.get('right_ankle')
            shoulder = lm.get('left_shoulder') or lm.get('right_shoulder')

            if not all([hip, knee, ankle, shoulder]):
                return {'stage': 'waiting', 'feedback': 'Stand fully in frame', 'accuracy': 0}

            knee_angle = calculate_angle(hip, knee, ankle)
            back_angle = calculate_angle(shoulder, hip, knee)

            t = SQUAT_THRESHOLDS
            stage = self._prev_stage

            # Determine stage
            if knee_angle <= t['down_angle']:
                stage = 'down'
            elif knee_angle >= t['up_angle']:
                stage = 'up'

            # Form feedback
            if back_angle < 120:
                feedback = 'Keep Your Back Straight'
                accuracy = max(0, 60 - (120 - back_angle))
            elif stage == 'down' and knee_angle > t['down_angle']:
                feedback = 'Go Lower'
                accuracy = max(0, 70 - (knee_angle - t['down_angle']))
            elif stage == 'up' or stage == 'waiting':
                feedback = 'Ready — Begin Squat'
                accuracy = 85
            else:
                # Ideal down position
                depth_bonus = max(0, (t['down_angle'] - knee_angle) / t['down_angle']) * 20
                accuracy = min(100, 80 + depth_bonus)
                feedback = 'Correct Form ✓'

            return {'stage': stage, 'feedback': feedback, 'accuracy': round(accuracy, 1)}

        except Exception:
            return {'stage': 'waiting', 'feedback': 'Analyzing...', 'accuracy': 0}

    # ── Pushup ────────────────────────────────────────────────────────────────

    def _analyze_pushup(self, lm: dict) -> dict:
        """
        Key joints: shoulder → elbow → wrist (elbow angle).
        Also checks shoulder → hip → ankle for body alignment.
        """
        try:
            shoulder = lm.get('left_shoulder') or lm.get('right_shoulder')
            elbow = lm.get('left_elbow') or lm.get('right_elbow')
            wrist = lm.get('left_wrist') or lm.get('right_wrist')
            hip = lm.get('left_hip') or lm.get('right_hip')
            ankle = lm.get('left_ankle') or lm.get('right_ankle')

            if not all([shoulder, elbow, wrist]):
                return {'stage': 'waiting', 'feedback': 'Get into push-up position', 'accuracy': 0}

            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            t = PUSHUP_THRESHOLDS
            stage = self._prev_stage

            if elbow_angle <= t['down_angle']:
                stage = 'down'
            elif elbow_angle >= t['up_angle']:
                stage = 'up'

            # Body alignment check
            body_straight = True
            body_angle = 180
            if hip and ankle:
                body_angle = calculate_angle(shoulder, hip, ankle)
                body_straight = body_angle >= t['body_angle']

            if not body_straight:
                feedback = 'Keep Body Straight'
                accuracy = max(0, 60 - (t['body_angle'] - body_angle) * 0.5)
            elif stage == 'down' and elbow_angle > t['down_angle']:
                feedback = 'Go Lower'
                accuracy = max(0, 65 - (elbow_angle - t['down_angle']))
            elif stage == 'up' and elbow_angle < t['up_angle']:
                feedback = 'Arms Not Fully Extended'
                accuracy = max(0, 70 - (t['up_angle'] - elbow_angle))
            elif stage == 'waiting' or stage == 'up':
                feedback = 'Ready — Begin Push-up'
                accuracy = 85
            else:
                accuracy = min(100, 80 + (t['down_angle'] - elbow_angle) * 0.3)
                feedback = 'Correct Form ✓'

            return {'stage': stage, 'feedback': feedback, 'accuracy': round(accuracy, 1)}

        except Exception:
            return {'stage': 'waiting', 'feedback': 'Analyzing...', 'accuracy': 0}

    # ── Bicep Curl ────────────────────────────────────────────────────────────

    def _analyze_bicep_curl(self, lm: dict) -> dict:
        """
        Key joints: shoulder → elbow → wrist (elbow angle).
        Up: arm curled (small angle). Down: arm extended (large angle).
        """
        try:
            shoulder = lm.get('left_shoulder') or lm.get('right_shoulder')
            elbow = lm.get('left_elbow') or lm.get('right_elbow')
            wrist = lm.get('left_wrist') or lm.get('right_wrist')

            if not all([shoulder, elbow, wrist]):
                return {'stage': 'waiting', 'feedback': 'Stand with arm visible', 'accuracy': 0}

            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            t = BICEP_THRESHOLDS
            stage = self._prev_stage

            if elbow_angle <= t['up_angle']:
                stage = 'up'
            elif elbow_angle >= t['down_angle']:
                stage = 'down'

            if stage == 'down' and elbow_angle < t['down_angle']:
                feedback = 'Fully Extend Your Arm'
                accuracy = max(0, 70 - (t['down_angle'] - elbow_angle) * 0.5)
            elif stage == 'up' and elbow_angle > t['up_angle']:
                feedback = 'Curl Higher'
                accuracy = max(0, 60 - (elbow_angle - t['up_angle']) * 0.8)
            elif stage == 'waiting':
                feedback = 'Ready — Begin Curl'
                accuracy = 85
            else:
                accuracy = min(100, 85 + (t['up_angle'] - elbow_angle) * 0.3) if stage == 'up' else 82
                feedback = 'Correct Form ✓'

            return {'stage': stage, 'feedback': feedback, 'accuracy': round(accuracy, 1)}

        except Exception:
            return {'stage': 'waiting', 'feedback': 'Analyzing...', 'accuracy': 0}
