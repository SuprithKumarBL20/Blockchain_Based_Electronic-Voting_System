# Secure Blockchain-Based Voting System - Testing & Troubleshooting Guide

## Testing Procedures

### Pre-Testing Checklist
- [ ] Application is running without errors
- [ ] Database is accessible
- [ ] Camera is working (for face recognition)
- [ ] Network access is configured
- [ ] Admin credentials are available

### 1. System Functionality Tests

#### A. Authentication Testing

**Test 1: Admin Login**
1. Navigate to `http://localhost:5000/admin/login`
2. Enter username: `admin`, password: `admin123`
3. Expected: Redirect to admin dashboard
4. Verify: Admin dashboard loads with statistics

**Test 2: Invalid Login**
1. Navigate to login page
2. Enter incorrect credentials
3. Expected: Error message displayed
4. Verify: No access to protected pages

**Test 3: Logout Functionality**
1. Login as admin
2. Click logout button
3. Expected: Redirect to homepage
4. Verify: Cannot access admin pages without login

#### B. Voter Registration Testing

**Test 1: New Voter Registration**
1. Navigate to registration page
2. Fill in valid details:
   - Name: "Test Voter"
   - Email: "test@example.com"
   - Phone: "1234567890"
   - Password: "test123"
3. Upload a clear face photo
4. Expected: Registration successful, pending approval

**Test 2: Duplicate Email Registration**
1. Try to register with existing email
2. Expected: Error message about duplicate email

**Test 3: Invalid Phone Number**
1. Register with invalid phone format
2. Expected: Validation error for phone format

#### C. Face Recognition Testing

**Test 1: Face Upload**
1. During registration, upload a clear face photo
2. Expected: Photo uploads successfully
3. Verify: Photo appears in voter profile

**Test 2: Face Authentication**
1. Login as registered voter
2. Allow camera access
3. Show face to camera
4. Expected: Face recognition successful
5. Verify: Access granted to voter dashboard

**Test 3: Face Recognition Failure**
1. Try face recognition with poor lighting
2. Expected: Recognition fails, OTP option offered

#### D. OTP Verification Testing

**Test 1: OTP Sending**
1. During login/registration
2. Click "Send OTP"
3. Expected: OTP sent to registered phone
4. Verify: 6-digit code received

**Test 2: OTP Validation**
1. Enter correct OTP within 5 minutes
2. Expected: OTP validation successful

**Test 3: Expired OTP**
1. Wait 6+ minutes after OTP sent
2. Enter the OTP
3. Expected: OTP expired error

#### E. Election Management Testing

**Test 1: Create Election (Admin)**
1. Login as admin
2. Navigate to Elections → Create Election
3. Fill election details:
   - Title: "Test Election"
   - Description: "Testing election"
   - Start time: Current time + 1 hour
   - End time: Current time + 2 hours
4. Expected: Election created successfully

**Test 2: Add Candidates (Admin)**
1. In admin panel, go to Candidates
2. Click "Add Candidate"
3. Fill candidate details with photo
4. Expected: Candidate added successfully

**Test 3: View Election Results**
1. After voting is complete
2. Navigate to election results
3. Expected: Results show vote counts
4. Verify: Results match actual votes cast

#### F. Voting Process Testing

**Test 1: Cast Vote**
1. Login as approved voter
2. Navigate to active election
3. Select a candidate
4. Confirm vote
5. Expected: Vote recorded successfully
6. Verify: Cannot vote again in same election

**Test 2: Vote Verification**
1. After voting, check voter dashboard
2. Expected: Vote history shows the vote
3. Verify: Blockchain hash is generated

**Test 3: Double Voting Prevention**
1. Try to vote twice in same election
2. Expected: Error message preventing double voting

#### G. Blockchain Testing

**Test 1: Block Creation**
1. Cast a vote
2. Check blockchain in admin panel
3. Expected: New block created with vote data
4. Verify: Block has valid hash and previous hash

**Test 2: Chain Integrity**
1. Navigate to blockchain viewer
2. Verify all blocks are connected
3. Expected: Each block's previous_hash matches previous block's hash

**Test 3: Mining Verification**
1. Check block hash format
2. Expected: Hash starts with 4 zeros (difficulty level)

### 2. Performance Testing

#### A. Load Testing
**Test concurrent users:**
1. Open multiple browser sessions
2. Login with different users simultaneously
3. Expected: System handles multiple users without crashes

#### B. Response Time Testing
**Measure page load times:**
1. Homepage: Should load < 2 seconds
2. Login page: Should load < 1 second
3. Voting page: Should load < 3 seconds
4. Admin dashboard: Should load < 2 seconds

#### C. Database Performance
**Test with large datasets:**
1. Create multiple elections (10+)
2. Add many candidates (50+)
3. Register many voters (100+)
4. Expected: Pages still load within acceptable time

### 3. Security Testing

#### A. Authentication Security
**Test session management:**
1. Login and close browser
2. Reopen browser and navigate to protected page
3. Expected: Redirected to login page

**Test password security:**
1. Try SQL injection in login form: `' OR '1'='1`
2. Expected: Login fails, no database errors

#### B. Input Validation
**Test XSS prevention:**
1. Enter `<script>alert('XSS')</script>` in forms
2. Expected: Input sanitized, no script execution

**Test file upload security:**
1. Try uploading non-image files
2. Expected: Upload rejected with error

#### C. Rate Limiting
**Test API abuse prevention:**
1. Make rapid login attempts (>50/hour)
2. Expected: Rate limit error after threshold

## Common Issues and Solutions

### 1. Application Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`
**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Reinstall requirements
pip install -r requirements.txt
```

**Error**: `Address already in use`
**Solution**:
```bash
# Find process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -i :5000
kill -9 <PID>
```

### 2. Database Issues

**Error**: `sqlite3.OperationalError: database is locked`
**Solution**:
```bash
# Stop the application
# Delete the database file
rm database/db.sqlite3
# Restart application (database will be recreated)
python app.py
```

**Error**: `no such table: voter`
**Solution**:
```bash
# Database tables not created
# Stop and restart the application
# Tables will be created automatically
```

### 3. Camera/Face Recognition Issues

**Error**: Camera not detected
**Solution**:
1. Check camera connection
2. Allow browser camera permissions
3. Try different browser
4. Check if another app is using camera

**Error**: Face recognition always fails
**Solution**:
1. Ensure good lighting conditions
2. Face camera directly
3. Remove glasses/hats if possible
4. Check camera quality (minimum 720p recommended)

### 4. OTP Issues

**Error**: OTP not received
**Solution**:
1. Check phone number format (should be 10 digits)
2. Verify phone can receive SMS
3. Check if SMS service is configured
4. Try email OTP if available

**Error**: OTP validation fails
**Solution**:
1. Ensure OTP entered within 5 minutes
2. Check for typos in OTP entry
3. Request new OTP if expired

### 5. Voting Issues

**Error**: Cannot cast vote
**Solution**:
1. Check if election is active
2. Verify voter is approved by admin
3. Ensure voter hasn't already voted
4. Check election start/end times

**Error**: Vote not recorded in blockchain
**Solution**:
1. Check blockchain difficulty setting
2. Verify system has enough resources
3. Check for blockchain corruption
4. Restart application if needed

### 6. Network Access Issues

**Error**: Cannot access from other devices
**Solution**:
1. Check firewall settings:
   ```bash
   # Windows: Allow Python through firewall
   # Linux: sudo ufw allow 5000
   # Mac: Check Security & Privacy settings
   ```

2. Verify IP address:
   ```bash
   # Find correct IP
   ipconfig  # Windows
   ifconfig  # Linux/Mac
   ```

3. Ensure devices on same network
4. Check for VPN interference

### 7. Performance Issues

**Error**: Slow page loading
**Solution**:
1. Check system resources:
   ```bash
   # Check CPU/RAM usage
   top  # Linux/Mac
   taskmgr  # Windows
   ```

2. Optimize database queries
3. Clear browser cache
4. Restart application

**Error**: Face recognition slow
**Solution**:
1. Close other camera-using applications
2. Reduce camera resolution if possible
3. Check system performance
4. Consider upgrading hardware

### 8. Browser-Specific Issues

**Chrome Issues**:
- Camera permissions: Settings → Privacy → Camera
- Clear cache: Ctrl+Shift+Delete
- Disable extensions temporarily

**Firefox Issues**:
- Camera permissions: Preferences → Privacy → Permissions
- Try safe mode to disable extensions

**Safari Issues**:
- Camera permissions: Safari → Preferences → Websites → Camera
- Clear cache: Safari → Clear History

**Edge Issues**:
- Camera permissions: Settings → Cookies and site permissions → Camera
- Try InPrivate browsing mode

## Advanced Troubleshooting

### 1. Debug Mode
Enable Flask debug mode for detailed error information:
```python
# In app.py, ensure debug=True
app.run(debug=True, host='0.0.0.0', port=5000)
```

### 2. Log Analysis
Check application logs for errors:
```bash
# Look for error messages in console output
# Check browser developer console (F12)
# Review network requests in browser
```

### 3. Database Inspection
Use SQLite browser to inspect database:
```bash
# Install SQLite browser
# Open database/db.sqlite3
# Check table contents and relationships
```

### 4. Blockchain Verification
Manually verify blockchain integrity:
```python
# Python script to verify blockchain
from blockchain.blockchain import Blockchain
blockchain = Blockchain()
print(blockchain.is_chain_valid())
```

### 5. Face Model Verification
Check face recognition model:
```python
# Test face model loading
from ai.face_encoder import face_encoder
print(face_encoder.model_loaded)
```

## Emergency Procedures

### 1. Complete System Reset
If system is completely broken:
```bash
# 1. Stop application
# 2. Delete virtual environment
rm -rf venv
# 3. Delete database
rm database/db.sqlite3
# 4. Recreate environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# 5. Restart application
python app.py
```

### 2. Database Recovery
If database is corrupted:
```bash
# 1. Backup corrupted database
cp database/db.sqlite3 database/db.sqlite3.backup
# 2. Delete corrupted database
rm database/db.sqlite3
# 3. Restart application
python app.py
# 4. Recreate admin user (will happen automatically)
```

### 3. Blockchain Recovery
If blockchain is corrupted:
```bash
# 1. Stop application
# 2. Clear blockchain table (requires SQL)
sqlite3 database/db.sqlite3 "DELETE FROM blockchain_block;"
# 3. Restart application
# 4. Blockchain will rebuild as new votes are cast
```

## Testing Checklist

Use this checklist after setup or troubleshooting:

### Basic Functionality
- [ ] Application starts without errors
- [ ] Homepage loads correctly
- [ ] Admin login works (admin/admin123)
- [ ] Database accessible
- [ ] Camera working for face recognition

### Authentication
- [ ] Voter registration successful
- [ ] Face recognition working
- [ ] OTP verification working
- [ ] Login/logout functionality
- [ ] Session management

### Election Management
- [ ] Create election (admin)
- [ ] Add candidates (admin)
- [ ] Approve voters (admin)
- [ ] View results (admin)

### Voting Process
- [ ] Cast vote successfully
- [ ] Vote recorded in blockchain
- [ ] Double voting prevented
- [ ] Vote history visible

### Security
- [ ] Input validation working
- [ ] Rate limiting active
- [ ] XSS prevention working
- [ ] SQL injection prevented

### Performance
- [ ] Pages load within 3 seconds
- [ ] Multiple users supported
- [ ] No memory leaks
- [ ] Responsive design working

### Network Access
- [ ] Local access (127.0.0.1:5000)
- [ ] Network access (192.168.x.x:5000)
- [ ] Firewall configured
- [ ] Cross-device compatibility

## Getting Help

If you encounter issues not covered in this guide:

1. **Check Documentation**:
   - `PROJECT_ARCHITECTURE.md` for system overview
   - `TECHNICAL_DETAILS.txt` for technical details
   - `SETUP_GUIDE.md` for installation help

2. **Collect Information**:
   - Error messages (exact text)
   - Screenshots of issues
   - Browser console logs (F12)
   - System information (OS, Python version)
   - Steps to reproduce the issue

3. **Common Support Requests**:
   - Include specific error messages
   - Mention when the issue started
   - List what you've already tried
   - Provide system specifications

---

**Testing Guide Version**: 1.0  
**Last Updated**: November 2025  
**Compatibility**: All browsers and operating systems