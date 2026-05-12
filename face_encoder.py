import cv2
import numpy as np
import json
import os
from PIL import Image
import io
import base64
from typing import List, Optional, Tuple
import uuid

# Try to import onnxruntime, but provide fallback if not available
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    print("Warning: ONNX Runtime not available. Using fallback face detection.")
    ONNX_AVAILABLE = False

class FaceEncoder:
    def __init__(self, model_path: str = 'ai/model.onnx'):
        self.model_path = model_path
        self.session = None
        self.input_name = None
        self.output_name = None
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Model input size (adjust based on your ONNX model)
        self.input_size = (112, 112)
        self.embedding_size = 512  # Adjust based on your model
        
        self.load_model()
    
    def load_model(self):
        """Load the ONNX model"""
        try:
            if ONNX_AVAILABLE and os.path.exists(self.model_path):
                self.session = ort.InferenceSession(self.model_path)
                self.input_name = self.session.get_inputs()[0].name
                self.output_name = self.session.get_outputs()[0].name
                print(f"Face recognition model loaded from {self.model_path}")
            else:
                print(f"Warning: ONNX model not available or not found at {self.model_path}")
                print("Using fallback face detection only")
        except Exception as e:
            print(f"Error loading ONNX model: {e}")
            print("Using fallback face detection only")
    
    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect and extract face from image with enhanced preprocessing"""
        try:
            # Convert to grayscale for better face detection
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization for better contrast
            gray_equalized = cv2.equalizeHist(gray)
            
            # Try multiple detection scales for better accuracy
            faces = []
            for scale in [1.1, 1.05, 1.15]:
                faces = self.face_cascade.detectMultiScale(gray_equalized, scale, 4)
                if len(faces) > 0:
                    break
            
            if len(faces) == 0:
                # Try with original image if equalized version fails
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
                if len(faces) == 0:
                    return None
            
            # Take the largest face (most likely to be the main subject)
            largest_face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = largest_face
            
            # Extract face with adaptive padding based on face size
            padding = min(w, h) // 4  # Adaptive padding based on face dimensions
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(image.shape[1], x + w + padding)
            y2 = min(image.shape[0], y + h + padding)
            
            face = image[y1:y2, x1:x2]
            
            # Apply additional preprocessing for better quality
            if face.size > 0:
                # Ensure minimum face size for quality
                if face.shape[0] < 50 or face.shape[1] < 50:
                    # Upscale small faces
                    scale_factor = max(100 / face.shape[0], 100 / face.shape[1])
                    new_width = int(face.shape[1] * scale_factor)
                    new_height = int(face.shape[0] * scale_factor)
                    face = cv2.resize(face, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            return face
        except Exception as e:
            print(f"Error in face detection: {e}")
            return None
    
    def preprocess_face(self, face_image: np.ndarray) -> np.ndarray:
        """Preprocess face image for model input with enhanced quality improvements"""
        try:
            # Convert to RGB if needed
            if len(face_image.shape) == 2:  # Grayscale
                face_image = cv2.cvtColor(face_image, cv2.COLOR_GRAY2BGR)
            elif face_image.shape[2] == 4:  # RGBA
                face_image = cv2.cvtColor(face_image, cv2.COLOR_RGBA2BGR)
            
            # Apply histogram equalization for better lighting
            lab = cv2.cvtColor(face_image, cv2.COLOR_BGR2LAB)
            lab[:,:,0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(lab[:,:,0])
            face_enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            # Apply Gaussian blur to reduce noise
            face_blurred = cv2.GaussianBlur(face_enhanced, (3, 3), 0)
            
            # Resize to model input size using high-quality interpolation
            face_resized = cv2.resize(face_blurred, self.input_size, interpolation=cv2.INTER_AREA)
            
            # Normalize pixel values
            face_normalized = face_resized.astype(np.float32) / 255.0
            
            # Add batch dimension and transpose to NCHW format
            face_preprocessed = np.transpose(face_normalized, (2, 0, 1))
            face_preprocessed = np.expand_dims(face_preprocessed, axis=0)
            
            return face_preprocessed
        except Exception as e:
            print(f"Error preprocessing face: {e}")
            return None
    
    def get_face_embedding(self, image: np.ndarray) -> Optional[List[float]]:
        """Extract face embedding from image"""
        try:
            # Detect face
            face = self.detect_face(image)
            if face is None:
                return None
            
            # If ONNX model is available, use it
            if self.session is not None:
                preprocessed_face = self.preprocess_face(face)
                if preprocessed_face is None:
                    return None
                
                # Get embedding
                embedding = self.session.run([self.output_name], {self.input_name: preprocessed_face})[0]
                return embedding.flatten().tolist()
            else:
                # Enhanced Fallback: Use more robust face features for uploaded photos
                face_resized = cv2.resize(face, (112, 112))
                
                # Apply histogram equalization for better lighting
                lab = cv2.cvtColor(face_resized, cv2.COLOR_BGR2LAB)
                lab[:,:,0] = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(lab[:,:,0])
                face_enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                
                # Convert to different color spaces for better feature extraction
                gray = cv2.cvtColor(face_enhanced, cv2.COLOR_BGR2GRAY)
                hsv = cv2.cvtColor(face_enhanced, cv2.COLOR_BGR2HSV)
                
                # Extract multiple types of features
                features = []
                
                # 1. Raw pixel intensities (normalized)
                gray_flat = gray.flatten().astype(np.float32) / 255.0
                features.extend(gray_flat[:128])
                
                # 2. Histogram features (64 bins for better distribution)
                hist = cv2.calcHist([gray], [0], None, [64], [0, 256])
                hist_flat = hist.flatten() / np.max(hist) if np.max(hist) > 0 else hist.flatten()
                features.extend(hist_flat)
                
                # 3. HSV color features (normalized)
                hsv_flat = hsv[:,:,0].flatten().astype(np.float32) / 180.0  # Hue normalized to 0-1
                features.extend(hsv_flat[:32])
                
                # 4. Saturation features
                sat_flat = hsv[:,:,1].flatten().astype(np.float32) / 255.0
                features.extend(sat_flat[:32])
                
                # 5. Edge features (Laplacian for better edge detection)
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                edge_flat = laplacian.flatten().astype(np.float32) / np.max(np.abs(laplacian)) if np.max(np.abs(laplacian)) > 0 else laplacian.flatten()
                features.extend(edge_flat[:64])
                
                # 6. Texture features (local binary pattern approximation)
                kernel = np.array([[-1,-1,-1], [-1,8,-1], [-1,-1,-1]])
                texture = cv2.filter2D(gray, -1, kernel)
                texture_flat = texture.flatten().astype(np.float32) / np.max(np.abs(texture)) if np.max(np.abs(texture)) > 0 else texture.flatten()
                features.extend(texture_flat[:64])
                
                # 7. Gradient magnitude features
                sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                gradient_mag = np.sqrt(sobel_x**2 + sobel_y**2)
                gradient_flat = gradient_mag.flatten().astype(np.float32) / np.max(gradient_mag) if np.max(gradient_mag) > 0 else gradient_mag.flatten()
                features.extend(gradient_flat[:64])
                
                # Ensure we have exactly 512 features
                features = np.array(features)
                if len(features) < 512:
                    features = np.pad(features, (0, 512 - len(features)))
                else:
                    features = features[:512]
                
                # Normalize the entire feature vector
                features = features / np.linalg.norm(features) if np.linalg.norm(features) > 0 else features
                
                return features.tolist()
        
        except Exception as e:
            print(f"Error getting face embedding: {e}")
            return None
    
    def compare_faces(self, embedding1: List[float], embedding2: List[float], threshold: float = 0.6) -> Tuple[bool, float]:
        """Compare two face embeddings"""
        try:
            if len(embedding1) != len(embedding2):
                return False, 0.0
            
            # Calculate cosine similarity
            embedding1_np = np.array(embedding1)
            embedding2_np = np.array(embedding2)
            
            # Normalize embeddings
            embedding1_norm = embedding1_np / np.linalg.norm(embedding1_np)
            embedding2_norm = embedding2_np / np.linalg.norm(embedding2_np)
            
            # Calculate similarity
            similarity = np.dot(embedding1_norm, embedding2_norm)
            
            # Convert to distance (0 = identical, 2 = completely different)
            distance = 1 - similarity
            
            # Check if faces match (lower distance = more similar)
            is_match = distance < threshold
            
            return is_match, float(distance)
        
        except Exception as e:
            print(f"Error comparing faces: {e}")
            return False, 1.0
    
    def save_face_image(self, image_data: str, filename: str = None) -> Optional[str]:
        """Save face image from base64 data"""
        try:
            if not filename:
                filename = f"face_{uuid.uuid4().hex}.jpg"
            
            # Decode base64 image
            image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return None
            
            # Detect face
            face = self.detect_face(image)
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
    
    def verify_face_from_image(self, stored_embedding: List[float], image_data: str, threshold: float = 0.6) -> Tuple[bool, float]:
        """Verify face from uploaded image against stored embedding with enhanced accuracy"""
        try:
            # Decode base64 image
            image_data = image_data.split(',')[1]  # Remove data:image/jpeg;base64, prefix
            image_bytes = base64.b64decode(image_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                print("Failed to decode uploaded image")
                return False, 1.0
            
            # Try multiple preprocessing approaches for better accuracy
            best_match = False
            best_distance = 1.0
            
            # Approach 1: Original image
            current_embedding1 = self.get_face_embedding(image)
            if current_embedding1 is not None:
                is_match1, distance1 = self.compare_faces(stored_embedding, current_embedding1, threshold)
                if is_match1:
                    return True, distance1
                if distance1 < best_distance:
                    best_distance = distance1
            
            # Approach 2: Enhanced contrast
            try:
                lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
                lab[:,:,0] = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(lab[:,:,0])
                enhanced_image = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
                
                current_embedding2 = self.get_face_embedding(enhanced_image)
                if current_embedding2 is not None:
                    is_match2, distance2 = self.compare_faces(stored_embedding, current_embedding2, threshold)
                    if is_match2:
                        return True, distance2
                    if distance2 < best_distance:
                        best_distance = distance2
            except Exception as e:
                print(f"Contrast enhancement failed: {e}")
            
            # Approach 3: Slightly different scale (for uploaded photos that might be scaled differently)
            try:
                # Try slight upscaling
                scaled_up = cv2.resize(image, None, fx=1.1, fy=1.1, interpolation=cv2.INTER_CUBIC)
                current_embedding3 = self.get_face_embedding(scaled_up)
                if current_embedding3 is not None:
                    is_match3, distance3 = self.compare_faces(stored_embedding, current_embedding3, threshold)
                    if is_match3:
                        return True, distance3
                    if distance3 < best_distance:
                        best_distance = distance3
            except Exception as e:
                print(f"Upscaling failed: {e}")
            
            # Return the best result found
            return best_distance < threshold, best_distance
        
        except Exception as e:
            print(f"Error verifying face: {e}")
            return False, 1.0

# Global face encoder instance
face_encoder = FaceEncoder()