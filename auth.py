from flask import Blueprint, request, jsonify, session, flash, redirect, url_for, render_template
from flask_login import login_user, logout_user, login_required, current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import random
import json
from werkzeug.security import generate_password_hash, check_password_hash

from database.models import db, Voter, Admin, OTPVerification
from ai.deepface_encoder import DeepFaceEncoder

auth_bp = Blueprint('auth', __name__)

# Initialize DeepFace encoder
deepface_encoder = DeepFaceEncoder()

# Rate limiting for authentication endpoints
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["5 per minute"]
)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'aadhaar_number', 'password', 'face_image']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if email already exists
        if Voter.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Check if Aadhaar number already exists
        if Voter.query.filter_by(aadhaar_number=data['aadhaar_number']).first():
            return jsonify({'error': 'Aadhaar number already registered'}), 400
        
        # Process face image
        face_embedding = None
        face_image_path = None
        
        if data.get('face_image'):
            # Save face image and get embedding using DeepFaceEncoder
            face_image_path = deepface_encoder.save_face_image(data['face_image'])
            if not face_image_path:
                return jsonify({'error': 'Face detection failed. Please ensure your face is clearly visible.'}), 400
            
            # Get face embedding
            import cv2
            import numpy as np
            import base64
            
            # Decode image for embedding extraction
            image_data = data['face_image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            face_embedding = deepface_encoder.get_face_embedding(image)
            if not face_embedding:
                return jsonify({'error': 'Face embedding extraction failed'}), 400
            
            # Convert to list of floats to ensure JSON serializability
            face_embedding = [float(x) for x in face_embedding]
        
        # Create new voter
        voter = Voter(
            virtual_voter_id=Voter.generate_virtual_voter_id(),
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            aadhaar_number=data['aadhaar_number'],
            face_embedding=json.dumps(face_embedding) if face_embedding else None,
            face_image_path=face_image_path
        )
        
        # Set password
        voter.set_password(data['password'])
        
        # Save to database
        db.session.add(voter)
        db.session.commit()
        
        return jsonify({
            'message': 'Registration successful! Please wait for admin approval.',
            'virtual_voter_id': voter.virtual_voter_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('virtual_voter_id') or not data.get('password'):
            return jsonify({'error': 'Virtual Voter ID and password are required'}), 400
        
        # Find voter
        voter = Voter.query.filter_by(virtual_voter_id=data['virtual_voter_id']).first()
        
        if not voter:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if voter is approved
        if not voter.is_approved:
            return jsonify({'error': 'Your registration is pending admin approval'}), 403
        
        # Check if voter is active
        if not voter.is_active:
            return jsonify({'error': 'Your account has been deactivated'}), 403
        
        # Verify password
        if not voter.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Store voter ID in session for face authentication
        session['pending_voter_id'] = voter.id
        
        return jsonify({
            'message': 'Password verified. Please complete face authentication.',
            'next_step': 'face_auth'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/face-auth', methods=['POST'])
@limiter.limit("5 per minute")
def face_authentication():
    try:
        data = request.get_json()
        
        if not data.get('face_image'):
            return jsonify({'error': 'Face image is required'}), 400
        
        # Get pending voter ID from session
        voter_id = session.get('pending_voter_id')
        if not voter_id:
            return jsonify({'error': 'Session expired. Please login again.'}), 401
        
        # Find voter
        voter = Voter.query.get(voter_id)
        if not voter or not voter.face_embedding:
            return jsonify({'error': 'Face authentication not available for this user'}), 400
        
        # Parse stored face embedding
        stored_embedding = json.loads(voter.face_embedding)
        
        # Verify face using DeepFaceEncoder with optimized threshold
        print(f"Stored embedding dimensions: {len(stored_embedding)}")
        is_match, similarity_score = deepface_encoder.verify_face_from_image(
            stored_embedding, 
            data['face_image']
            # No threshold parameter - use encoder's optimized default
        )
        
        if not is_match:
            print(f"Face authentication failed - Similarity Score: {similarity_score}, Threshold: {deepface_encoder.get_model_threshold(len(stored_embedding))}")
            return jsonify({
                'error': 'Face authentication failed. Please ensure proper lighting and face alignment.',
                'similarity_score': similarity_score,
                'unauthorized': True  # Flag for frontend popup
            }), 401
        
        # Generate OTP
        otp_code = str(random.randint(100000, 999999))
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        # Save OTP
        otp_verification = OTPVerification(
            voter_id=voter.id,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.session.add(otp_verification)
        db.session.commit()
        
        # Store voter ID for OTP verification
        session['otp_voter_id'] = voter.id
        
        return jsonify({
            'message': 'Face authentication successful. Please enter OTP.',
            'next_step': 'otp_verify',
            'otp_code': otp_code,  # Display OTP directly for demo purposes
            'otp_hint': f'OTP: {otp_code} (for demo purposes - normally sent to phone ending in {voter.phone[-4:]})'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Face authentication failed: {str(e)}'}), 500

@auth_bp.route('/otp-verify', methods=['POST'])
@limiter.limit("5 per minute")
def otp_verify():
    try:
        data = request.get_json()
        
        otp_code = data.get('otp_code') or data.get('otp')
        if not otp_code:
            return jsonify({'error': 'OTP code is required'}), 400
        
        # Get voter ID from session
        voter_id = session.get('otp_voter_id')
        if not voter_id:
            return jsonify({'error': 'Session expired. Please login again.'}), 401
        
        # Find voter
        voter = Voter.query.get(voter_id)
        if not voter:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Find latest OTP for this voter
        otp_verification = OTPVerification.query.filter_by(
            voter_id=voter.id,
            is_used=False
        ).order_by(OTPVerification.created_at.desc()).first()
        
        if not otp_verification:
            return jsonify({'error': 'No OTP found. Please request a new one.'}), 400
        
        # Check if OTP is expired
        if otp_verification.is_expired():
            return jsonify({'error': 'OTP has expired. Please request a new one.'}), 400
        
        # Verify OTP
        if otp_verification.otp_code != otp_code:
            return jsonify({'error': 'Invalid OTP code'}), 401
        
        # Mark OTP as used
        otp_verification.is_used = True
        
        # Create access token
        access_token = create_access_token(identity={
            'user_id': voter.id,
            'user_type': 'voter',
            'virtual_voter_id': voter.virtual_voter_id
        })
        
        # Login user
        login_user(voter)
        
        # Set user type in session
        session['user_type'] = 'voter'
        
        # Clear session data
        session.pop('pending_voter_id', None)
        session.pop('otp_voter_id', None)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful!',
            'access_token': access_token,
            'redirect_url': url_for('voter.voter_dashboard')
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'OTP verification failed: {str(e)}'}), 500

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find admin
        admin = Admin.query.filter_by(username=data['username']).first()
        
        if not admin or not admin.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not admin.is_active:
            return jsonify({'error': 'Admin account is deactivated'}), 403
        
        # Update last login
        admin.last_login = datetime.utcnow()
        
        # Create access token
        access_token = create_access_token(identity={
            'user_id': admin.id,
            'user_type': 'admin',
            'username': admin.username
        })
        
        # Login user
        login_user(admin)
        
        # Set user type in session
        session['user_type'] = 'admin'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Admin login successful!',
            'access_token': access_token,
            'redirect_url': url_for('admin.admin_dashboard')
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Admin login failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    # Clear user type from session
    session.pop('user_type', None)
    return jsonify({'message': 'Logged out successfully'}), 200