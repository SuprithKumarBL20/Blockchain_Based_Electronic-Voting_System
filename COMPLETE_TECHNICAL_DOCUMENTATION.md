# BLOCKCHAIN VOTING SYSTEM - COMPLETE TECHNICAL DOCUMENTATION

## 1. FACE VERIFICATION & OTP AUTHENTICATION SYSTEM

### Face Verification Process
```
User Login → Password Verification → Face Authentication → OTP Generation → OTP Verification → Access Granted
```

**Step 1: Password Verification**
- User enters Virtual Voter ID and password
- System validates against SQLite database
- Returns success with next_step: 'face_auth'

**Step 2: Face Authentication**
- User uploads/captures face image via camera
- System extracts face embedding using DeepFace/ONNX/OpenCV
- Compares with stored face embedding in database
- Uses cosine similarity with threshold (0.05 for OpenCV, 0.4 for DeepFace)
- Returns OTP code on successful match

**Step 3: OTP Verification**
- 6-digit OTP sent to user's registered phone/email
- OTP expires after 5 minutes
- User enters OTP for final verification
- Access granted to voter dashboard

### Technical Implementation
- **Face Detection**: Multiple backends (ONNX, DeepFace, OpenCV)
- **Embedding Extraction**: 512-dimensional vectors (DeepFace) or 265-dimensional (OpenCV)
- **Similarity Calculation**: Cosine distance with configurable thresholds
- **Security**: Rate limiting (5 attempts per minute), session management

## 2. BLOCKCHAIN STORAGE SYSTEM

### What is `/e:/Blockchain - voting/p-4/secure-voting-system/blockchain/__pycache__/blockchain.cpython-313.pyc`?
- **Compiled Python bytecode**: Auto-generated compiled version of `blockchain.py`
- **Purpose**: Speeds up module loading by caching compiled code
- **Location**: `__pycache__/` directory
- **Safe to delete**: Yes, Python will regenerate it when needed

### Blockchain Architecture

**Block Structure**:
```python
Block {
    index: int,              # Block number (0 = genesis)
    timestamp: datetime,     # Creation time
    voter_hash: str,         # Hash of voter ID
    vote_hash: str,          # Hash of vote data
    previous_hash: str,      # Hash of previous block
    nonce: int,              # Proof of work nonce
    current_hash: str        # SHA256 hash of block
}
```

**Blockchain Process**:
1. **Vote Cast**: User selects candidate and confirms vote
2. **Block Creation**: New block created with vote data
3. **Mining**: Proof of work with difficulty 4 (4 leading zeros)
4. **Chain Addition**: Block added to blockchain with previous hash link
5. **Storage**: Block stored in `blockchain_blocks` table in SQLite

**Proof of Work**:
- Difficulty: 4 (requires hash starting with "0000")
- Algorithm: SHA256 with nonce increment
- Security: Prevents tampering and ensures immutability

## 3. DATABASE SYSTEM

### Primary Database: `db.sqlite3`
- **Location**: `e:/Blockchain - voting/p-4/secure-voting-system/database/db.sqlite3`
- **Size**: 112 KB
- **Tables**: 7 tables with complete voting system data

### Database Schema

**voters Table**:
```sql
CREATE TABLE voters (
    id INTEGER PRIMARY KEY,
    virtual_voter_id VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    face_embedding TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    has_voted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**candidates Table**:
```sql
CREATE TABLE candidates (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    party_name VARCHAR(100) NOT NULL,
    party_symbol VARCHAR(100),
    description TEXT,
    photo_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**elections Table**:
```sql
CREATE TABLE elections (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**blockchain_blocks Table**:
```sql
CREATE TABLE blockchain_blocks (
    index INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    voter_hash VARCHAR(255) NOT NULL,
    vote_hash VARCHAR(255) NOT NULL,
    previous_hash VARCHAR(255) NOT NULL,
    current_hash VARCHAR(255) NOT NULL,
    nonce INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**votes Table**:
```sql
CREATE TABLE votes (
    id INTEGER PRIMARY KEY,
    voter_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    election_id INTEGER NOT NULL,
    block_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(voter_id) REFERENCES voters(id),
    FOREIGN KEY(candidate_id) REFERENCES candidates(id),
    FOREIGN KEY(election_id) REFERENCES elections(id)
);
```

**otp_verifications Table**:
```sql
CREATE TABLE otp_verifications (
    id INTEGER PRIMARY KEY,
    voter_id INTEGER NOT NULL,
    otp_code VARCHAR(6) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(voter_id) REFERENCES voters(id)
);
```

**admins Table**:
```sql
CREATE TABLE admins (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. HOW TO MANUALLY EDIT DATABASE

### Method 1: Using SQLite Browser (GUI)
1. **Download**: SQLite Browser from https://sqlitebrowser.org/
2. **Open Database**: File → Open Database → Select `database/db.sqlite3`
3. **Browse Data**: Click on tables to view/edit data
4. **Execute SQL**: Use "Execute SQL" tab for queries
5. **Save Changes**: File → Write Changes

### Method 2: Using Python (Command Line)
```python
import sqlite3

# Connect to database
conn = sqlite3.connect('database/db.sqlite3')
cursor = conn.cursor()

# View data
cursor.execute("SELECT * FROM voters;")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Insert data
cursor.execute("INSERT INTO voters (virtual_voter_id, name, email, phone, password_hash) VALUES (?, ?, ?, ?, ?)", 
               ('VV-2025-99999', 'Test User', 'test@email.com', '1234567890', 'hashed_password'))

# Update data
cursor.execute("UPDATE voters SET is_approved = TRUE WHERE virtual_voter_id = 'VV-2025-99999';")

# Delete data
cursor.execute("DELETE FROM voters WHERE virtual_voter_id = 'VV-2025-99999';")

# Commit changes
conn.commit()
conn.close()
```

### Method 3: Using Command Line (sqlite3)
```bash
# Navigate to database directory
cd database

# Open SQLite CLI
sqlite3 db.sqlite3

# View tables
.tables

# View schema
.schema voters

# Query data
SELECT * FROM voters WHERE is_approved = TRUE;

# Insert data
INSERT INTO voters (virtual_voter_id, name, email, phone, password_hash) 
VALUES ('VV-2025-99999', 'Test User', 'test@email.com', '1234567890', 'hashed_password');

# Exit
.quit
```

## 5. FILE STORAGE SYSTEM

### Upload Directories
- **Party Symbols**: `static/uploads/` - Candidate party logos
- **Face Images**: `static/images/faces/` - Voter face photos for recognition
- **Static Files**: `static/css/`, `static/js/` - Frontend assets

### File Structure
```
secure-voting-system/
├── ai/                          # Face recognition AI models
│   ├── deepface_encoder.py     # Main face encoder
│   ├── face_encoder.py         # ONNX face encoder
│   ├── robust_face_encoder.py  # Enhanced OpenCV encoder
│   └── model.onnx              # ONNX face recognition model
├── blockchain/                  # Blockchain implementation
│   └── blockchain.py           # Block and Blockchain classes
├── database/                    # Database layer
│   ├── models.py               # SQLAlchemy models
│   └── db.sqlite3              # Main SQLite database
├── routes/                      # Flask route handlers
│   ├── auth.py                 # Authentication routes
│   ├── admin.py                # Admin panel routes
│   ├── voter.py                # Voter functionality routes
│   └── election.py             # Election management routes
├── static/                      # Static web assets
│   ├── css/                    # Stylesheets
│   ├── images/                 # Images and photos
│   └── uploads/                # Uploaded files
├── templates/                   # HTML templates
├── instance/                    # Flask instance files
└── blockchain/                  # Blockchain cache files
```

## 6. SECURITY FEATURES

### Authentication Security
- **Password Hashing**: Werkzeug's secure password hashing
- **Rate Limiting**: Flask-Limiter (5 attempts per minute)
- **Session Management**: Flask-Login with secure sessions
- **OTP Security**: 6-digit codes with 5-minute expiration

### Blockchain Security
- **Immutability**: SHA256 hash chaining prevents tampering
- **Proof of Work**: Mining difficulty prevents fake blocks
- **Voter Anonymity**: Voter IDs are hashed, not stored in plain text
- **Vote Integrity**: Each vote cryptographically linked to previous

### Data Protection
- **Face Embeddings**: Stored as JSON, not raw images
- **Database Encryption**: SQLite with proper access controls
- **Input Validation**: All user inputs sanitized and validated
- **CSRF Protection**: Built into Flask forms

## 7. TROUBLESHOOTING COMMON ISSUES

### Face Detection Not Working
1. **Check ONNX Runtime**: `pip install onnxruntime`
2. **Check TensorFlow**: Use `tensorflow-cpu` for Windows
3. **Check OpenCV**: Should be installed with `opencv-python`
4. **Verify Model**: Ensure `ai/model.onnx` exists

### Database Connection Issues
1. **Check File Path**: Ensure `database/db.sqlite3` exists
2. **Check Permissions**: Ensure write access to database file
3. **Check Schema**: Run `init_db.py` to initialize tables
4. **Backup First**: Always backup before manual edits

### Login Issues
1. **Check Account Status**: Verify `is_approved` and `is_active` flags
2. **Check Password**: Use correct password (voters: password123, admin: admin123)
3. **Check Face Auth**: Ensure face embedding exists for voter
4. **Check OTP**: Verify OTP not expired and correct code

### Blockchain Issues
1. **Check Genesis Block**: Ensure block 0 exists in database
2. **Check Mining**: Verify proof of work is completing
3. **Check Chain Validity**: Use blockchain validation methods
4. **Check Database**: Ensure blockchain_blocks table exists