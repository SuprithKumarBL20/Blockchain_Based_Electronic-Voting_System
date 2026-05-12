# Secure Blockchain-Based Voting System - Setup Guide

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space
- **Camera**: Required for face recognition authentication
- **Internet**: Required for initial setup and face model download

### Software Dependencies
- Python 3.8+
- pip (Python package manager)
- Git (for version control)
- Web browser (Chrome, Firefox, Safari, Edge)

## Installation Steps

### Step 1: Install Python

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and check "Add Python to PATH"
3. Verify installation: Open Command Prompt and run:
   ```cmd
   python --version
   ```
   Python 3.13.7 

#### macOS
1. Install Homebrew if not already installed:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```bash
   brew install python
   ```
3. Verify installation:
   ```bash
   python3 --version
   ```

#### Linux (Ubuntu/Debian)
1. Update package list:
   ```bash
   sudo apt update
   ```
2. Install Python:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```
3. Verify installation:
   ```bash
   python3 --version
   ```

### Step 2: Download the Project

#### Option A: Download ZIP
1. Download the project ZIP file
2. Extract to your desired location (e.g., `C:\Projects\voting-system`)

#### Option B: Clone with Git
```bash
git clone <repository-url>
cd secure-voting-system
```

### Step 3: Set Up Virtual Environment

#### Windows
```cmd
cd secure-voting-system
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
cd secure-voting-system
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

1. Make sure you're in the project directory and virtual environment is activated
2. Install all required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Expected installation time: 5-10 minutes depending on your internet speed

### Step 5: Download Face Recognition Model

The face recognition model should be included in the project, but if missing:

1. Create the `ai/` directory if it doesn't exist:
   ```bash
   mkdir ai
   ```

2. The model file `model.onnx` should be present in the `ai/` directory
3. If missing, contact the project administrator for the model file

### Step 6: Initialize Database

1. The database will be created automatically when you first run the application
2. Default admin account will be created with credentials:
   - Username: `admin`
   - Password: `admin123`

### Step 7: Configure Network Access

The application is pre-configured for network access. To access from other devices:

1. Find your computer's IP address:
   - **Windows**: Open Command Prompt and run `ipconfig`
   - **macOS/Linux**: Run `ifconfig` or `ip addr`

2. Look for your local IP address (usually starts with 192.168.x.x)

3. The application will be accessible at:
   - Local: `http://127.0.0.1:5000`
   - Network: `http://YOUR_IP:5000`

### Step 8: Run the Application

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. You should see output like:
   ```
   Starting Secure Voting System...
   Admin credentials: username='admin', password='admin123'
   Visit: http://localhost:5000
   ```

3. Open your web browser and navigate to:
   - Local access: `http://localhost:5000`
   - Network access: `http://YOUR_IP:5000`

## Verification Steps

### 1. Test Basic Access
- Open browser and go to `http://localhost:5000`
- You should see the voting system homepage

### 2. Test Admin Access
- Go to `http://localhost:5000/admin/login`
- Login with username: `admin`, password: `admin123`
- You should see the admin dashboard

### 3. Test Network Access
- From another device on the same network, open browser
- Navigate to `http://YOUR_IP:5000`
- Should display the same homepage

### 4. Test Camera Access
- Go to registration page
- Allow camera permissions when prompted
- You should see camera feed for face capture

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
**Error**: `Address already in use`
**Solution**: 
- Find process using port 5000:
  - Windows: `netstat -ano | findstr :5000`
  - macOS/Linux: `lsof -i :5000`
- Kill the process or change port in `app.py`

#### 2. Camera Not Working
**Error**: Camera not detected or permission denied
**Solution**:
- Check camera connection and drivers
- Allow browser permission for camera
- Try different browser
- Check if another app is using camera

#### 3. Face Recognition Model Missing
**Error**: Model file not found
**Solution**:
- Ensure `ai/model.onnx` exists
- Download model file if missing
- Check file permissions

#### 4. Database Errors
**Error**: Database locked or corrupted
**Solution**:
- Delete `database/db.sqlite3` file
- Restart application to recreate database
- Check disk space and permissions

#### 5. Python Module Errors
**Error**: Module not found
**Solution**:
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`
- Check Python version compatibility

#### 6. Network Access Issues
**Error**: Cannot access from other devices
**Solution**:
- Check firewall settings
- Ensure devices are on same network
- Verify IP address is correct
- Try disabling VPN if active

### Performance Optimization

#### 1. Slow Loading
- Check internet connection
- Clear browser cache
- Restart the application
- Check system resources (RAM/CPU)

#### 2. Face Recognition Slow
- Ensure good lighting conditions
- Check camera quality
- Close other camera-using applications
- Restart browser if needed

#### 3. Database Performance
- Regular database cleanup
- Index optimization
- Connection pooling
- Query optimization

## Security Considerations

### Development Environment
- Change default admin password immediately
- Use strong passwords for all accounts
- Keep software dependencies updated
- Regular security audits recommended

### Production Deployment
- Use environment variables for sensitive data
- Enable HTTPS with SSL certificates
- Implement proper firewall rules
- Regular backups of database
- Monitor access logs

## Next Steps

### For Development
- Explore the admin dashboard features
- Test the voting process end-to-end
- Customize the UI/UX as needed
- Add new features or modify existing ones

### For Production
- Set up proper web server (Nginx/Apache)
- Configure SSL certificates
- Set up automated backups
- Implement monitoring and alerting
- Regular security updates

## Support

If you encounter issues not covered in this guide:

1. Check the `TECHNICAL_DETAILS.txt` file for detailed technical information
2. Review the `PROJECT_ARCHITECTURE.md` for system overview
3. Check the troubleshooting section in this guide
4. Ensure all prerequisites are met
5. Verify all installation steps were followed correctly

For additional support, contact the project administrator with:
- Error messages and screenshots
- System information (OS, Python version)
- Steps to reproduce the issue
- Browser console logs if applicable

---

**Setup Guide Version**: 1.0  
**Last Updated**: November 2025  
**Compatibility**: Python 3.8+, Windows/macOS/Linux