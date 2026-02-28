# 🏗️ Technical Architecture

Comprehensive technical documentation for the LAN Project Control Dashboard.

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Data Flow](#data-flow)
3. [Module Structure](#module-structure)
4. [Design Patterns](#design-patterns)
5. [Performance Optimization](#performance-optimization)
6. [Extension Guidelines](#extension-guidelines)

---

## 🎯 System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                    (Streamlit Web UI)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                          │
│                      (app.py)                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Dashboard   │  │  Dashboard   │  │  Dashboard   │     │
│  │  Manager     │  │  Renderer    │  │  Controller  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                      │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │  calculations │  │visualizations │  │     utils     │  │
│  │  .py          │  │     .py       │  │     .py       │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                        │
│                    (data_loader.py)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  DataLoader  │  │  Validator   │  │  Transformer │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCE                             │
│              (Excel File / Database)                        │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Web UI framework |
| **Visualization** | Plotly | Interactive charts |
| **Data Processing** | Pandas, NumPy | Data manipulation |
| **Statistics** | SciPy | Statistical analysis |
| **Data Source** | Excel (openpyxl) | Data storage |

---

## 🔄 Data Flow

### Data Loading Process

```
1. Excel File
   │
   ▼
2. DataLoader.load_data()
   - Reads Excel with pandas
   - Skips header rows
   - Returns raw DataFrame
   │
   ▼
3. DataLoader.preprocess_data()
   - clean_column_names()
   - validate_and_clean_data()
   - Type conversions
   - Date parsing
   │
   ▼
4. Cached DataFrame
   - Stored in Streamlit cache
   - Reused across reruns
   │
   ▼
5. Metric Calculations
   - ProjectMetrics
   - MaterialMetrics
   - DelayRiskAnalyzer
   │
   ▼
6. Visualizations
   - Plotly charts
   - Tables
   - KPI cards
   │
   ▼
7. User Interface
   - Streamlit components
   - Interactive filters
   - Real-time updates
```

### Calculation Pipeline

```python
# Example: Project Metrics Pipeline

df (raw) 
  → calculate_delay_days()
  → categorize_delay_risk()
  → ProjectMetrics(df)
    → _calculate_derived_fields()
      - delay_days
      - cable_per_node
      - switch_per_node
      - delay_risk
    → get_kpis()
      - total_sites
      - completed_sites
      - avg_delay
      - completion_pct
    → get_district_completion()
    → get_installation_trend()
    → get_top_delayed_sites()
```

---

## 📦 Module Structure

### 1. data_loader.py

**Purpose:** Data loading, validation, and preprocessing

**Classes:**
```python
class DataLoader:
    """
    Handles all data loading operations
    """
    
    def __init__(self, file_path: str)
    def get_available_sheets(self) -> list
    def load_data(self, sheet_name: str, skiprows: int) -> pd.DataFrame
    def preprocess_data(self) -> pd.DataFrame
    def load_and_process(self, sheet_name: str, skiprows: int) -> pd.DataFrame
    def get_data_summary(self) -> dict
    def get_column_info(self) -> pd.DataFrame
```

**Key Functions:**
- `load_project_data()`: Convenience function for quick loading
- `get_sample_data_path()`: Returns default data path

**Data Validation:**
1. Remove empty rows
2. Filter invalid site IDs
3. Convert data types
4. Parse dates
5. Clean text fields

### 2. calculations.py

**Purpose:** Business logic and metric calculations

**Classes:**

#### ProjectMetrics
```python
class ProjectMetrics:
    """
    Project management metrics and KPIs
    """
    
    def __init__(self, df: pd.DataFrame)
    def _calculate_derived_fields(self)
    def get_kpis(self) -> dict
    def get_district_completion(self) -> pd.DataFrame
    def get_installation_trend(self) -> pd.DataFrame
    def get_top_delayed_sites(self, n: int) -> pd.DataFrame
    def get_at_risk_sites(self, delay_threshold: int) -> pd.DataFrame
```

**Calculated Fields:**
- `delay_days` = installation_date - delivery_date
- `delay_risk` = categorize_delay_risk(delay_days)

**KPIs:**
- Total sites
- Completed sites (installation_date not null)
- Pending sites
- Delayed sites (delay_days > 0)
- Average delay
- Completion percentage

#### MaterialMetrics
```python
class MaterialMetrics:
    """
    Material consumption analysis
    """
    
    def __init__(self, df: pd.DataFrame)
    def _calculate_material_metrics(self)
    def get_material_summary(self) -> dict
    def detect_cable_outliers(self, threshold: float) -> pd.DataFrame
    def get_district_material_summary(self) -> pd.DataFrame
```

**Calculated Metrics:**
- `cable_per_node` = cable_meters / lan_nodes
- `total_switches` = switch_8port + switch_24port
- `switch_per_node` = total_switches / lan_nodes

**Outlier Detection:**
- Method: Z-score
- Formula: z = (x - μ) / σ
- Threshold: configurable (default: 2)

#### DelayRiskAnalyzer
```python
class DelayRiskAnalyzer:
    """
    Delay risk analysis and categorization
    """
    
    def __init__(self, df: pd.DataFrame)
    def get_risk_distribution(self) -> pd.DataFrame
    def get_district_delay_heatmap_data(self) -> pd.DataFrame
    def get_sites_by_delay_threshold(self, min_delay: int) -> pd.DataFrame
```

**Risk Categories:**
```python
def categorize_delay_risk(delay_days):
    if delay_days < 0:     return 'Early'
    elif delay_days <= 3:  return 'Low'
    elif delay_days <= 7:  return 'Medium'
    else:                  return 'High'
```

### 3. visualizations.py

**Purpose:** All Plotly chart generation

**Chart Functions:**

| Function | Chart Type | Purpose |
|----------|-----------|---------|
| `create_completion_gauge()` | Gauge | Project completion % |
| `create_district_completion_bar()` | Horizontal Bar | District progress |
| `create_installation_trend()` | Line + Bar | Timeline analysis |
| `create_delay_distribution()` | Histogram | Delay patterns |
| `create_risk_category_pie()` | Pie | Risk distribution |
| `create_material_consumption_bars()` | Bar | Material totals |
| `create_district_heatmap()` | Heatmap | Delay by district |
| `create_cable_per_node_scatter()` | Scatter | Consumption analysis |
| `create_kpi_cards_figure()` | Indicators | KPI display |
| `create_timeline_gantt()` | Gantt | Project timeline |

**Chart Features:**
- Interactive tooltips
- Color-coded values
- Responsive design
- Professional styling
- Export capabilities (built into Plotly)

### 4. utils.py

**Purpose:** Helper functions and utilities

**Key Functions:**

```python
# Data Cleaning
clean_column_names(df) -> pd.DataFrame
validate_and_clean_data(df) -> pd.DataFrame

# Calculations
calculate_delay_days(df) -> pd.Series
categorize_delay_risk(delay_days) -> str
detect_outliers_zscore(series, threshold) -> pd.Series

# Formatting
format_number(num) -> str
calculate_completion_percentage(total, completed) -> float
get_status_color(value, thresholds) -> str

# Projections
estimate_completion_date(df, current_date) -> dict

# Export
export_to_excel(dataframes_dict, filename)
```

**Estimation Algorithm:**
```python
def estimate_completion_date(df):
    """
    1. Count completed and pending sites
    2. Calculate date range of installations
    3. Compute installation rate (sites/day)
    4. Project remaining days: pending / rate
    5. Add to current date
    """
```

### 5. app.py

**Purpose:** Main application and UI orchestration

**Structure:**
```python
# Configuration
st.set_page_config(...)

# Custom CSS
st.markdown("""<style>...</style>""")

# Data Loading
@st.cache_data
def load_data(file_path) -> pd.DataFrame

# Dashboard Functions
def show_overview_dashboard(df)
def show_project_management_dashboard(df)
def show_material_consumption_dashboard(df)
def show_delay_risk_dashboard(df)

# Main Function
def main():
    # Header
    # Sidebar navigation
    # Data loading
    # Dashboard selection
    # Display selected dashboard
    # Footer
```

**Caching Strategy:**
```python
@st.cache_data
def load_data(file_path):
    """
    Caches data in memory
    - Cleared on file change
    - Cleared on refresh button
    - Shared across sessions
    """
```

---

## 🎨 Design Patterns

### 1. **Class-Based Metrics (Strategy Pattern)**

Each metric category is a separate class:
```python
pm = ProjectMetrics(df)  # Project metrics
mm = MaterialMetrics(df)  # Material metrics
dra = DelayRiskAnalyzer(df)  # Risk analysis
```

**Benefits:**
- Separation of concerns
- Easy to extend
- Testable
- Reusable

### 2. **Lazy Calculation**

Derived fields calculated once in `__init__`:
```python
class ProjectMetrics:
    def __init__(self, df):
        self.df = df.copy()
        self._calculate_derived_fields()  # Once
    
    def get_kpis(self):
        # Use pre-calculated fields
        return self.df['delay_days'].mean()
```

### 3. **Functional Composition**

Small, composable functions:
```python
# Instead of monolithic function
def process_data(df):
    df = clean_column_names(df)
    df = validate_and_clean_data(df)
    df['delay'] = calculate_delay_days(df)
    return df
```

### 4. **Data Caching**

Streamlit's caching for performance:
```python
@st.cache_data
def load_data(file_path):
    # Expensive operation cached
    return DataLoader(file_path).load_and_process()
```

### 5. **Dashboard Factory**

Each dashboard is a function:
```python
def show_project_management_dashboard(df):
    # Render project dashboard
    pass

# Called based on user selection
dashboards = {
    "Project Management": show_project_management_dashboard,
    "Material Consumption": show_material_consumption_dashboard,
}

dashboards[selected_dashboard](df)
```

---

## ⚡ Performance Optimization

### 1. **Data Caching**

```python
# Cache expensive operations
@st.cache_data
def load_data(file_path):
    return DataLoader(file_path).load_and_process()

# Manual cache clearing
if st.sidebar.button("Refresh"):
    st.cache_data.clear()
    st.rerun()
```

### 2. **Efficient Data Structures**

```python
# Use vectorized operations (Pandas/NumPy)
df['delay_days'] = (df['installation_date'] - df['delivery_date']).dt.days

# Instead of:
# df['delay_days'] = df.apply(lambda row: (row['installation_date'] - row['delivery_date']).days, axis=1)
```

### 3. **Lazy Loading**

Only calculate what's displayed:
```python
if dashboard == "Project Management":
    pm = ProjectMetrics(df)  # Only when needed
    kpis = pm.get_kpis()
```

### 4. **Memory Management**

```python
# Copy only when necessary
def __init__(self, df):
    self.df = df.copy()  # Prevents side effects

# Use views when possible
filtered_df = df[df['district'] == 'Selected']  # View, not copy
```

### 5. **Chart Optimization**

```python
# Limit data points in visualizations
def create_timeline_gantt(df, max_sites=20):
    gantt_df = df.head(max_sites)  # Limit for performance
```

---

## 🔧 Extension Guidelines

### Adding a New Dashboard

1. **Create Dashboard Function:**
```python
def show_my_new_dashboard(df):
    st.markdown("### My New Dashboard")
    
    # Calculate metrics
    # Create visualizations
    # Display results
```

2. **Add to Navigation:**
```python
dashboard = st.sidebar.radio(
    "Select Dashboard",
    [..., "My New Dashboard"]
)

# Add to dispatcher
if dashboard == "My New Dashboard":
    show_my_new_dashboard(df)
```

### Adding a New Metric

1. **Add to Appropriate Class:**
```python
class ProjectMetrics:
    def get_my_new_metric(self):
        # Calculate metric
        return result
```

2. **Use in Dashboard:**
```python
def show_project_management_dashboard(df):
    pm = ProjectMetrics(df)
    new_metric = pm.get_my_new_metric()
    st.metric("New Metric", new_metric)
```

### Adding a New Visualization

1. **Create Chart Function:**
```python
def create_my_new_chart(data):
    fig = go.Figure()
    # Add traces
    fig.update_layout(...)
    return fig
```

2. **Use in Dashboard:**
```python
st.plotly_chart(
    create_my_new_chart(data),
    use_container_width=True
)
```

### Adding Cost & Margin Analysis

The system is designed to support cost analysis when data is available:

```python
# In calculations.py
class CostMetrics:
    def __init__(self, df):
        self.df = df
        self._validate_cost_columns()
    
    def _validate_cost_columns(self):
        required = ['cost', 'revenue']
        if not all(col in self.df.columns for col in required):
            raise ValueError("Cost/Revenue columns not found")
    
    def get_margin_analysis(self):
        df = self.df.copy()
        df['margin'] = df['revenue'] - df['cost']
        df['margin_pct'] = (df['margin'] / df['revenue'] * 100)
        return df
    
    def get_top_profitable_sites(self, n=10):
        return self.df.nlargest(n, 'margin')

# In app.py
def show_cost_margin_dashboard(df):
    try:
        cm = CostMetrics(df)
        # Display cost analysis
    except ValueError:
        st.info("Cost data not available")
```

---

## 🧪 Testing Guidelines

### Unit Testing

```python
# tests/test_calculations.py
import pytest
from calculations import ProjectMetrics

def test_kpi_calculation():
    # Arrange
    df = create_test_dataframe()
    pm = ProjectMetrics(df)
    
    # Act
    kpis = pm.get_kpis()
    
    # Assert
    assert kpis['total_sites'] == 10
    assert kpis['completion_percentage'] == 50.0
```

### Integration Testing

```python
# tests/test_integration.py
def test_full_pipeline():
    loader = DataLoader('test_data.xlsx')
    df = loader.load_and_process()
    pm = ProjectMetrics(df)
    kpis = pm.get_kpis()
    assert kpis is not None
```

---

## 📚 API Reference

### DataLoader

```python
DataLoader(file_path: str)
    .get_available_sheets() -> list
    .load_data(sheet_name: str, skiprows: int) -> pd.DataFrame
    .preprocess_data() -> pd.DataFrame
    .load_and_process(sheet_name: str, skiprows: int) -> pd.DataFrame
    .get_data_summary() -> dict
    .get_column_info() -> pd.DataFrame
```

### ProjectMetrics

```python
ProjectMetrics(df: pd.DataFrame)
    .get_kpis() -> dict
    .get_district_completion() -> pd.DataFrame
    .get_installation_trend() -> pd.DataFrame
    .get_top_delayed_sites(n: int) -> pd.DataFrame
    .get_at_risk_sites(delay_threshold: int) -> pd.DataFrame
```

### MaterialMetrics

```python
MaterialMetrics(df: pd.DataFrame)
    .get_material_summary() -> dict
    .detect_cable_outliers(threshold: float) -> pd.DataFrame
    .get_district_material_summary() -> pd.DataFrame
```

### DelayRiskAnalyzer

```python
DelayRiskAnalyzer(df: pd.DataFrame)
    .get_risk_distribution() -> pd.DataFrame
    .get_district_delay_heatmap_data() -> pd.DataFrame
    .get_sites_by_delay_threshold(min_delay: int) -> pd.DataFrame
```

---

## 🔐 Security Considerations

### Data Protection
- No hardcoded credentials
- Use environment variables for sensitive data
- Implement authentication for production
- Encrypt data in transit (HTTPS)

### Input Validation
- All user inputs validated
- File uploads sanitized
- SQL injection prevention (if using database)
- XSS prevention in displayed data

### Access Control
- Role-based access (future enhancement)
- Audit logging
- Session management

---

## 📈 Scalability Considerations

### Current Limitations
- In-memory data processing
- Single-file data source
- No concurrent user management

### Scaling Strategies

**Horizontal Scaling:**
- Deploy multiple instances
- Load balancer
- Shared data source

**Vertical Scaling:**
- Increase server resources
- Optimize memory usage
- Database backend

**Data Scaling:**
- Partition large datasets
- Use database instead of Excel
- Implement data pagination

---

## 🎯 Future Architecture

### Recommended Enhancements

1. **Database Backend:**
```python
# Replace Excel with PostgreSQL
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost/db')
df = pd.read_sql_query("SELECT * FROM sites", engine)
```

2. **API Layer:**
```python
# FastAPI backend + Streamlit frontend
# Separate data access from UI
```

3. **Microservices:**
```
- Data Service
- Analytics Service
- Reporting Service
- UI Service
```

4. **Real-time Updates:**
```python
# WebSocket for live data
# Auto-refresh on data changes
```

---

**Last Updated:** 2024  
**Architecture Version:** 1.0.0  
**Maintainer:** Development Team
