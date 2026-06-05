"""
Angle Calculator — compute joint angles from MediaPipe landmarks.
Uses arctan2 for robust angle calculation at any orientation.
"""
import numpy as np


def calculate_angle(a: tuple, b: tuple, c: tuple) -> float:
    """
    Calculate the angle (in degrees) at joint B formed by points A–B–C.

    Args:
        a: (x, y) of the first point  (e.g. hip)
        b: (x, y) of the vertex joint (e.g. knee)
        c: (x, y) of the third point  (e.g. ankle)

    Returns:
        Angle in degrees [0, 180].
    """
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    ba = a - b
    bc = c - b

    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosine = np.clip(cosine, -1.0, 1.0)
    angle = np.degrees(np.arccos(cosine))
    return float(angle)


def get_landmark_pair(landmarks: dict, name: str):
    """
    Return (x, y) for a named landmark, or None if not present.
    Tries left side first, falls back to right side if needed.
    """
    return landmarks.get(name)
