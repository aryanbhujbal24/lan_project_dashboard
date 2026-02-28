"""
LAN Project Control Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Import custom modules
from data_loader import DataLoader, get_sample_data_path
from calculations import ProjectMetrics, MaterialMetrics, DelayRiskAnalyzer
from visualizations import (
    create_completion_gauge, create_district_completion_bar,
    create_installation_trend, create_delay_distribution,
    create_risk_category_pie, create_material_consumption_bars,
    create_district_heatmap, create_cable_per_node_scatter,
    create_kpi_cards_figure, create_timeline_gantt
)
from utils import estimate_completion_date, format_number

# Page configuration
st.set_page_config(
    page_title="LAN Project Control Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
        padding-left: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: black;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(file_path):
    """Load and cache data"""
    loader = DataLoader(file_path)
    df = loader.load_and_process()
    return df


def show_project_management_dashboard(df):
    """Display Project Management Dashboard"""
    st.markdown('<div class="section-header">📊 Project Management Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Initialize metrics
    pm = ProjectMetrics(df)
    kpis = pm.get_kpis()
    
    # KPI Cards
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Sites", kpis['total_sites'])
    
    with col2:
        st.metric("Completed", kpis['completed_sites'], 
                 delta=f"{kpis['completion_percentage']:.1f}%")
    
    with col3:
        st.metric("Pending", kpis['pending_sites'])
    
    with col4:
        st.metric("Delayed", kpis['delayed_sites'])
    
    with col5:
        st.metric("Avg Delay", f"{kpis['avg_installation_delay']:.1f} days")
    
    with col6:
        completion_color = "normal" if kpis['completion_percentage'] >= 80 else "inverse"
        st.metric("Completion", f"{kpis['completion_percentage']:.1f}%")
    
    st.markdown("---")
    
    # Completion Gauge and District Completion
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.plotly_chart(
            create_completion_gauge(kpis['completion_percentage']),
            use_container_width=True
        )
    
    with col2:
        district_completion = pm.get_district_completion()
        if not district_completion.empty:
            st.plotly_chart(
                create_district_completion_bar(district_completion),
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Installation Trend
    st.markdown("### Installation Trend Over Time")
    trend_data = pm.get_installation_trend()
    if not trend_data.empty:
        st.plotly_chart(
            create_installation_trend(trend_data),
            use_container_width=True
        )
    else:
        st.info("No installation data available yet.")
    
    st.markdown("---")
    
    # Completion Estimation
    st.markdown("### 🎯 Projected Completion Estimate")
    estimation = estimate_completion_date(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if estimation['estimated_date']:
            st.metric("Estimated Completion", 
                     estimation['estimated_date'].strftime('%Y-%m-%d'))
        else:
            st.info(estimation['message'])
    
    with col2:
        st.metric("Days Remaining", estimation.get('days_remaining', 'N/A'))
    
    with col3:
        st.metric("Current Rate", f"{estimation.get('sites_per_week', 0):.2f} sites/week")
    
    with col4:
        st.metric("Sites Remaining", kpis['pending_sites'])
    
    st.markdown("---")
    
    # Top Delayed Sites
    st.markdown("### ⚠️ Top 10 Delayed Sites")
    top_delayed = pm.get_top_delayed_sites(10)
    
    if not top_delayed.empty:
        # Format dates for display
        display_df = top_delayed.copy()
        if 'delivery_date' in display_df.columns:
            display_df['delivery_date'] = pd.to_datetime(display_df['delivery_date']).dt.strftime('%Y-%m-%d')
        if 'installation_date' in display_df.columns:
            display_df['installation_date'] = pd.to_datetime(display_df['installation_date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No delayed sites found!")


def show_material_consumption_dashboard(df):
    """Display Material Consumption Dashboard"""
    st.markdown('<div class="section-header">📦 Material Consumption Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Initialize metrics
    mm = MaterialMetrics(df)
    material_summary = mm.get_material_summary()
    
    # Material Summary KPIs
    st.markdown("### Material Summary")
    cols = st.columns(5)
    
    metrics_data = [
        ("Total LAN Nodes", material_summary.get('total_lan_nodes', 0)),
        ("Total Cable", f"{material_summary.get('total_cable_meters', 0):,.0f} m"),
        ("Avg Cable/Node", f"{material_summary.get('avg_cable_per_node', 0):.2f} m"),
        ("Total Switches", material_summary.get('total_switches', 0)),
        ("Total Racks", material_summary.get('total_racks', 0))
    ]
    
    for col, (label, value) in zip(cols, metrics_data):
        with col:
            st.metric(label, value)
    
    st.markdown("---")
    
    # Material Consumption Bars
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_material_consumption_bars(material_summary),
            use_container_width=True
        )
    
    with col2:
        # Additional metrics
        st.markdown("#### Material Ratios")
        st.metric("Switch per Node Ratio", 
                 f"{material_summary.get('switch_per_node_ratio', 0):.3f}")
        st.metric("Rack per Site Ratio", 
                 f"{material_summary.get('rack_per_site_ratio', 0):.2f}")
    
    st.markdown("---")
    
    # Cable per Node Analysis
    st.markdown("### Cable Consumption Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(
            create_cable_per_node_scatter(df),
            use_container_width=True
        )
    
    with col2:
        st.markdown("#### Outlier Detection")
        threshold = st.slider(
            "Z-score Threshold",
            min_value=1.5,
            max_value=3.0,
            value=2.0,
            step=0.1
        )
        
        outliers = mm.detect_cable_outliers(threshold=threshold)
        
        st.metric("Outlier Sites", len(outliers))
        
        if not outliers.empty:
            st.warning(f"⚠️ {len(outliers)} sites flagged as outliers")
    
    # Outlier Table
    if not outliers.empty:
        st.markdown("### 🚨 Flagged Outlier Sites")
        st.dataframe(
            outliers,
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # District-wise Material Summary
    st.markdown("### District-wise Material Summary")
    district_material = mm.get_district_material_summary()
    
    if not district_material.empty:
        st.dataframe(
            district_material.style.format({
                'lan_nodes': '{:.0f}',
                'cable_meters': '{:,.0f}',
                'cable_per_node': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    # Filters
    st.sidebar.markdown("### Material Filters")
    
    if 'district' in df.columns:
        selected_districts = st.sidebar.multiselect(
            "Filter by District",
            options=df['district'].unique(),
            default=None
        )
        
        if selected_districts:
            filtered_df = df[df['district'].isin(selected_districts)]
            st.info(f"Showing data for {len(selected_districts)} district(s)")
            
            # Recalculate metrics for filtered data
            filtered_mm = MaterialMetrics(filtered_df)
            filtered_summary = filtered_mm.get_material_summary()
            
            st.markdown("#### Filtered Material Summary")
            st.json(filtered_summary)


def show_delay_risk_dashboard(df):
    """Display Delay Risk Dashboard"""
    st.markdown('<div class="section-header">⚠️ Delay Risk Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Initialize analyzer
    dra = DelayRiskAnalyzer(df)
    
    # Risk Distribution
    st.markdown("### Risk Category Distribution")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        risk_dist = dra.get_risk_distribution()
        st.plotly_chart(
            create_risk_category_pie(risk_dist),
            use_container_width=True
        )
    
    with col2:
        st.markdown("#### Risk Breakdown")
        st.dataframe(
            risk_dist.style.format({'percentage': '{:.2f}%'}),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # Delay Distribution Histogram
    st.markdown("### Delay Distribution")
    st.plotly_chart(
        create_delay_distribution(df),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # District Delay Heatmap
    st.markdown("### District-wise Delay Analysis")
    district_delay = dra.get_district_delay_heatmap_data()
    
    if not district_delay.empty:
        st.plotly_chart(
            create_district_heatmap(district_delay),
            use_container_width=True
        )
        
        # Show table
        st.dataframe(
            district_delay.style.format({
                'avg_delay': '{:.2f}',
                'median_delay': '{:.2f}',
                'max_delay': '{:.2f}'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # Sites at Risk
    st.markdown("### 🚨 Sites at Risk")
    
    # Delay threshold filter
    delay_threshold = st.slider(
        "Delay Threshold (days)",
        min_value=0,
        max_value=30,
        value=7,
        step=1
    )
    
    at_risk_sites = dra.get_sites_by_delay_threshold(delay_threshold)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.metric(f"Sites Delayed > {delay_threshold} days", len(at_risk_sites))
    
    with col2:
        if not at_risk_sites.empty:
            st.error(f"⚠️ {len(at_risk_sites)} sites require immediate attention!")
    
    if not at_risk_sites.empty:
        # Format dates
        display_df = at_risk_sites.copy()
        if 'delivery_date' in display_df.columns:
            display_df['delivery_date'] = pd.to_datetime(display_df['delivery_date']).dt.strftime('%Y-%m-%d')
        if 'installation_date' in display_df.columns:
            display_df['installation_date'] = pd.to_datetime(display_df['installation_date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success(f"✅ No sites delayed more than {delay_threshold} days!")
    
    st.markdown("---")
    
    # Not Yet Installed
    st.markdown("### 📋 Delivered but Not Yet Installed")
    
    not_installed = df[
        (df['delivery_date'].notna()) & 
        (df['installation_date'].isna())
    ].copy()
    
    st.metric("Pending Installation", len(not_installed))
    
    if not not_installed.empty:
        display_cols = ['district', 'site_name', 'delivery_date', 'lan_nodes']
        available_cols = [c for c in display_cols if c in not_installed.columns]
        
        display_df = not_installed[available_cols].copy()
        if 'delivery_date' in display_df.columns:
            display_df['delivery_date'] = pd.to_datetime(display_df['delivery_date']).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


def show_overview_dashboard(df):
    """Display Executive Overview Dashboard"""
    st.markdown('<div class="section-header">🎯 Executive Overview</div>', 
                unsafe_allow_html=True)
    
    # Initialize all metrics
    pm = ProjectMetrics(df)
    mm = MaterialMetrics(df)
    dra = DelayRiskAnalyzer(df)
    
    kpis = pm.get_kpis()
    material_summary = mm.get_material_summary()
    risk_dist = dra.get_risk_distribution()
    
    # Executive Summary
    st.markdown("### Project Status Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Project Progress")
        st.metric("Completion", f"{kpis['completion_percentage']:.1f}%")
        st.metric("Completed Sites", f"{kpis['completed_sites']}/{kpis['total_sites']}")
        st.metric("Avg Delay", f"{kpis['avg_installation_delay']:.1f} days")
    
    with col2:
        st.markdown("#### Material Status")
        st.metric("Total LAN Nodes", format_number(material_summary.get('total_lan_nodes', 0)))
        st.metric("Total Cable", f"{format_number(material_summary.get('total_cable_meters', 0))} m")
        st.metric("Avg Cable/Node", f"{material_summary.get('avg_cable_per_node', 0):.2f} m")
    
    with col3:
        st.markdown("#### Risk Status")
        high_risk = risk_dist[risk_dist['risk_category'] == 'High']['count'].sum() if 'High' in risk_dist['risk_category'].values else 0
        st.metric("High Risk Sites", high_risk)
        st.metric("Delayed Sites", kpis['delayed_sites'])
        st.metric("Pending Sites", kpis['pending_sites'])
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_completion_gauge(kpis['completion_percentage']),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_risk_category_pie(risk_dist),
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Timeline
    st.markdown("### Installation Timeline")
    st.plotly_chart(
        create_timeline_gantt(df, max_sites=15),
        use_container_width=True
    )


def main():
    """Main application"""
    
    # Header
    st.markdown(
        '<div class="main-header">🏗️ LAN Infrastructure Project Control Dashboard</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=Project+Dashboard", 
                     use_container_width=True)
    st.sidebar.title("Navigation")
    
    # Load data
    try:
        data_file = get_sample_data_path()
        
        # File uploader for custom data
        uploaded_file = st.sidebar.file_uploader(
            "Upload Custom Excel File",
            type=['xlsx', 'xls'],
            help="Upload your own project data"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = "/tmp/uploaded_data.xlsx"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            data_file = temp_path
        
        df = load_data(data_file)
        
        # Show data info
        with st.sidebar.expander("📊 Data Information"):
            st.write(f"**Total Records:** {len(df)}")
            st.write(f"**Districts:** {df['district'].nunique() if 'district' in df.columns else 'N/A'}")
            st.write(f"**Date Range:** {df['delivery_date'].min().strftime('%Y-%m-%d') if 'delivery_date' in df.columns and df['delivery_date'].notna().any() else 'N/A'} to {df['installation_date'].max().strftime('%Y-%m-%d') if 'installation_date' in df.columns and df['installation_date'].notna().any() else 'N/A'}")
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()
    
    # Dashboard selection
    dashboard = st.sidebar.radio(
        "Select Dashboard",
        ["Executive Overview", "Project Management", "Material Consumption", "Delay Risk Analysis"],
        index=0
    )
    
    st.sidebar.markdown("---")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Display selected dashboard
    if dashboard == "Executive Overview":
        show_overview_dashboard(df)
    elif dashboard == "Project Management":
        show_project_management_dashboard(df)
    elif dashboard == "Material Consumption":
        show_material_consumption_dashboard(df)
    elif dashboard == "Delay Risk Analysis":
        show_delay_risk_dashboard(df)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p><b>LAN Project Dashboard v1.0</b></p>
        <p>Built with Streamlit & Plotly</p>
        <p>© 2024 Project Control System</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
