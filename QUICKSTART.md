# 🚀 Quick Start Guide

Get your LAN Project Control Dashboard up and running in 5 minutes!

## ⚡ Quick Installation (3 Steps)

### Step 1: Install Python Dependencies

```bash
# Navigate to the project directory
cd lan_project_dashboard

# Install required packages
pip install streamlit pandas numpy plotly openpyxl scipy
```

### Step 2: Prepare Your Data

**Option A: Use Existing Data**
- Place your Excel file in the project directory
- Update the path in `data_loader.py`:
  ```python
  def get_sample_data_path():
      return 'YOUR_FILE_NAME.xlsx'  # Change this
  ```

**Option B: Upload via Web Interface**
- Start the app (Step 3)
- Use the sidebar file uploader
- Upload your Excel file directly

### Step 3: Run the Dashboard

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📊 Dashboard Overview

### Available Dashboards

1. **Executive Overview** 📈
   - High-level project summary
   - Key metrics at a glance
   - Timeline visualization

2. **Project Management** 🏗️
   - Site completion tracking
   - Installation progress
   - Delay analysis
   - Completion estimation

3. **Material Consumption** 📦
   - Cable usage analysis
   - Equipment deployment
   - Outlier detection
   - District-wise breakdown

4. **Delay Risk Analysis** ⚠️
   - Risk categorization
   - Delayed sites tracking
   - Heatmap analysis
   - At-risk sites monitoring

## 🎯 First Time Usage

### 1. Launch the Dashboard
```bash
streamlit run app.py
```

### 2. Navigate Using Sidebar
- Select dashboard from radio buttons
- Use filters to refine data
- Click "Refresh Data" to reload

### 3. Interact with Charts
- Hover for detailed information
- Click legend items to show/hide
- Zoom and pan on charts
- Download charts as images

## 🔧 Configuration

### Custom Data File Location

Edit `data_loader.py`:

```python
def get_sample_data_path():
    return '/path/to/your/data.xlsx'
```

### Adjust Dashboard Settings

In `app.py`, modify:

```python
# Page title
page_title="Your Company Dashboard"

# Default dashboard
dashboard = st.sidebar.radio(
    "Select Dashboard",
    [...],
    index=0  # Change default selection
)
```

## 💡 Common Tasks

### View Project Status
1. Select "Executive Overview"
2. Check completion gauge
3. Review risk distribution

### Find Delayed Sites
1. Select "Delay Risk Analysis"
2. Adjust delay threshold slider
3. Review flagged sites table

### Analyze Material Usage
1. Select "Material Consumption"
2. Check cable per node chart
3. Review outlier sites

### Estimate Completion Date
1. Select "Project Management"
2. Scroll to "Projected Completion"
3. View estimated completion date

## 🐛 Troubleshooting

### Dashboard Won't Start

**Error: ModuleNotFoundError**
```bash
# Install missing package
pip install PACKAGE_NAME
```

**Error: Port already in use**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Data Not Loading

**Check file path:**
```python
# In data_loader.py
print("Looking for file at:", get_sample_data_path())
```

**Use file uploader:**
- Click "Browse files" in sidebar
- Upload your Excel file

### Charts Not Displaying

**Clear cache:**
- Click "Refresh Data" button in sidebar
- Restart the application

## 📝 Data Requirements

### Minimum Required Columns
- Site ID
- District name
- Site name
- LAN Nodes count
- Delivery date
- Installation date (can have nulls)

### Recommended Columns
- Cable meters
- Switch counts
- Rack counts
- Other equipment data

## 🎨 Customization

### Change Color Scheme

In `visualizations.py`:
```python
# Modify color scales
colorscale='RdYlGn'  # Red-Yellow-Green
colorscale='Viridis'  # Purple-Yellow
colorscale='Blues'    # Blue gradient
```

### Add Custom Metrics

In `calculations.py`:
```python
class ProjectMetrics:
    def get_my_custom_metric(self):
        # Your calculation here
        return result
```

Then use in `app.py`:
```python
custom_metric = pm.get_my_custom_metric()
st.metric("Custom Metric", custom_metric)
```

## 📊 Sample Data Structure

```
| Sr. No. | District   | Site Name      | LAN Nodes | Delivery Date | Installation Date |
|---------|------------|----------------|-----------|---------------|-------------------|
| 1       | District A | Court Complex 1| 32        | 2024-01-15    | 2024-01-20        |
| 2       | District B | Court Complex 2| 48        | 2024-01-16    | 2024-01-25        |
| 3       | District A | Court Complex 3| 16        | 2024-01-17    | (blank)           |
```

## 🚀 Next Steps

1. ✅ Run the test script: `python test_installation.py`
2. ✅ Start the dashboard: `streamlit run app.py`
3. ✅ Upload your data via sidebar
4. ✅ Explore the dashboards
5. ✅ Customize as needed

## 📚 Additional Resources

- **Full Documentation:** See `README.md`
- **Deployment Guide:** See `DEPLOYMENT.md`
- **Architecture Details:** See `ARCHITECTURE.md`
- **Streamlit Docs:** https://docs.streamlit.io/

## 💬 Getting Help

If you encounter issues:

1. Check error messages in terminal
2. Review `ARCHITECTURE.md` for technical details
3. Verify data format matches requirements
4. Check file paths are correct
5. Ensure all dependencies are installed

## 🎉 You're Ready!

Your dashboard is now set up and ready to use. Start by running:

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

Happy monitoring! 📊✨
