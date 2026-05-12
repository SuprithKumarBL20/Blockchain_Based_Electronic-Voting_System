from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Import from our modules
from config import Config
from database.models import db, Voter, Candidate, Election, Vote, Admin, OTPVerification, BlockchainBlock
from blockchain.blockchain import Blockchain, VoteHasher
from ai.face_encoder import face_encoder

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize blockchain
blockchain = Blockchain(difficulty=app.config['BLOCKCHAIN_DIFFICULTY'])

@login_manager.user_loader
def load_user(user_id):
    # Get user type from session to determine which table to query
    user_type = session.get('user_type')
    
    if user_type == 'admin':
        return Admin.query.get(int(user_id))
    elif user_type == 'voter':
        return Voter.query.get(int(user_id))
    else:
        # Fallback to old behavior if user_type not in session
        # Try to load as voter first, then as admin
        voter = Voter.query.get(int(user_id))
        if voter:
            return voter
        
        admin = Admin.query.get(int(user_id))
        if admin:
            return admin
    
    return None

# Create tables
with app.app_context():
    db.create_all()
    
    # Load blockchain from database
    try:
        blockchain.load_from_database(db.session)
        print(f"Blockchain loaded with {len(blockchain.chain)} blocks")
    except Exception as e:
        print(f"Failed to load blockchain: {e}")
    
    # Create default admin if not exists
    if not Admin.query.first():
        admin = Admin(
            username='admin',
            email='admin@voting.com'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Default admin created - username: admin, password: admin123")

# Import routes
from routes.auth import auth_bp
from routes.voter import voter_bp
from routes.admin import admin_bp
from routes.election import election_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(voter_bp, url_prefix='/voter')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(election_bp, url_prefix='/election')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if isinstance(current_user, Admin):
        return redirect(url_for('admin.admin_dashboard'))
    return redirect(url_for('voter.voter_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    print("Starting Secure Voting System...")
    print("Admin credentials: username='admin', password='admin123'")
    print("Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)