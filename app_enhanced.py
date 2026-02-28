"""
Enhanced LAN Project Control Dashboard with Site Material Tracking
Main Streamlit Application with Material Management Interface
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
from site_material_tracking import SiteMaterialTracker, save_tracking_data
from visualizations import (
    create_completion_gauge, create_district_completion_bar,
    create_installation_trend, create_delay_distribution,
    create_risk_category_pie, create_material_consumption_bars,
    create_district_heatmap, create_cable_per_node_scatter,
    create_kpi_cards_figure, create_timeline_gantt
)
from utils import estimate_completion_date, format_number
import plotly.graph_objects as go
import plotly.express as px

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
    .status-complete { color: #28a745; font-weight: bold; }
    .status-partial { color: #ffc107; font-weight: bold; }
    .status-not-started { color: #6c757d; font-weight: bold; }
    .status-excess { color: #dc3545; font-weight: bold; }
    .stMetric {
        background-color: black;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
""", unsafe_allow_html=True)


# Session state for data persistence
if 'tracker' not in st.session_state:
    st.session_state.tracker = None
if 'df' not in st.session_state:
    st.session_state.df = None


@st.cache_data
def load_data(file_path):
    """Load and cache data"""
    loader = DataLoader(file_path)
    df = loader.load_and_process()
    return df


def initialize_tracker(df):
    """Initialize or get tracker from session state"""
    if st.session_state.tracker is None:
        st.session_state.tracker = SiteMaterialTracker(df)
    return st.session_state.tracker


def show_site_material_management(df):
    """Display Site Material Management Dashboard - NEW FEATURE"""
    st.markdown('<div class="section-header">📦 Site Material Management</div>', 
                unsafe_allow_html=True)
    
    # Initialize tracker
    tracker = initialize_tracker(df)
    
    # Top-level metrics
    variance_analysis = tracker.get_variance_analysis()
    
    st.markdown("### 📊 Overall Material Status")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Sites", variance_analysis.get('total_sites', 0))
    with col2:
        st.metric("Overall Completion", 
                 f"{variance_analysis.get('overall_completion', 0):.1f}%")
    with col3:
        st.metric("Sites with Shortage", 
                 variance_analysis.get('sites_with_shortage', 0),
                 delta=f"-{variance_analysis.get('sites_with_shortage', 0)}" if variance_analysis.get('sites_with_shortage', 0) > 0 else None,
                 delta_color="inverse")
    with col4:
        st.metric("Sites with Excess", 
                 variance_analysis.get('sites_with_excess', 0),
                 delta=f"+{variance_analysis.get('sites_with_excess', 0)}" if variance_analysis.get('sites_with_excess', 0) > 0 else None,
                 delta_color="inverse")
    with col5:
        st.metric("Pending Items", 
                 format_number(variance_analysis.get('total_pending_items', 0)))
    
    st.markdown("---")
    
    # Material-wise completion
    st.markdown("### 📋 Material-wise Status")
    
    if 'material_wise' in variance_analysis and not variance_analysis['material_wise'].empty:
        material_df = variance_analysis['material_wise']
        
        # Create bar chart for material completion
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Arrived',
            x=material_df['material'],
            y=material_df['arrived'],
            marker_color='lightgreen'
        ))
        
        fig.add_trace(go.Bar(
            name='Pending',
            x=material_df['material'],
            y=material_df['pending'],
            marker_color='lightcoral'
        ))
        
        fig.update_layout(
            title='Material Arrival Status',
            barmode='stack',
            xaxis_title='Material Type',
            yaxis_title='Quantity',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Material completion table
        st.dataframe(
            material_df.style.format({
                'planned': '{:,.0f}',
                'arrived': '{:,.0f}',
                'pending': '{:,.0f}',
                'variance': '{:,.0f}',
                'completion_pct': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # Site-wise tracking interface
    st.markdown("### 🏗️ Site-wise Material Tracking")
    
    # Two modes: View All Sites or Manage Single Site
    mode = st.radio(
        "Select Mode",
        ["📊 View All Sites", "✏️ Update Site Material"],
        horizontal=True
    )
    
    if mode == "📊 View All Sites":
        show_all_sites_view(tracker, df)
    else:
        show_site_update_interface(tracker, df)


def show_all_sites_view(tracker, df):
    """Show all sites material status"""
    
    # Get all sites summary
    all_sites = tracker.get_all_sites_summary()
    
    if all_sites.empty:
        st.info("No site data available")
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'district' in all_sites.columns:
            districts = ['All'] + list(all_sites['district'].unique())
            selected_district = st.selectbox("Filter by District", districts)
        else:
            selected_district = 'All'
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            ['All', 'Complete (100%)', 'In Progress (1-99%)', 'Not Started (0%)']
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ['Site ID', 'Completion %', 'Pending Items']
        )
    
    # Apply filters
    filtered_sites = all_sites.copy()
    
    if selected_district != 'All':
        filtered_sites = filtered_sites[filtered_sites['district'] == selected_district]
    
    if status_filter == 'Complete (100%)':
        filtered_sites = filtered_sites[filtered_sites['overall_completion'] == 100]
    elif status_filter == 'In Progress (1-99%)':
        filtered_sites = filtered_sites[
            (filtered_sites['overall_completion'] > 0) & 
            (filtered_sites['overall_completion'] < 100)
        ]
    elif status_filter == 'Not Started (0%)':
        filtered_sites = filtered_sites[filtered_sites['overall_completion'] == 0]
    
    # Sort
    if sort_by == 'Completion %':
        filtered_sites = filtered_sites.sort_values('overall_completion', ascending=False)
    elif sort_by == 'Pending Items':
        filtered_sites = filtered_sites.sort_values('not_started', ascending=False)
    else:
        filtered_sites = filtered_sites.sort_values('site_id')
    
    # Display sites
    st.markdown(f"#### Showing {len(filtered_sites)} site(s)")
    
    # Create visual cards for each site
    for idx, site in filtered_sites.iterrows():
        with st.expander(
            f"🏗️ Site {int(site['site_id'])} - {site['site_name'][:50]} | "
            f"Completion: {site['overall_completion']:.1f}%"
        ):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Overall Completion", f"{site['overall_completion']:.1f}%")
            with col2:
                st.metric("✅ Complete", site['complete_items'])
            with col3:
                st.metric("🟡 Partial", site['partial_items'])
            with col4:
                st.metric("⚪ Not Started", site['not_started'])
            
            if site['excess_items'] > 0:
                st.warning(f"⚠️ {site['excess_items']} item(s) have excess material")
            
            # Show detailed material status
            site_details = tracker.get_site_material_status(int(site['site_id']))
            
            if not site_details.empty:
                st.dataframe(
                    site_details[['material', 'planned', 'arrived', 'pending', 'status_icon', 'status']],
                    use_container_width=True,
                    hide_index=True
                )
            
            # Notes
            if site['notes']:
                st.markdown("**📝 Notes:**")
                st.text_area("", site['notes'], height=100, disabled=True, key=f"notes_{idx}")
            
            st.markdown(f"*Last Update: {site['last_update']}*")
    
    st.markdown("---")
    
    # Critical sites alert
    st.markdown("### 🚨 Critical Sites (Material Shortage)")
    critical_sites = tracker.get_critical_sites(shortage_threshold=0.3)
    
    if not critical_sites.empty:
        st.error(f"⚠️ {len(critical_sites)} site(s) have critical material shortages (≥30%)")
        st.dataframe(
            critical_sites.style.format({
                'overall_completion': '{:.1f}%',
                'shortage_pct': '{:.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No critical material shortages detected")


def show_site_update_interface(tracker, df):
    """Interface for updating site material status"""
    
    st.markdown("#### 🔄 Update Material Arrival Status")
    
    # Site selection
    site_ids = sorted([int(x) for x in df['site_id'].unique() if pd.notna(x)])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_site_id = st.selectbox(
            "Select Site",
            site_ids,
            format_func=lambda x: f"Site {x}"
        )
    
    with col2:
        # Show current site info
        site_info = df[df['site_id'] == selected_site_id].iloc[0]
        st.info(f"**District:** {site_info.get('district', 'N/A')}  \n**Site:** {site_info.get('site_name', 'N/A')}")
    
    # Get current status
    current_status = tracker.get_site_material_status(selected_site_id)
    
    if current_status.empty:
        st.warning("No material data available for this site")
        return
    
    # Display current status
    st.markdown("##### Current Material Status")
    st.dataframe(
        current_status[['material', 'planned', 'arrived', 'pending', 'status']],
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    
    # Update form
    st.markdown("##### ✏️ Update Arrived Quantities")
    
    st.info("💡 **Tip:** Site manager can call and provide current quantities. Update here and save.")
    
    # Create input fields for each material
    material_updates = {}
    
    # Group into columns for better layout
    num_cols = 3
    cols = st.columns(num_cols)
    
    for idx, row in current_status.iterrows():
        col_idx = idx % num_cols
        with cols[col_idx]:
            material_name = row['material']
            planned = row['planned']
            current_arrived = row['arrived']
            
            new_qty = st.number_input(
                f"{material_name} (Planned: {planned:.0f})",
                min_value=0.0,
                max_value=planned * 2,  # Allow up to 2x for excess
                value=float(current_arrived),
                step=1.0,
                key=f"update_{selected_site_id}_{material_name}"
            )
            
            # Map back to column name
            material_col_map = {
                'LAN Nodes': 'lan_nodes_arrived',
                '8-Port Switch': 'switch_8port_arrived',
                '24-Port Switch': 'switch_24port_arrived',
                'Cable (m)': 'cable_meters_arrived',
                'Patch Panel': 'patch_panel_arrived',
                'I/O Boxes': 'io_boxes_arrived',
                'Patch Cord 1m': 'patch_cord_1m_arrived',
                'Patch Cord 3m': 'patch_cord_3m_arrived',
                '6U Rack': 'rack_6u_arrived'
            }
            
            if material_name in material_col_map:
                material_updates[material_col_map[material_name]] = new_qty
    
    # Notes field
    st.markdown("##### 📝 Add Notes (Optional)")
    update_notes = st.text_area(
        "Notes about this update",
        placeholder="e.g., Site manager reported cable delivery completed, switches pending...",
        height=100
    )
    
    # Update button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Update", type="primary", use_container_width=True):
            success = tracker.update_material_arrival(
                selected_site_id,
                material_updates,
                update_notes
            )
            
            if success:
                # Update session state
                st.session_state.tracker = tracker
                st.success("✅ Material status updated successfully!")
                st.balloons()
                
                # Show what changed
                st.markdown("**Updated Quantities:**")
                for col, qty in material_updates.items():
                    st.write(f"- {col}: {qty:.0f}")
                
                # Offer to save to Excel
                st.info("💡 Click 'Export to Excel' below to save changes permanently")
            else:
                st.error("❌ Failed to update. Please check site ID.")
    
    with col2:
        if st.button("🔄 Reset Form", use_container_width=True):
            st.rerun()
    
    st.markdown("---")
    
    # Export functionality
    st.markdown("### 💾 Save Changes to Excel")
    st.warning("⚠️ Make sure to export after updates to save changes permanently")
    
    export_filename = st.text_input(
        "Export filename",
        value=f"site_material_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )
    
    if st.button("📥 Export to Excel", type="secondary"):
        try:
            output_path = f"/tmp/{export_filename}"
            save_tracking_data(tracker, output_path)
            
            # Read file for download
            with open(output_path, 'rb') as f:
                st.download_button(
                    label="⬇️ Download Updated File",
                    data=f,
                    file_name=export_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            st.success("✅ File ready for download!")
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")


# Include all other dashboard functions from original app.py
# (Copy show_project_management_dashboard, show_material_consumption_dashboard, etc.)

def show_project_management_dashboard(df):
    """Display Project Management Dashboard"""
    st.markdown('<div class="section-header">📊 Project Management Dashboard</div>', 
                unsafe_allow_html=True)
    
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
        st.metric("Completion", f"{kpis['completion_percentage']:.1f}%")
    
    st.markdown("---")
    
    # Charts
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


def main():
    """Main application"""
    
    # Header
    st.markdown(
        '<div class="main-header">🏗️ LAN Infrastructure Project Control Dashboard</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar
    st.sidebar.title("Navigation")
    
    # Load data
    try:
        data_file = get_sample_data_path()
        
        uploaded_file = st.sidebar.file_uploader(
            "Upload Custom Excel File",
            type=['xlsx', 'xls'],
            help="Upload your project data"
        )
        
        if uploaded_file is not None:
            temp_path = "/tmp/uploaded_data.xlsx"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            data_file = temp_path
        
        df = load_data(data_file)
        st.session_state.df = df
        
        with st.sidebar.expander("📊 Data Information"):
            st.write(f"**Total Records:** {len(df)}")
            st.write(f"**Districts:** {df['district'].nunique() if 'district' in df.columns else 'N/A'}")
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()
    
    # Dashboard selection - ADDED NEW DASHBOARD
    dashboard = st.sidebar.radio(
        "Select Dashboard",
        [
            "🏗️ Site Material Management",  # NEW - Most important for client
            "📊 Executive Overview",
            "📈 Project Management", 
            "📦 Material Consumption",
            "⚠️ Delay Risk Analysis"
        ],
        index=0  # Default to Site Material Management
    )
    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.session_state.tracker = None
        st.rerun()
    
    # Display selected dashboard
    if dashboard == "🏗️ Site Material Management":
        show_site_material_management(df)
    elif dashboard == "📊 Executive Overview":
        show_overview_dashboard(df)
    elif dashboard == "📈 Project Management":
        show_project_management_dashboard(df)
    elif dashboard == "📦 Material Consumption":
        show_material_consumption_dashboard(df)
    elif dashboard == "⚠️ Delay Risk Analysis":
        show_delay_risk_dashboard(df)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <p><b>LAN Project Dashboard v2.0</b></p>
        <p>With Site Material Management</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_overview_dashboard(df):
    """Placeholder - copy from original app.py"""
    st.info("Use original dashboard functions here")


def show_material_consumption_dashboard(df):
    """Placeholder - copy from original app.py"""
    st.info("Use original dashboard functions here")


def show_delay_risk_dashboard(df):
    """Placeholder - copy from original app.py"""
    st.info("Use original dashboard functions here")


if __name__ == "__main__":
    main()
