"""
Site Material Tracking Module
Handles site-wise material arrival tracking, status updates, and variance analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json


class SiteMaterialTracker:
    """
    Tracks material status for each site
    - Planned vs Arrived quantities
    - Pending materials
    - Excess/Shortage analysis
    """
    
    def __init__(self, df):
        """
        Initialize with project dataframe
        
        Args:
            df (pd.DataFrame): Project data with material specifications
        """
        self.df = df.copy()
        self._initialize_tracking_columns()
    
    def _initialize_tracking_columns(self):
        """Initialize columns for tracking material arrival"""
        
        # Material arrival tracking columns (initialize with 0 if not present)
        tracking_cols = {
            'lan_nodes_arrived': 0,
            'switch_8port_arrived': 0,
            'switch_24port_arrived': 0,
            'cable_meters_arrived': 0,
            'patch_panel_arrived': 0,
            'io_boxes_arrived': 0,
            'patch_cord_1m_arrived': 0,
            'patch_cord_3m_arrived': 0,
            'rack_6u_arrived': 0,
            'last_material_update': None,
            'material_status_notes': ''
        }
        
        for col, default_val in tracking_cols.items():
            if col not in self.df.columns:
                self.df[col] = default_val
    
    def get_site_material_status(self, site_id=None):
        """
        Get comprehensive material status for site(s)
        
        Args:
            site_id (int, optional): Specific site ID, or None for all sites
            
        Returns:
            pd.DataFrame: Material status with planned, arrived, and pending quantities
        """
        
        if site_id is not None:
            df_filtered = self.df[self.df['site_id'] == site_id].copy()
        else:
            df_filtered = self.df.copy()
        
        # Material columns mapping
        materials = {
            'LAN Nodes': ('lan_nodes', 'lan_nodes_arrived'),
            '8-Port Switch': ('switch_8port', 'switch_8port_arrived'),
            '24-Port Switch': ('switch_24port', 'switch_24port_arrived'),
            'Cable (m)': ('cable_meters', 'cable_meters_arrived'),
            'Patch Panel': ('patch_panel', 'patch_panel_arrived'),
            'I/O Boxes': ('io_boxes', 'io_boxes_arrived'),
            'Patch Cord 1m': ('patch_cord_1m', 'patch_cord_1m_arrived'),
            'Patch Cord 3m': ('patch_cord_3m', 'patch_cord_3m_arrived'),
            '6U Rack': ('rack_6u', 'rack_6u_arrived')
        }
        
        status_records = []
        
        for _, row in df_filtered.iterrows():
            for material_name, (planned_col, arrived_col) in materials.items():
                if planned_col in self.df.columns and arrived_col in self.df.columns:
                    planned = row.get(planned_col, 0) or 0
                    arrived = row.get(arrived_col, 0) or 0
                    
                    if planned > 0:  # Only include materials that are planned
                        pending = planned - arrived
                        variance_pct = ((arrived - planned) / planned * 100) if planned > 0 else 0
                        
                        # Determine status
                        if arrived == 0:
                            status = 'Not Started'
                            status_icon = '⚪'
                        elif arrived < planned:
                            status = 'Partial'
                            status_icon = '🟡'
                        elif arrived == planned:
                            status = 'Complete'
                            status_icon = '🟢'
                        else:
                            status = 'Excess'
                            status_icon = '🔴'
                        
                        status_records.append({
                            'site_id': row.get('site_id'),
                            'district': row.get('district', 'N/A'),
                            'site_name': row.get('site_name', 'N/A'),
                            'material': material_name,
                            'planned': planned,
                            'arrived': arrived,
                            'pending': pending,
                            'variance': arrived - planned,
                            'variance_pct': round(variance_pct, 2),
                            'status': status,
                            'status_icon': status_icon,
                            'last_update': row.get('last_material_update', 'Never')
                        })
        
        return pd.DataFrame(status_records)
    
    def get_site_summary(self, site_id):
        """
        Get summary for a specific site
        
        Args:
            site_id (int): Site ID
            
        Returns:
            dict: Site summary with overall completion
        """
        site_data = self.df[self.df['site_id'] == site_id]
        
        if len(site_data) == 0:
            return None
        
        site_row = site_data.iloc[0]
        material_status = self.get_site_material_status(site_id)
        
        if len(material_status) == 0:
            total_completion = 0
        else:
            total_completion = (
                material_status['arrived'].sum() / 
                material_status['planned'].sum() * 100
            ) if material_status['planned'].sum() > 0 else 0
        
        # Count status categories
        status_counts = material_status['status'].value_counts().to_dict()
        
        return {
            'site_id': site_id,
            'district': site_row.get('district', 'N/A'),
            'site_name': site_row.get('site_name', 'N/A'),
            'overall_completion': round(total_completion, 2),
            'total_items': len(material_status),
            'complete_items': status_counts.get('Complete', 0),
            'partial_items': status_counts.get('Partial', 0),
            'not_started': status_counts.get('Not Started', 0),
            'excess_items': status_counts.get('Excess', 0),
            'last_update': site_row.get('last_material_update', 'Never'),
            'notes': site_row.get('material_status_notes', '')
        }
    
    def get_all_sites_summary(self):
        """
        Get summary for all sites
        
        Returns:
            pd.DataFrame: Summary of all sites
        """
        summaries = []
        
        for site_id in self.df['site_id'].unique():
            if pd.notna(site_id):
                summary = self.get_site_summary(site_id)
                if summary:
                    summaries.append(summary)
        
        return pd.DataFrame(summaries)
    
    def update_material_arrival(self, site_id, material_updates, notes=''):
        """
        Update material arrival for a site
        
        Args:
            site_id (int): Site ID
            material_updates (dict): Dictionary of {material_column: quantity}
            notes (str): Update notes
            
        Returns:
            bool: Success status
        """
        site_idx = self.df[self.df['site_id'] == site_id].index
        
        if len(site_idx) == 0:
            return False
        
        idx = site_idx[0]
        
        # Update material quantities
        for col, qty in material_updates.items():
            if col in self.df.columns:
                self.df.at[idx, col] = qty
        
        # Update timestamp and notes
        self.df.at[idx, 'last_material_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if notes:
            existing_notes = self.df.at[idx, 'material_status_notes']
            new_notes = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}: {notes}"
            if pd.notna(existing_notes) and existing_notes:
                self.df.at[idx, 'material_status_notes'] = f"{existing_notes}\n{new_notes}"
            else:
                self.df.at[idx, 'material_status_notes'] = new_notes
        
        return True
    
    def get_variance_analysis(self):
        """
        Analyze material variances across all sites
        
        Returns:
            dict: Variance analysis statistics
        """
        material_status = self.get_site_material_status()
        
        if len(material_status) == 0:
            return {}
        
        # Sites with issues
        excess_sites = material_status[material_status['status'] == 'Excess'].groupby('site_id').size()
        shortage_sites = material_status[material_status['pending'] > 0].groupby('site_id').size()
        
        # Material-wise variance
        material_variance = material_status.groupby('material').agg({
            'planned': 'sum',
            'arrived': 'sum',
            'pending': 'sum',
            'variance': 'sum'
        }).reset_index()
        
        material_variance['completion_pct'] = (
            material_variance['arrived'] / material_variance['planned'] * 100
        ).round(2)
        
        return {
            'total_sites': self.df['site_id'].nunique(),
            'sites_with_excess': len(excess_sites),
            'sites_with_shortage': len(shortage_sites),
            'overall_completion': round(
                material_status['arrived'].sum() / material_status['planned'].sum() * 100, 2
            ) if material_status['planned'].sum() > 0 else 0,
            'total_planned_items': int(material_status['planned'].sum()),
            'total_arrived_items': int(material_status['arrived'].sum()),
            'total_pending_items': int(material_status['pending'].sum()),
            'material_wise': material_variance
        }
    
    def get_critical_sites(self, shortage_threshold=0.3):
        """
        Get sites with critical material shortages
        
        Args:
            shortage_threshold (float): Threshold for critical shortage (0.3 = 30% or more pending)
            
        Returns:
            pd.DataFrame: Sites with critical shortages
        """
        all_summaries = self.get_all_sites_summary()
        
        if len(all_summaries) == 0:
            return pd.DataFrame()
        
        # Calculate shortage percentage
        all_summaries['shortage_pct'] = 100 - all_summaries['overall_completion']
        
        # Filter critical sites
        critical = all_summaries[
            all_summaries['shortage_pct'] >= (shortage_threshold * 100)
        ].copy()
        
        critical = critical.sort_values('shortage_pct', ascending=False)
        
        return critical[['site_id', 'district', 'site_name', 'overall_completion', 
                        'shortage_pct', 'not_started', 'partial_items', 'last_update']]
    
    def export_current_status(self):
        """
        Export current material status to DataFrame (for Excel export)
        
        Returns:
            pd.DataFrame: Complete current status
        """
        return self.df.copy()
    
    def generate_material_requisition(self, site_id):
        """
        Generate material requisition list for pending items
        
        Args:
            site_id (int): Site ID
            
        Returns:
            pd.DataFrame: Requisition list with pending quantities
        """
        material_status = self.get_site_material_status(site_id)
        
        # Filter only pending items
        pending = material_status[material_status['pending'] > 0].copy()
        
        if len(pending) == 0:
            return pd.DataFrame()
        
        # Format for requisition
        pending['requisition_qty'] = pending['pending']
        pending = pending[['material', 'planned', 'arrived', 'requisition_qty']]
        
        return pending
    
    def get_excess_materials(self):
        """
        Get all sites with excess materials
        
        Returns:
            pd.DataFrame: Sites and materials with excess quantities
        """
        material_status = self.get_site_material_status()
        
        excess = material_status[material_status['variance'] > 0].copy()
        
        if len(excess) == 0:
            return pd.DataFrame()
        
        excess = excess.sort_values('variance', ascending=False)
        
        return excess[['site_id', 'district', 'site_name', 'material', 
                      'planned', 'arrived', 'variance']]


def save_tracking_data(tracker, filepath):
    """
    Save updated tracking data to Excel
    
    Args:
        tracker (SiteMaterialTracker): Tracker instance
        filepath (str): Path to save Excel file
    """
    df = tracker.export_current_status()
    df.to_excel(filepath, index=False)


def load_tracking_data(filepath):
    """
    Load tracking data and create tracker
    
    Args:
        filepath (str): Path to Excel file
        
    Returns:
        SiteMaterialTracker: Tracker instance
    """
    from data_loader import DataLoader
    
    loader = DataLoader(filepath)
    df = loader.load_and_process()
    
    return SiteMaterialTracker(df)
