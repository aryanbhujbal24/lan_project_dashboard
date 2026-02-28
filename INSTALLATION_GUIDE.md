# 📦 Complete Installation Guide

## 🎯 Overview

This guide will help you set up the LAN Project Control Dashboard on your local machine or deploy it to a cloud platform.

## 📋 Prerequisites

### Required Software
- **Python 3.8 or higher** ([Download](https://www.python.org/downloads/))
- **pip** (Python package installer - comes with Python)
- **Git** (optional, for version control)

### System Requirements
- **RAM:** 2GB minimum, 4GB recommended
- **Storage:** 500MB free space
- **OS:** Windows, macOS, or Linux
- **Browser:** Chrome, Firefox, Safari, or Edge

## 🚀 Installation Steps

### Step 1: Extract the Project Files

If you received a ZIP file:
```bash
# Windows (PowerShell)
Expand-Archive lan_project_dashboard.zip -DestinationPath C:\Projects\

# macOS/Linux
unzip lan_project_dashboard.zip -d ~/Projects/
cd ~/Projects/lan_project_dashboard
```

If using Git:
```bash
git clone https://github.com/yourusername/lan-project-dashboard.git
cd lan-project-dashboard
```

### Step 2: Set Up Python Environment

**Option A: Using Virtual Environment (Recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate
```

**Option B: Global Installation (Not Recommended)**
```bash
# Skip virtual environment
# Install packages globally
```

### Step 3: Install Dependencies

```bash
# Ensure you're in the project directory
cd lan_project_dashboard

# Install all required packages
pip install -r requirements.txt

# If you encounter SSL errors, try:
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Manual Installation (if requirements.txt fails):**
```bash
pip install streamlit==1.31.0
pip install pandas==2.1.4
pip install numpy==1.26.3
pip install plotly==5.18.0
pip install openpyxl==3.1.2
pip install scipy==1.11.4
```

### Step 4: Verify Installation

Run the test script:
```bash
python test_installation.py
```

Expected output:
```
======================================================================
LAN PROJECT DASHBOARD - INSTALLATION TEST
======================================================================
Testing package imports...
  ✓ Streamlit imported successfully
  ✓ Pandas imported successfully
  ✓ NumPy imported successfully
  ✓ Plotly imported successfully
  ✓ SciPy imported successfully
  ✓ OpenPyXL imported successfully

Testing custom modules...
  ✓ data_loader.py imported successfully
  ✓ calculations.py imported successfully
  ✓ visualizations.py imported successfully
  ✓ utils.py imported successfully

...
======================================================================
Results: 6/6 tests passed

✓ All tests passed! The dashboard is ready to run.
```

### Step 5: Configure Data Source

**Option A: Update File Path (Recommended for fixed location)**

Edit `data_loader.py`:
```python
def get_sample_data_path():
    # Change this to your file path
    return '/path/to/your/Lan_Nodes_1424_Phase__2_3_1.xlsx'
    
    # Windows example:
    # return r'C:\Data\Lan_Nodes_1424_Phase__2_3_1.xlsx'
    
    # macOS/Linux example:
    # return '/Users/yourname/Documents/Lan_Nodes_1424_Phase__2_3_1.xlsx'
```

**Option B: Use File Upload (Recommended for flexible location)**
- Leave the path as is
- Upload file via the web interface when running

### Step 6: Run the Dashboard

```bash
streamlit run app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

The dashboard will automatically open in your default browser.

## 🔧 Configuration

### Change Default Port

If port 8501 is already in use:
```bash
streamlit run app.py --server.port 8080
```

### Configure Streamlit Settings

Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 200
```

### Set Environment Variables

For production deployments:

**Windows:**
```cmd
set STREAMLIT_SERVER_PORT=8501
set STREAMLIT_SERVER_HEADLESS=true
```

**macOS/Linux:**
```bash
export STREAMLIT_SERVER_PORT=8501
export STREAMLIT_SERVER_HEADLESS=true
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "Python not found"
**Solution:**
```bash
# Verify Python installation
python --version
# or
python3 --version

# Add Python to PATH (Windows)
# System Properties > Environment Variables > Path > Add Python installation directory
```

#### Issue 2: "pip not recognized"
**Solution:**
```bash
# Verify pip installation
python -m pip --version

# Upgrade pip
python -m pip install --upgrade pip
```

#### Issue 3: "Permission denied" (macOS/Linux)
**Solution:**
```bash
# Use --user flag
pip install --user -r requirements.txt

# Or use sudo (not recommended)
sudo pip install -r requirements.txt
```

#### Issue 4: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:**
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt
```

#### Issue 5: "Excel file not found"
**Solution:**
1. Check file path in `data_loader.py`
2. Use absolute path instead of relative path
3. Or use the file uploader in the web interface

#### Issue 6: "Port 8501 already in use"
**Solution:**
```bash
# Kill existing process (Windows)
netstat -ano | findstr :8501
taskkill /PID [PID] /F

# Kill existing process (macOS/Linux)
lsof -i :8501
kill -9 [PID]

# Or use different port
streamlit run app.py --server.port 8502
```

#### Issue 7: "Data not displaying in charts"
**Solution:**
1. Click "Refresh Data" button
2. Check console for error messages
3. Verify data format matches requirements
4. Clear browser cache (Ctrl+Shift+Delete)

#### Issue 8: "Slow performance"
**Solution:**
1. Reduce data size by filtering
2. Increase system memory
3. Close other applications
4. Clear Streamlit cache: `st.cache_data.clear()`

## 📊 Data Preparation

### Excel File Format

Your Excel file should have these columns:

**Required:**
- `Sr. No.` - Site identifier
- `Name of the Judicial District` - District name
- `Name of Court Complex` - Site name
- `Lan Nodes to be provided` - Number of nodes
- `Date of Delivery` - Delivery date
- `Date of Installation` - Installation date

**Optional:**
- `8 Port Switch`, `24 Port Switch`
- `Cat-6 Cable (mtr)` - Cable in meters
- `Patch Panel (24 Port)`
- `6U Rack`

### Data Validation Checklist

- [ ] Dates in proper date format (not text)
- [ ] Numbers in numeric format (no commas)
- [ ] No merged cells
- [ ] No blank rows at top (except title row)
- [ ] Column headers in row 3
- [ ] Consistent district names
- [ ] Valid site IDs

## 🌐 Network Deployment

### Local Network Access

To allow access from other devices on your network:

```bash
# Run with network access enabled
streamlit run app.py --server.address 0.0.0.0

# Access from other devices
# http://YOUR_IP_ADDRESS:8501
```

Find your IP address:
```bash
# Windows
ipconfig

# macOS/Linux
ifconfig
# or
ip addr show
```

### Firewall Configuration

**Windows:**
1. Windows Defender Firewall > Advanced Settings
2. Inbound Rules > New Rule
3. Port > TCP > 8501
4. Allow the connection

**macOS:**
```bash
# Allow incoming connections
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /usr/local/bin/streamlit
```

**Linux (ufw):**
```bash
sudo ufw allow 8501/tcp
```

## 📱 Mobile Access

The dashboard is mobile-responsive. Access it from mobile devices:

1. Ensure device is on same network
2. Open browser on mobile
3. Navigate to: `http://YOUR_COMPUTER_IP:8501`

## 🔒 Security Recommendations

### For Production Use

1. **Add Authentication:**
   - Implement login system
   - Use environment variables for credentials

2. **Enable HTTPS:**
   - Use reverse proxy (Nginx, Apache)
   - Obtain SSL certificate

3. **Restrict Access:**
   - Firewall rules
   - VPN for remote access
   - IP whitelisting

4. **Data Protection:**
   - Regular backups
   - Encrypted storage
   - Access logging

## 📚 Next Steps

After successful installation:

1. ✅ Read `QUICKSTART.md` for basic usage
2. ✅ Review `README.md` for full features
3. ✅ Check `DEPLOYMENT.md` for cloud deployment
4. ✅ Explore `ARCHITECTURE.md` for customization

## 💡 Quick Commands Reference

```bash
# Start dashboard
streamlit run app.py

# Start with custom port
streamlit run app.py --server.port 8080

# Start with network access
streamlit run app.py --server.address 0.0.0.0

# Run tests
python test_installation.py

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Update packages
pip install --upgrade -r requirements.txt

# Clear Streamlit cache
rm -rf ~/.streamlit/cache
```

## 🎓 Learning Resources

- **Streamlit Documentation:** https://docs.streamlit.io/
- **Pandas Tutorial:** https://pandas.pydata.org/docs/user_guide/
- **Plotly Guide:** https://plotly.com/python/
- **Python Documentation:** https://docs.python.org/3/

## 📞 Support

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review error messages in terminal
3. Check `ARCHITECTURE.md` for technical details
4. Verify all dependencies are installed correctly

## ✅ Installation Checklist

Before starting:
- [ ] Python 3.8+ installed
- [ ] pip installed and updated
- [ ] Project files extracted
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Test script passed
- [ ] Data file configured
- [ ] Dashboard started successfully

## 🎉 Success!

You're all set! Your LAN Project Control Dashboard is now ready to use.

Run this command to get started:
```bash
streamlit run app.py
```

Enjoy monitoring your infrastructure projects! 📊✨
