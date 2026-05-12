#!/usr/bin/env python3
import requests
import json

# Get voter info first
from app import app
from database.models import db, Voter
from werkzeug.security import generate_password_hash

with app.app_context():
    # Find active and approved voters
    active_voters = Voter.query.filter_by(is_active=True, is_approved=True).all()
    if active_voters:
        for voter in active_voters:
            print(f"Voter: {voter.name}")
            print(f"Virtual Voter ID: {voter.virtual_voter_id}")
            print(f"Email: {voter.email}")
            # Reset password to known value for testing
            voter.set_password('password123')
            db.session.commit()
            print(f"Password reset to: password123")
            print("---")
        print("All passwords have been reset to 'password123'")
    else:
        print("No active voters found")