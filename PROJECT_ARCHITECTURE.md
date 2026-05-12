# Secure Blockchain-Based Voting System - Project Architecture

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Technical Requirements](#technical-requirements)
4. [User Flow and System Design](#user-flow-and-system-design)
5. [Database Architecture](#database-architecture)
6. [Blockchain Implementation](#blockchain-implementation)
7. [Security Features](#security-features)
8. [Frontend Architecture](#frontend-architecture)
9. [API Design](#api-design)
10. [Deployment Architecture](#deployment-architecture)
11. [Testing Strategy](#testing-strategy)
12. [Conclusion](#conclusion)

## Introduction

The Secure Blockchain-Based Voting System is a comprehensive web application designed to provide transparent, secure, and tamper-proof electronic voting. The system leverages blockchain technology to ensure vote integrity, implements multi-factor authentication for voter verification, and provides real-time election monitoring capabilities.

### Project Objectives
- **Transparency**: All votes are recorded on an immutable blockchain ledger
- **Security**: Multi-layered security with face recognition, OTP verification, and encrypted voting
- **Accessibility**: User-friendly interface accessible across all devices
- **Scalability**: Modular architecture supporting multiple elections simultaneously
- **Auditability**: Complete audit trail for election verification

### Key Features
- Blockchain-based vote recording with cryptographic hashing
- Face recognition authentication system
- One-Time Password (OTP) verification
- Real-time election results and analytics
- Admin dashboard for election management
- Mobile-responsive design
- Rate limiting and security protections

## System Architecture

### High-Level Architecture
The system follows a three-tier architecture pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Voter     │  │    Admin     │  │  Public Portal   │  │
│  │  Interface  │  │  Dashboard   │  │   (Results)      │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Flask     │  │    JWT       │  │   Rate Limiter   │  │
│  │  Framework  │  │  Authentication│  │   (Security)     │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Blockchain │  │ Face Recog.  │  │   OTP System     │  │
│  │   Engine    │  │   System     │  │   (Twilio)       │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                    Data Layer                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   SQLite    │  │  Blockchain  │  │   File System    │  │
│  │  Database   │  │    Ledger    │  │  (Images/Logs)   │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### Core Components
1. **Flask Application Server** (`app.py`)
   - Main application entry point
   - Blueprint registration for modular routing
   - Extension initialization (JWT, LoginManager, RateLimiter)
   - Database setup and migration

2. **Authentication System**
   - **Face Recognition**: ONNX-based facial recognition using `ai/face_encoder.py`
   - **Password Authentication**: Werkzeug password hashing
   - **JWT Tokens**: Flask-JWT-Extended for API security
   - **OTP Verification**: Time-based one-time passwords

3. **Blockchain Engine** (`blockchain/blockchain.py`)
   - Custom blockchain implementation
   - Proof-of-Work consensus mechanism
   - Cryptographic vote hashing
   - Immutable ledger maintenance

4. **Database Layer** (`database/models.py`)
   - SQLAlchemy ORM for data persistence
   - Relational database design
   - User and election management
   - Vote recording and verification

5. **Frontend Layer** (`templates/`)
   - Jinja2 templating engine
   - Responsive HTML5/CSS3 design
   - JavaScript for interactivity
   - Modern glassmorphism UI design

## Technical Requirements

### System Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 18.04+), macOS 10.14+
- **Python**: 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free space for installation
- **Network**: Internet connection for face recognition model download

### Software Dependencies
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-JWT-Extended==4.5.3
Flask-Limiter==3.5.0
Werkzeug==2.3.7
opencv-python==4.8.1.78
onnxruntime==1.16.0
numpy==1.24.3
Pillow==10.0.1
python-dotenv==1.0.0
```

### Hardware Requirements
- **Camera**: Required for face recognition authentication
- **Microphone**: Optional for future voice features
- **Display**: Minimum 1024x768 resolution

## User Flow and System Design

### Voter Registration Flow
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Landing   │────▶│ Registration│────▶│ Face Capture│────▶│ OTP Verify  │
│   Page      │     │    Form     │     │  & Upload   │     │   Phone     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Login     │◀────│ Pending     │◀────│ Face Train  │◀────│ OTP Sent    │
│   Page      │     │ Approval    │     │  & Store    │     │  & Wait     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Voting Process Flow
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Login     │────▶│ Face Auth   │────▶│ Election    │────▶│ Candidate   │
│   (Email)   │     │  Verify     │     │ Selection   │     │  Review     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Dashboard  │◀────│ OTP Verify  │◀────│ Vote Cast   │◀────│ Confirm     │
│   (Results) │     │   Phone     │     │ Blockchain  │     │  Vote       │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

### Admin Management Flow
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Admin     │────▶│ Dashboard   │────▶│ Voter       │────▶│ Election    │
│   Login     │     │ Overview    │     │ Management  │     │  Setup      │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Analytics  │◀────│ Settings    │◀────│ Candidate   │◀────│ Results     │
│   & Reports │     │ & Config    │     │ Management  │     │  View       │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## Database Architecture

### Entity Relationship Diagram
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     Voter       │     │    Election     │     │   Candidate     │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │────▶│ id (PK)         │────▶│ id (PK)         │
│ email           │     │ title           │     │ name            │
│ password_hash   │     │ description     │     │ party           │
│ name            │     │ start_time      │     │ election_id (FK)│
│ phone           │     │ end_time        │     │ photo           │
│ face_encoding   │     │ is_active       │     │ description     │
│ is_approved     │     │ created_by      │     │ created_at      │
│ created_at      │     │ created_at      │     │ updated_at      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│      Vote       │     │  BlockchainBlock│     │   Admin         │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ voter_id (FK)   │     │ block_id        │     │ username        │
│ candidate_id(FK)│     │ voter_hash      │     │ email           │
│ election_id (FK)│     │ vote_hash       │     │ password_hash   │
│ vote_hash       │     │ previous_hash   │     │ created_at      │
│ blockchain_hash │     │ current_hash    │     │ last_login      │
│ timestamp       │     │ nonce           │     │ is_active       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Database Schema

#### Voter Table
```sql
CREATE TABLE voter (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    face_encoding TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Election Table
```sql
CREATE TABLE election (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES admin(id)
);
```

#### Candidate Table
```sql
CREATE TABLE candidate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    party VARCHAR(100),
    election_id INTEGER NOT NULL,
    photo VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (election_id) REFERENCES election(id)
);
```

#### Vote Table
```sql
CREATE TABLE vote (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voter_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    election_id INTEGER NOT NULL,
    vote_hash VARCHAR(64) NOT NULL,
    blockchain_hash VARCHAR(64),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (voter_id) REFERENCES voter(id),
    FOREIGN KEY (candidate_id) REFERENCES candidate(id),
    FOREIGN KEY (election_id) REFERENCES election(id)
);
```

#### BlockchainBlock Table
```sql
CREATE TABLE blockchain_block (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    voter_hash VARCHAR(64) NOT NULL,
    vote_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    current_hash VARCHAR(64) NOT NULL,
    nonce INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Blockchain Implementation

### Blockchain Structure
```python
class Block:
    def __init__(self, index, timestamp, voter_hash, vote_hash, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.voter_hash = voter_hash
        self.vote_hash = vote_hash
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.current_hash = self.calculate_hash()
    
    def calculate_hash(self):
        # SHA-256 hashing of block data
        block_string = json.dumps({...}, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        # Proof-of-Work consensus
        target = '0' * difficulty
        while self.current_hash[:difficulty] != target:
            self.nonce += 1
            self.current_hash = self.calculate_hash()
```

### Vote Hashing Process
```python
class VoteHasher:
    @staticmethod
    def hash_vote(voter_id, candidate_id, timestamp):
        # Combine voter ID, candidate ID, and timestamp
        vote_data = f"{voter_id}:{candidate_id}:{timestamp}"
        return hashlib.sha256(vote_data.encode()).hexdigest()
    
    @staticmethod
    def hash_voter(voter_email, voter_phone):
        # Hash voter identification
        voter_data = f"{voter_email}:{voter_phone}"
        return hashlib.sha256(voter_data.encode()).hexdigest()
```

### Blockchain Verification
```python
class Blockchain:
    def __init__(self, difficulty=4):
        self.chain = [self.create_genesis_block()]
        self.difficulty = difficulty
    
    def create_genesis_block(self):
        # First block in the chain
        return Block(0, datetime.now(), "0", "0", "0")
    
    def add_block(self, voter_hash, vote_hash):
        # Add new vote to blockchain
        previous_block = self.get_latest_block()
        new_block = Block(
            len(self.chain),
            datetime.now(),
            voter_hash,
            vote_hash,
            previous_block.current_hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self):
        # Verify blockchain integrity
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.current_hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.current_hash:
                return False
        
        return True
```

## Security Features

### Multi-Factor Authentication
1. **Password Authentication**: Bcrypt hashing with salt
2. **Face Recognition**: ONNX-based facial encoding comparison
3. **OTP Verification**: Time-based one-time passwords

### Data Protection
1. **Vote Encryption**: SHA-256 hashing of vote data
2. **Voter Anonymity**: Voter hashes instead of direct identification
3. **Blockchain Immutability**: Tamper-proof vote recording
4. **Rate Limiting**: Prevent brute force attacks

### Network Security
1. **JWT Tokens**: Secure API authentication
2. **HTTPS Ready**: Configurable for SSL/TLS deployment
3. **Input Validation**: Server-side validation for all inputs
4. **SQL Injection Prevention**: ORM-based database queries

## Frontend Architecture

### Template Structure
```
templates/
├── base.html                 # Base template with common layout
├── base_modern.html         # Modern design base template
├── index.html               # Landing page
├── login.html               # Login page
├── register.html            # Registration page
├── vote.html                # Voting interface
├── voter_dashboard.html     # Voter dashboard
├── admin/
│   ├── dashboard.html       # Admin overview
│   ├── candidates.html      # Candidate management
│   ├── elections.html       # Election management
│   ├── voters.html          # Voter approval
│   ├── blockchain.html      # Blockchain viewer
│   └── results.html         # Election results
└── modern/                  # Modern design templates
    ├── index_modern.html
    ├── login_modern.html
    └── ... (modern versions)
```

### CSS Architecture
```css
static/css/
├── style.css           # Base styles
├── modern-theme.css    # Modern design system
└── responsive.css      # Mobile responsiveness
```

### JavaScript Components
```javascript
static/js/
├── face-auth.js        # Face recognition
├── otp-verify.js       # OTP verification
├── vote-cast.js        # Voting process
└── admin-dashboard.js  # Admin functions
```

## API Design

### Authentication Endpoints
```
POST /auth/login          # User login
POST /auth/logout         # User logout
POST /auth/register       # Voter registration
POST /auth/face-verify    # Face recognition
POST /auth/otp-send       # Send OTP
POST /auth/otp-verify     # Verify OTP
```

### Voting Endpoints
```
GET  /election/list       # List active elections
GET  /election/candidates # Get candidates
POST /vote/cast           # Cast vote
GET  /vote/status         # Check vote status
GET  /vote/history        # Voting history
```

### Admin Endpoints
```
GET  /admin/dashboard     # Admin overview
POST /admin/candidate     # Add candidate
PUT  /admin/candidate/:id # Update candidate
DELETE /admin/candidate/:id # Remove candidate
POST /admin/election      # Create election
GET  /admin/voters        # List voters
PUT  /admin/voter/:id/approve # Approve voter
GET  /admin/blockchain    # View blockchain
GET  /admin/results       # Election results
```

## Deployment Architecture

### Development Environment
```
Local Machine Setup:
- Python 3.8+ with virtual environment
- SQLite database
- Local file storage for images
- Development server (Flask built-in)
```

### Production Environment
```
Production Setup:
- WSGI server (Gunicorn/uWSGI)
- PostgreSQL/MySQL database
- Cloud storage (AWS S3/Azure Blob)
- Reverse proxy (Nginx/Apache)
- SSL/TLS certificates
- Load balancer for scalability
```

### Network Configuration
```python
# Network access configuration
app.run(debug=True, host='0.0.0.0', port=5000)

# This allows access from:
- Localhost: http://127.0.0.1:5000
- Local network: http://192.168.x.x:5000
- Remote access: http://your-ip:5000
```

## Testing Strategy

### Unit Testing
- **Backend**: Python unittest for models and blockchain
- **Frontend**: JavaScript testing with Jest
- **API**: Postman/Newman for API testing

### Integration Testing
- **Database**: CRUD operations testing
- **Authentication**: Login/logout flow
- **Voting**: Complete voting process
- **Blockchain**: Block creation and validation

### Security Testing
- **Penetration Testing**: SQL injection, XSS attempts
- **Rate Limiting**: API abuse prevention
- **Authentication**: Brute force protection
- **Data Integrity**: Blockchain validation

### Performance Testing
- **Load Testing**: Concurrent user simulation
- **Stress Testing**: System limits evaluation
- **Database**: Query optimization
- **Frontend**: Page load times

## Conclusion

The Secure Blockchain-Based Voting System represents a comprehensive solution for modern electronic voting needs. The architecture successfully combines security, transparency, and usability through:

### Key Achievements
1. **Blockchain Integration**: Immutable vote recording with cryptographic security
2. **Multi-Factor Authentication**: Enhanced security through face recognition and OTP
3. **Responsive Design**: Accessible across all devices and screen sizes
4. **Modular Architecture**: Scalable and maintainable codebase
5. **Real-time Processing**: Instant vote validation and result computation

### Future Enhancements
1. **Mobile Application**: Native iOS/Android apps
2. **Advanced Analytics**: Machine learning for fraud detection
3. **Multi-language Support**: Internationalization features
4. **Biometric Integration**: Fingerprint and iris scanning
5. **Cloud Deployment**: AWS/Azure cloud services
6. **API Integration**: Third-party election monitoring

### Deployment Readiness
The system is production-ready with:
- Comprehensive security measures
- Scalable architecture design
- Detailed documentation
- Testing procedures
- Network accessibility configuration

This architecture document serves as a complete reference for understanding, deploying, and maintaining the Secure Blockchain-Based Voting System.

---

**Document Version**: 1.0  
**Last Updated**: November 2025  
**Project**: Secure Blockchain-Based Voting System  
**Authors**: Development Team