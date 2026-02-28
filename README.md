# 🏗️ LAN Infrastructure Project Control Dashboard

A comprehensive, production-ready project control dashboard for monitoring LAN infrastructure deployment across multiple sites. Built with Python, Streamlit, Pandas, and Plotly.

## 📊 Features

### 1. **Executive Overview Dashboard**
- Real-time project status at a glance
- Key performance indicators (KPIs)
- Project progress visualization
- Material and risk summaries
- Interactive timeline view

### 2. **Project Management Dashboard**
- **KPIs:**
  - Total Sites
  - Completed Sites
  - Pending Sites
  - Delayed Sites
  - Average Installation Delay
  - Phase Completion Percentage

- **Visualizations:**
  - Completion gauge chart
  - District-wise completion breakdown
  - Installation trend over time
  - Top 10 delayed sites table

- **Advanced Features:**
  - Projected completion date estimation
  - Current installation rate tracking
  - Completion forecast based on historical data

### 3. **Material Consumption Dashboard**
- **Metrics:**
  - Total LAN Nodes deployed
  - Total Cable Used (meters)
  - Average Cable per Node
  - Switch per Node ratio
  - Rack per Site ratio

- **Analysis:**
  - Cable consumption scatter plot
  - Statistical outlier detection (Z-score method)
  - Flagged sites with unusual consumption
  - District-wise material breakdown

- **Interactive Filters:**
  - District selection
  - Customizable outlier threshold

### 4. **Delay Risk Dashboard**
- **Risk Analysis:**
  - Sites categorized by risk level (Low/Medium/High)
  - Risk distribution pie chart
  - Delay histogram distribution

- **Risk Categories:**
  - **Low Risk:** 0-3 days delay
  - **Medium Risk:** 4-7 days delay
  - **High Risk:** 8+ days delay

- **Features:**
  - District-wise delay heatmap
  - Sites delivered but not installed
  - Customizable delay threshold slider
  - At-risk sites table

## 🏗️ Project Architecture

```
lan_project_dashboard/
│
├── app.py                  # Main Streamlit application
├── data_loader.py          # Excel data loading and preprocessing
├── calculations.py         # Metric calculation and analysis
├── visualizations.py       # Plotly chart generation
├── utils.py               # Utility functions and helpers
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── DEPLOYMENT.md         # Deployment instructions
└── ARCHITECTURE.md       # Technical architecture details
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone or download the project:**
```bash
cd lan_project_dashboard
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Prepare your data:**
   - Place your Excel file in the project directory, or
   - Update the file path in `data_loader.py` (function `get_sample_data_path()`)

5. **Run the dashboard:**
```bash
streamlit run app.py
```

6. **Access the dashboard:**
   - Open your browser and navigate to: `http://localhost:8501`

## 📁 Data Requirements

### Excel File Structure

The dashboard expects an Excel file with the following structure:

**Required Columns:**
- `Sr. No.` - Site ID
- `Name of the Judicial District` - District name
- `Name of Court Complex` - Site name
- `Lan Nodes to be provided` - Number of LAN nodes
- `8 Port Switch` - Number of 8-port switches
- `24 Port Switch` - Number of 24-port switches
- `Cat-6 Cable (mtr)` - Cable length in meters
- `Date of Delivery` - Material delivery date
- `Date of Installation` - Installation completion date

**Optional Columns:**
- `Patch Panel (24 Port)` - Patch panels
- `I/O (Box,Face plate)` - I/O boxes
- `1 mtr Patch Cord` - 1m patch cords
- `3 mtr Patch Cord` - 3m patch cords
- `6U Rack` - Rack units

### Data Format Notes
- Dates should be in recognizable date format
- Numeric fields should contain numbers only
- Missing values are handled gracefully
- The system automatically cleans and validates data

## 📊 Dashboard Usage

### Navigation
Use the sidebar to switch between dashboards:
1. **Executive Overview** - High-level summary
2. **Project Management** - Detailed progress tracking
3. **Material Consumption** - Material analysis
4. **Delay Risk Analysis** - Risk management

### Interactive Features

**Filters:**
- District selection (Material Dashboard)
- Delay threshold slider (Risk Dashboard)
- Outlier detection threshold (Material Dashboard)

**Data Upload:**
- Upload custom Excel files via sidebar
- Automatic data processing and validation

**Refresh:**
- Click "Refresh Data" to reload the dashboard

## 🎯 Key Metrics Explained

### Project Metrics
- **Completion %:** (Completed Sites / Total Sites) × 100
- **Average Delay:** Mean of (Installation Date - Delivery Date) for completed sites
- **Delayed Sites:** Count of sites with positive delay

### Material Metrics
- **Cable per Node:** Total Cable / Total LAN Nodes
- **Switch per Node Ratio:** Total Switches / Total LAN Nodes
- **Outlier Detection:** Sites with Z-score > threshold (default: 2)

### Risk Metrics
- **Risk Category:** Based on delay duration
- **At-Risk Sites:** Delivered but not installed OR delayed beyond threshold

## 🔧 Customization

### Modifying Metrics
Edit `calculations.py` to add new metrics or modify existing ones.

### Adding Visualizations
Add new chart functions in `visualizations.py` using Plotly.

### Changing Styles
Modify the CSS in `app.py` under the `st.markdown()` section.

### Data Source
Update `get_sample_data_path()` in `data_loader.py` to change the default data file.

## 📈 Advanced Features

### Projected Completion
The system automatically estimates project completion based on:
- Current installation rate (sites per week)
- Remaining pending sites
- Historical installation trend

### Outlier Detection
Uses statistical Z-score method to identify sites with unusual material consumption:
- Z-score > 2: Flagged as outlier
- Helps identify data quality issues or exceptional cases

### Real-time Updates
- Data is cached for performance
- Click "Refresh Data" to reload
- Supports live Excel file updates

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt --upgrade
```

**2. File Not Found**
- Check the file path in `data_loader.py`
- Ensure Excel file is in the correct location
- Use the file uploader in the sidebar

**3. Date Parsing Issues**
- Ensure date columns are in proper date format
- Check for invalid date values
- The system will show errors for unparseable dates

**4. Missing Data**
- The dashboard handles missing values gracefully
- Check the "Data Information" section in sidebar
- Review data validation warnings

## 📝 License

This project is open-source and available for use in infrastructure project management.

## 👥 Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the architecture documentation
3. Submit an issue on the project repository

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Plotly Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 🚀 Future Enhancements

Potential features for future versions:
- [ ] Cost & margin analysis (when cost data available)
- [ ] Export reports to PDF/Excel
- [ ] Email notifications for at-risk sites
- [ ] Multi-phase project support
- [ ] User authentication
- [ ] Mobile responsive design
- [ ] Integration with project management tools
- [ ] Real-time data synchronization
- [ ] Predictive analytics with ML

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Built with:** Python, Streamlit, Plotly, Pandas, NumPy
