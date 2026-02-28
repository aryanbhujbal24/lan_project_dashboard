"""
Visualizations module for LAN Project Dashboard
Contains all Plotly chart generation functions
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np


def create_completion_gauge(completion_pct):
    """
    Create a gauge chart for completion percentage
    
    Args:
        completion_pct (float): Completion percentage
        
    Returns:
        plotly.graph_objects.Figure: Gauge chart
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=completion_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Project Completion %", 'font': {'size': 24}},
        delta={'reference': 100, 'increasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#ffcccc'},
                {'range': [50, 80], 'color': '#ffffcc'},
                {'range': [80, 100], 'color': '#ccffcc'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig


def create_district_completion_bar(district_df):
    """
    Create horizontal bar chart for district-wise completion
    
    Args:
        district_df (pd.DataFrame): District completion data
        
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    fig = go.Figure()
    
    # Sort by completion percentage
    district_df = district_df.sort_values('completion_pct', ascending=True)
    
    fig.add_trace(go.Bar(
        y=district_df['district'],
        x=district_df['completion_pct'],
        orientation='h',
        text=district_df['completion_pct'].round(1).astype(str) + '%',
        textposition='outside',
        marker=dict(
            color=district_df['completion_pct'],
            colorscale='RdYlGn',
            showscale=True,
            colorbar=dict(title="Completion %")
        ),
        hovertemplate='<b>%{y}</b><br>' +
                      'Completion: %{x:.1f}%<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title='District-wise Completion Percentage',
        xaxis_title='Completion %',
        yaxis_title='District',
        height=max(400, len(district_df) * 25),
        margin=dict(l=150, r=50, t=50, b=50),
        showlegend=False
    )
    
    return fig


def create_installation_trend(trend_df):
    """
    Create line chart for installation trend over time
    
    Args:
        trend_df (pd.DataFrame): Installation trend data
        
    Returns:
        plotly.graph_objects.Figure: Line chart
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Daily installations
    fig.add_trace(
        go.Bar(
            x=trend_df['date'],
            y=trend_df['installations'],
            name='Daily Installations',
            marker_color='lightblue',
            hovertemplate='Date: %{x}<br>Installations: %{y}<extra></extra>'
        ),
        secondary_y=False
    )
    
    # Cumulative installations
    fig.add_trace(
        go.Scatter(
            x=trend_df['date'],
            y=trend_df['cumulative_installations'],
            name='Cumulative',
            mode='lines+markers',
            line=dict(color='darkblue', width=3),
            marker=dict(size=8),
            hovertemplate='Date: %{x}<br>Total: %{y}<extra></extra>'
        ),
        secondary_y=True
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Daily Installations", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative Installations", secondary_y=True)
    
    fig.update_layout(
        title='Installation Trend Over Time',
        hovermode='x unified',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_delay_distribution(df):
    """
    Create histogram of delay distribution
    
    Args:
        df (pd.DataFrame): Data with delay_days column
        
    Returns:
        plotly.graph_objects.Figure: Histogram
    """
    # Filter out NaN values and create bins
    delay_data = df[df['delay_days'].notna()]['delay_days']
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=delay_data,
        nbinsx=20,
        marker=dict(
            color='rgba(100, 149, 237, 0.7)',
            line=dict(color='darkblue', width=1)
        ),
        hovertemplate='Delay Range: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Distribution of Installation Delays',
        xaxis_title='Delay (days)',
        yaxis_title='Number of Sites',
        height=400,
        showlegend=False
    )
    
    # Add vertical line at 0
    fig.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="On Time")
    
    return fig


def create_risk_category_pie(risk_dist_df):
    """
    Create pie chart for risk category distribution
    
    Args:
        risk_dist_df (pd.DataFrame): Risk distribution data
        
    Returns:
        plotly.graph_objects.Figure: Pie chart
    """
    colors = {
        'Low': '#90EE90',
        'Medium': '#FFD700',
        'High': '#FF6347',
        'Unknown': '#D3D3D3',
        'Early': '#87CEEB'
    }
    
    color_map = [colors.get(cat, '#CCCCCC') for cat in risk_dist_df['risk_category']]
    
    fig = go.Figure(data=[go.Pie(
        labels=risk_dist_df['risk_category'],
        values=risk_dist_df['count'],
        hole=0.4,
        marker=dict(colors=color_map),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Delay Risk Distribution',
        height=400,
        showlegend=True
    )
    
    return fig


def create_material_consumption_bars(material_summary):
    """
    Create bar charts for material consumption
    
    Args:
        material_summary (dict): Material summary statistics
        
    Returns:
        plotly.graph_objects.Figure: Bar chart
    """
    metrics = []
    values = []
    
    if 'total_lan_nodes' in material_summary:
        metrics.append('LAN Nodes')
        values.append(material_summary['total_lan_nodes'])
    
    if 'total_cable_meters' in material_summary:
        metrics.append('Cable (m)')
        values.append(material_summary['total_cable_meters'])
    
    if 'total_switches' in material_summary:
        metrics.append('Switches')
        values.append(material_summary['total_switches'])
    
    if 'total_racks' in material_summary:
        metrics.append('Racks')
        values.append(material_summary['total_racks'])
    
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            text=values,
            textposition='outside',
            marker=dict(
                color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'][:len(metrics)],
                line=dict(color='black', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Total: %{y:,.0f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='Total Material Consumption',
        xaxis_title='Material Type',
        yaxis_title='Quantity',
        height=400,
        showlegend=False
    )
    
    return fig


def create_district_heatmap(district_delay_df):
    """
    Create heatmap for district-wise delay analysis
    
    Args:
        district_delay_df (pd.DataFrame): District delay data
        
    Returns:
        plotly.graph_objects.Figure: Heatmap
    """
    if len(district_delay_df) == 0:
        return go.Figure()
    
    # Prepare data for heatmap
    districts = district_delay_df['district'].tolist()
    metrics = ['Avg Delay', 'Median Delay', 'Max Delay']
    
    z_data = [
        district_delay_df['avg_delay'].tolist(),
        district_delay_df['median_delay'].tolist(),
        district_delay_df['max_delay'].tolist()
    ]
    
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=districts,
        y=metrics,
        colorscale='RdYlGn_r',
        text=z_data,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        hovertemplate='District: %{x}<br>Metric: %{y}<br>Days: %{z:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='District-wise Delay Analysis (Days)',
        xaxis_title='District',
        yaxis_title='Delay Metric',
        height=300,
        margin=dict(l=100, r=50, t=50, b=100)
    )
    
    fig.update_xaxes(tickangle=-45)
    
    return fig


def create_cable_per_node_scatter(df):
    """
    Create scatter plot for cable per node analysis
    
    Args:
        df (pd.DataFrame): Data with cable_per_node
        
    Returns:
        plotly.graph_objects.Figure: Scatter plot
    """
    if 'cable_per_node' not in df.columns or 'lan_nodes' not in df.columns:
        return go.Figure()
    
    # Remove NaN values
    plot_df = df[df['cable_per_node'].notna()].copy()
    
    # Calculate mean and std for reference lines
    mean_val = plot_df['cable_per_node'].mean()
    std_val = plot_df['cable_per_node'].std()
    
    fig = go.Figure()
    
    # Add scatter points
    fig.add_trace(go.Scatter(
        x=plot_df['lan_nodes'],
        y=plot_df['cable_per_node'],
        mode='markers',
        marker=dict(
            size=8,
            color=plot_df['cable_per_node'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Cable/Node")
        ),
        text=plot_df['district'] if 'district' in plot_df.columns else None,
        hovertemplate='LAN Nodes: %{x}<br>Cable/Node: %{y:.2f}m<br>%{text}<extra></extra>'
    ))
    
    # Add mean line
    fig.add_hline(
        y=mean_val, 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Mean: {mean_val:.2f}m"
    )
    
    # Add +/- 2 std lines
    fig.add_hline(
        y=mean_val + 2*std_val,
        line_dash="dot",
        line_color="orange",
        annotation_text="+2σ"
    )
    
    fig.add_hline(
        y=mean_val - 2*std_val,
        line_dash="dot",
        line_color="orange",
        annotation_text="-2σ"
    )
    
    fig.update_layout(
        title='Cable Consumption per Node Analysis',
        xaxis_title='Number of LAN Nodes',
        yaxis_title='Cable per Node (meters)',
        height=450,
        hovermode='closest'
    )
    
    return fig


def create_kpi_cards_figure(kpis):
    """
    Create a figure with KPI cards (for display in subplot)
    
    Args:
        kpis (dict): Dictionary of KPI values
        
    Returns:
        plotly.graph_objects.Figure: KPI cards
    """
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=('Total Sites', 'Completed', 'Pending', 
                       'Delayed', 'Avg Delay (days)', 'Completion %'),
        specs=[[{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
               [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]]
    )
    
    # Total Sites
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('total_sites', 0),
        title={'text': "Total Sites"},
        number={'font': {'size': 40}}
    ), row=1, col=1)
    
    # Completed Sites
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('completed_sites', 0),
        title={'text': "Completed"},
        number={'font': {'size': 40, 'color': 'green'}}
    ), row=1, col=2)
    
    # Pending Sites
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('pending_sites', 0),
        title={'text': "Pending"},
        number={'font': {'size': 40, 'color': 'orange'}}
    ), row=1, col=3)
    
    # Delayed Sites
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('delayed_sites', 0),
        title={'text': "Delayed"},
        number={'font': {'size': 40, 'color': 'red'}}
    ), row=2, col=1)
    
    # Average Delay
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('avg_installation_delay', 0),
        title={'text': "Avg Delay (days)"},
        number={'font': {'size': 40}}
    ), row=2, col=2)
    
    # Completion %
    fig.add_trace(go.Indicator(
        mode="number",
        value=kpis.get('completion_percentage', 0),
        title={'text': "Completion %"},
        number={'font': {'size': 40, 'color': 'blue'}, 'suffix': '%'}
    ), row=2, col=3)
    
    fig.update_layout(height=400, margin=dict(t=50, b=0))
    
    return fig


def create_timeline_gantt(df, max_sites=20):
    """
    Create Gantt chart for site installation timeline
    
    Args:
        df (pd.DataFrame): Data with delivery and installation dates
        max_sites (int): Maximum number of sites to show
        
    Returns:
        plotly.graph_objects.Figure: Gantt chart
    """
    if 'delivery_date' not in df.columns or 'installation_date' not in df.columns:
        return go.Figure()
    
    # Filter sites with both dates
    gantt_df = df[
        df['delivery_date'].notna() & 
        df['installation_date'].notna()
    ].copy()
    
    if len(gantt_df) == 0:
        return go.Figure()
    
    # Limit to max_sites
    gantt_df = gantt_df.head(max_sites)
    
    # Create task names
    gantt_df['task'] = gantt_df['district'] + ' - ' + gantt_df['site_name'].str[:30]
    
    fig = go.Figure()
    
    for idx, row in gantt_df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row['delivery_date'], row['installation_date']],
            y=[row['task'], row['task']],
            mode='lines+markers',
            line=dict(width=10),
            marker=dict(size=10),
            name=row['task'],
            showlegend=False,
            hovertemplate='<b>%{y}</b><br>Period: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f'Installation Timeline (Top {len(gantt_df)} Sites)',
        xaxis_title='Date',
        yaxis_title='Site',
        height=max(400, len(gantt_df) * 25),
        margin=dict(l=250)
    )
    
    return fig
