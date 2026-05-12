#!/usr/bin/env python3
"""
Initialize the database manually
"""
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, 'e:/Blockchain - voting/p-4/secure-voting-system')

from app import app, db
from database.models import Voter, Candidate, Election, Vote, BlockchainBlock, Admin

print("🗄️ Initializing database...")

with app.app_context():
    try:
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Check what tables were created
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Created tables: {tables}")
        
        # Create default admin if not exists
        if not Admin.query.first():
            admin = Admin(
                username='admin',
                email='admin@voting.com'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin created - username: admin, password: admin123")
        else:
            print("ℹ️ Admin user already exists")
            
        # Show current admin users
        admins = Admin.query.all()
        print(f"Total admin users: {len(admins)}")
        for admin in admins:
            print(f"  - Username: {admin.username}, Email: {admin.email}")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()

print("🎉 Database initialization complete!")