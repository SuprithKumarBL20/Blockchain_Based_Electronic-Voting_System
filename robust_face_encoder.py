import cv2
import numpy as np
import base64
from typing import Optional, List, Tuple
import json
import os
from pathlib import Path

class RobustFaceEncoder:
    """Enhanced face encoder with robust handling of different image formats and qualities"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
    def normalize_image_size(self, image: np.ndarray, target_size: Tuple[int, int] = (160, 160)) -> np.ndarray:
        """Normalize image to standard size while maintaining aspect ratio"""
        h, w = image.shape[:2]
        target_h, target_w = target_size
        
        # Calculate scaling factor
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Create canvas with target size and center the image
        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        
        # Calculate padding to center the image
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        
        # Place resized image on canvas
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
        
        return canvas
    
    def enhance_image_quality(self, image: np.ndarray) -> np.ndarray:
        """Enhance image quality for better face recognition"""
        # Convert to LAB color space for better contrast enhancement
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        # Apply slight Gaussian blur to reduce noise
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        return enhanced
    
    def detect_and_extract_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Strict face detection and extraction with security validation"""
        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply histogram equalization
        gray_equalized = cv2.equalizeHist(gray)
        
        # SECURITY: Use strict detection parameters first
        faces = self.face_cascade.detectMultiScale(gray_equalized, 1.05, 6)  # Strict: scaleFactor=1.05, minNeighbors=6
        
        # If no faces found, try slightly more lenient but still secure
        if len(faces) == 0:
            faces = self.face_cascade.detectMultiScale(gray_equalized, 1.1, 5)  # minNeighbors=5
        
        if len(faces) == 0:
            print("SECURITY ALERT: No valid face detected with secure parameters")
            return None
        
        # Select the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        
        # SECURITY CHECK: Ensure face is reasonably sized
        face_area = w * h
        image_area = image.shape[0] * image.shape[1]
        face_ratio = face_area / image_area
        
        if face_ratio < 0.05:  # Face too small (less than 5% of image)
            print(f"SECURITY ALERT: Face too small - ratio: {face_ratio}")
            return None
        
        if face_ratio > 0.8:  # Face too large (more than 80% of image)
            print(f"SECURITY ALERT: Face too large - ratio: {face_ratio}")
            return None
        
        # SECURITY CHECK: Ensure reasonable face dimensions
        if w < 60 or h < 60:  # Minimum face size
            print(f"SECURITY ALERT: Face dimensions too small - {w}x{h}")
            return None
        
        # Add padding around the face
        padding = min(w, h) // 8  # Reduced padding for better accuracy
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)
        
        # Extract face region
        face = image[y1:y2, x1:x2]
        
        if face.size == 0:
            return None
        
        # Ensure minimum face size for feature extraction
        if face.shape[0] < 80 or face.shape[1] < 80:
            face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_CUBIC)
        
        return face
    
    def extract_face_features(self, face: np.ndarray) -> List[float]:
        """Extract robust facial features"""
        # Normalize face size
        normalized_face = self.normalize_image_size(face, (160, 160))
        
        # Enhance quality
        enhanced_face = self.enhance_image_quality(normalized_face)
        
        # Convert to grayscale for feature extraction
        gray = cv2.cvtColor(enhanced_face, cv2.COLOR_BGR2GRAY)
        
        # Extract multiple types of features
        features = []
        
        # 1. Raw pixel values (normalized)
        flat_pixels = gray.flatten() / 255.0
        features.extend(flat_pixels[:256])  # Use first 256 pixels as representative sample
        
        # 2. Histogram features
        hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
        hist = hist.flatten() / hist.sum()  # Normalize
        features.extend(hist)
        
        # 3. Edge features using Sobel operators
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        
        # Sample edge features
        edge_sample = sobel_magnitude.flatten()[::100]  # Every 100th pixel
        if len(edge_sample) > 64:
            edge_sample = edge_sample[:64]
        edge_features = edge_sample / np.max(edge_sample) if np.max(edge_sample) > 0 else edge_sample
        features.extend(edge_features)
        
        # 4. Texture features (Local Binary Pattern approximation)
        # Simple texture measure using standard deviation in small windows
        texture_features = []
        for i in range(0, gray.shape[0], 20):
            for j in range(0, gray.shape[1], 20):
                window = gray[i:i+20, j:j+20]
                if window.size > 0:
                    texture_features.append(np.std(window))
        
        # Normalize texture features
        if texture_features:
            texture_features = np.array(texture_features)
            texture_features = texture_features / np.max(texture_features) if np.max(texture_features) > 0 else texture_features
            features.extend(texture_features[:32])  # Limit to 32 features
        
        # Pad or truncate to ensure consistent length (512 features)
        target_length = 512
        if len(features) < target_length:
            # Pad with zeros
            features.extend([0.0] * (target_length - len(features)))
        elif len(features) > target_length:
            # Truncate
            features = features[:target_length]
        
        return features
    
    def compare_faces(self, embedding1: List[float], embedding2: List[float], threshold: float = 0.6) -> Tuple[bool, float]:
        """Compare two face embeddings with multiple similarity metrics"""
        
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # 1. Cosine similarity
        cosine_sim = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        
        # 2. Euclidean distance (normalized)
        euclidean_dist = np.linalg.norm(vec1 - vec2) / np.sqrt(len(vec1))
        
        # 3. Correlation coefficient
        correlation = np.corrcoef(vec1, vec2)[0, 1] if len(vec1) > 1 else 0
        
        # Combined similarity score (weighted average)
        # Higher cosine similarity and correlation are better
        # Lower euclidean distance is better
        similarity_score = (
            0.5 * cosine_sim +
            0.3 * (1 - euclidean_dist) +  # Convert distance to similarity
            0.2 * correlation
        )
        
        # Convert to distance (0 = identical, 1 = completely different)
        distance = 1 - similarity_score
        
        is_match = distance < threshold
        
        return is_match, distance
    
    def verify_face_from_image(self, stored_embedding: List[float], image_data: str, threshold: float = 0.4) -> Tuple[bool, float]:
        """Verify face from uploaded image with strict security checks"""
        
        try:
            # Handle data URL format
            if ',' in image_data:
                header, data = image_data.split(',', 1)
                print(f"Processing image with header: {header}")
            else:
                data = image_data
            
            # Decode base64 image
            image_bytes = base64.b64decode(data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                print("Failed to decode image from base64")
                return False, 1.0
            
            print(f"Loaded image: {image.shape}")
            
            # CRITICAL SECURITY CHECK: Ensure a valid face is detected
            face = self.detect_and_extract_face(image)
            if face is None:
                print("SECURITY ALERT: No valid face detected in uploaded image")
                return False, 1.0
            
            # Extract features from the detected face
            features = self.extract_face_features(face)
            if not features:
                print("SECURITY ALERT: Failed to extract valid face features")
                return False, 1.0
            
            # Compare faces with strict threshold
            is_match, distance = self.compare_faces(stored_embedding, features, threshold)
            
            # Additional security check: ensure the distance is reasonable
            if distance > 0.5:  # Additional safety margin
                print(f"SECURITY ALERT: Face similarity too low - Distance: {distance}")
                return False, distance
            
            print(f"Face verification result - Match: {is_match}, Distance: {distance}")
            return is_match, distance
            
        except Exception as e:
            print(f"Error in face verification: {e}")
            return False, 1.0
    
    def save_face_image(self, image_data: str, filename: str = None) -> Optional[str]:
        """Save face image from base64 data"""
        try:
            if not filename:
                import uuid
                filename = f"face_{uuid.uuid4().hex}.jpg"
            
            # Decode base64 image
            if ',' in image_data:
                header, data = image_data.split(',', 1)
            else:
                data = image_data
            
            image_bytes = base64.b64decode(data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None
            
            # Detect face
            face = self.detect_and_extract_face(image)
            if face is None:
                return None
            
            # Save face image
            filepath = f"static/images/faces/{filename}"
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            cv2.imwrite(filepath, face)
            
            return filepath
            
        except Exception as e:
            print(f"Error saving face image: {e}")
            return None

    def get_face_embedding(self, image: np.ndarray) -> Optional[List[float]]:
        """Extract face embedding from image"""
        try:
            face = self.detect_and_extract_face(image)
            if face is not None:
                return self.extract_face_features(face)
            return None
        except Exception as e:
            print(f"Error extracting face embedding: {e}")
            return None