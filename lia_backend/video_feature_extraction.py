import cv2
import numpy as np
from deepface import DeepFace
import mediapipe as mp
import time
from collections import deque, Counter
import os

def update_video_features(interview_instance, video_file, answer_num):
    """Process video file and extract features"""
    
    # Save the video file temporarily
    temp_path = f"/tmp/temp_video_{answer_num}.webm"
    video_file.save(temp_path)
    
    # Initialize MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Initialize variables
    total_frames = 0
    blink_count = 0
    smile_intensities = []
    gaze_directions = []
    engagement_scores = []
    stress_scores = []
    emotions = []
    
    try:
        # Read video file
        cap = cv2.VideoCapture(temp_path)
        if not cap.isOpened():
            raise Exception("Failed to open video file")
            
        # Process frames
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            total_frames += 1
            
            # Process frame with MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = mp_face_mesh.process(rgb_frame)
            
            if results.multi_face_landmarks:
                landmarks = np.array([[lm.x * frame.shape[1], lm.y * frame.shape[0]] 
                                    for lm in results.multi_face_landmarks[0].landmark])
                
                # Extract features
                ear = calculate_eye_aspect_ratio(landmarks)
                mar = calculate_mouth_aspect_ratio(landmarks)
                gaze = calculate_gaze_direction(landmarks, frame.shape[1])
                
                # Update metrics
                if ear < 0.25:  # Blink threshold
                    blink_count += 1
                
                smile_intensities.append(calculate_smile_intensity(mar))
                gaze_directions.append(gaze)
                
                # Calculate engagement score
                engagement_score = 0
                if gaze == "Looking Center":
                    engagement_score += 1
                if mar > 0.3:
                    engagement_score += 1
                engagement_scores.append(engagement_score)
                
                # Perform emotion analysis every 30 frames
                if total_frames % 30 == 0:
                    try:
                        emotion_analysis = DeepFace.analyze(
                            frame,
                            actions=['emotion'],
                            enforce_detection=False,
                            silent=True
                        )[0]
                        emotions.append(emotion_analysis['dominant_emotion'])
                        
                        # Update stress score based on emotion
                        stress_score = 1 if emotion_analysis['dominant_emotion'] in ['angry', 'fear', 'sad'] else 0
                        stress_scores.append(stress_score)
                    except Exception as e:
                        print(f"DeepFace analysis error: {str(e)}")
    
        # Calculate final metrics
        metrics = {
            'total_frames': total_frames,
            'blink_rate': blink_count / (total_frames / 30),  # Blinks per second
            'average_smile_intensity': np.mean(smile_intensities) if smile_intensities else 0,
            'gaze_distribution': Counter(gaze_directions),
            'average_engagement': np.mean(engagement_scores) if engagement_scores else 0,
            'average_stress': np.mean(stress_scores) if stress_scores else 0,
            'emotion_distribution': Counter(emotions)
        }
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        # Return default metrics if processing fails
        metrics = {
            'total_frames': 0,
            'blink_rate': 0,
            'average_smile_intensity': 0,
            'gaze_distribution': Counter(),
            'average_engagement': 0,
            'average_stress': 0,
            'emotion_distribution': Counter()
        }
    
    finally:
        # Cleanup
        if 'cap' in locals():
            cap.release()
        mp_face_mesh.close()
        
        # Remove temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    # Update interview instance
    if not hasattr(interview_instance, 'video_features'):
        interview_instance.video_features = []
    
    while len(interview_instance.video_features) <= answer_num:
        interview_instance.video_features.append({})
    
    interview_instance.video_features[answer_num] = metrics
    
    return metrics

def calculate_eye_aspect_ratio(landmarks):
    # Implementation of eye aspect ratio calculation
    # Using specific landmark indices for eyes
    left_eye = landmarks[[33, 160, 158, 133, 153, 144]]
    right_eye = landmarks[[263, 387, 385, 362, 380, 373]]
    
    def eye_ratio(eye):
        # Compute vertical distances
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        # Compute horizontal distance
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)
    
    return (eye_ratio(left_eye) + eye_ratio(right_eye)) / 2

def calculate_mouth_aspect_ratio(landmarks):
    # Using specific landmark indices for mouth
    mouth_points = landmarks[[13, 14, 78, 95, 78, 308]]
    
    # Vertical distances
    A = np.linalg.norm(mouth_points[0] - mouth_points[1])
    B = np.linalg.norm(mouth_points[2] - mouth_points[3])
    
    # Horizontal distance
    C = np.linalg.norm(mouth_points[4] - mouth_points[5])
    
    return (A + B) / (2.0 * C)

def calculate_smile_intensity(mar):
    # Convert MAR to smile intensity (0-100)
    threshold = 0.05
    max_mar = 0.15
    normalized = max(0, min(1, (mar - threshold) / (max_mar - threshold)))
    return normalized * 100

def calculate_gaze_direction(landmarks, frame_width):
    # Calculate average eye positions
    left_eye = np.mean(landmarks[[33, 160, 158, 133, 153, 144]], axis=0)
    right_eye = np.mean(landmarks[[263, 387, 385, 362, 380, 373]], axis=0)
    
    # Define regions
    left_region = frame_width * 0.48
    right_region = frame_width * 0.52
    
    if left_eye[0] < left_region and right_eye[0] < left_region:
        return "Looking Left"
    elif left_eye[0] > right_region and right_eye[0] > right_region:
        return "Looking Right"
    return "Looking Center"