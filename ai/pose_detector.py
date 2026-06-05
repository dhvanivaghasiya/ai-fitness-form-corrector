"""
Pose Detector — wraps MediaPipe Pose for landmark extraction.
Returns normalized landmarks and an annotated (drawn) frame.
"""
import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class PoseDetector:
    """
    Singleton-friendly MediaPipe Pose wrapper.
    Call detect(frame) to get landmarks + annotated BGR frame.
    """

    def __init__(self, min_detection_confidence: float = 0.7,
                 min_tracking_confidence: float = 0.7):
        self.pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def detect(self, frame: np.ndarray):
        """
        Run pose detection on a BGR frame.

        Returns:
            landmarks (dict | None): landmark name → (x, y) normalised coords
            annotated_frame (np.ndarray): frame with skeleton drawn
        """
        # MediaPipe needs RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.pose.process(rgb)
        rgb.flags.writeable = True

        annotated = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        if not results.pose_landmarks:
            return None, annotated

        # Draw landmarks with a clean, subtle style
        mp_drawing.draw_landmarks(
            annotated,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(
                color=(37, 99, 235), thickness=2, circle_radius=3   # blue-600
            ),
            connection_drawing_spec=mp_drawing.DrawingSpec(
                color=(148, 163, 184), thickness=2                   # slate-400
            ),
        )

        # Build landmark dict: name → (x, y)
        h, w = frame.shape[:2]
        landmarks = {}
        for idx, lm in enumerate(results.pose_landmarks.landmark):
            name = mp_pose.PoseLandmark(idx).name.lower()
            landmarks[name] = (lm.x, lm.y)

        return landmarks, annotated
