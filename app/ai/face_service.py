from math import dist

import cv2
import dlib
import face_recognition
import numpy as np


class FaceAIService:
    """AI helper for face matching and blink liveness checks."""

    def __init__(self, shape_predictor_path: str = "shape_predictor_68_face_landmarks.dat"):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(shape_predictor_path)

    @staticmethod
    def compare_embeddings(stored: list[float], candidate: list[float], threshold: float = 0.45) -> bool:
        return dist(stored, candidate) < threshold

    @staticmethod
    def eye_aspect_ratio(eye_points: np.ndarray) -> float:
        a = np.linalg.norm(eye_points[1] - eye_points[5])
        b = np.linalg.norm(eye_points[2] - eye_points[4])
        c = np.linalg.norm(eye_points[0] - eye_points[3])
        return (a + b) / (2.0 * c)

    def detect_blink(self, frame_bgr: np.ndarray, ear_threshold: float = 0.21) -> bool:
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        for face in faces:
            landmarks = self.predictor(gray, face)
            coords = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)])
            left_ear = self.eye_aspect_ratio(coords[42:48])
            right_ear = self.eye_aspect_ratio(coords[36:42])
            if (left_ear + right_ear) / 2 < ear_threshold:
                return True
        return False

    @staticmethod
    def embedding_from_rgb_image(rgb_frame: np.ndarray) -> list[float] | None:
        encodings = face_recognition.face_encodings(rgb_frame)
        if not encodings:
            return None
        return encodings[0].tolist()
