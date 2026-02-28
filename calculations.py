"""
Calculations module for LAN Project Dashboard
Contains all metric calculation and analysis functions
"""

import pandas as pd
import numpy as np
from scipy import stats
from utils import calculate_delay_days, categorize_delay_risk, detect_outliers_zscore


class ProjectMetrics:
    """
    Class for calculating project management metrics
    """
    
    def __init__(self, df):
        """
        Initialize with project dataframe
        
        Args:
            df (pd.DataFrame): Project data
        """
        self.df = df.copy()
        self._calculate_derived_fields()
    
    def _calculate_derived_fields(self):
        """Calculate derived fields like delay, cable per node, etc."""
        # Calculate delay
        self.df['delay_days'] = calculate_delay_days(self.df)
        
        # Calculate cable per node
        if 'cable_meters' in self.df.columns and 'lan_nodes' in self.df.columns:
            self.df['cable_per_node'] = self.df['cable_meters'] / self.df['lan_nodes']
            self.df['cable_per_node'] = self.df['cable_per_node'].replace([np.inf, -np.inf], np.nan)
        
        # Calculate switch per node ratio
        if 'switch_8port' in self.df.columns and 'switch_24port' in self.df.columns and 'lan_nodes' in self.df.columns:
            total_switches = self.df['switch_8port'].fillna(0) + self.df['switch_24port'].fillna(0)
            self.df['switch_per_node'] = total_switches / self.df['lan_nodes']
            self.df['switch_per_node'] = self.df['switch_per_node'].replace([np.inf, -np.inf], np.nan)
        
        # Calculate rack per site
        if 'rack_6u' in self.df.columns:
            self.df['rack_per_site'] = self.df['rack_6u']
        
        # Delay risk category
        self.df['delay_risk'] = self.df['delay_days'].apply(categorize_delay_risk)
    
    def get_kpis(self):
        """
        Calculate key performance indicators
        
        Returns:
            dict: Dictionary of KPIs
        """
        total_sites = len(self.df)
        completed_sites = self.df['installation_date'].notna().sum()
        pending_sites = total_sites - completed_sites
        
        # Calculate delayed sites (positive delay only)
        delayed_sites = ((self.df['delay_days'] > 0) & (self.df['delay_days'].notna())).sum()
        
        # Average delay (only for installed sites)
        installed_df = self.df[self.df['installation_date'].notna()]
        avg_delay = installed_df['delay_days'].mean() if len(installed_df) > 0 else 0
        
        # Completion percentage
        completion_pct = (completed_sites / total_sites * 100) if total_sites > 0 else 0
        
        return {
            'total_sites': total_sites,
            'completed_sites': completed_sites,
            'pending_sites': pending_sites,
            'delayed_sites': delayed_sites,
            'avg_installation_delay': round(avg_delay, 2),
            'completion_percentage': round(completion_pct, 2)
        }
    
    def get_district_completion(self):
        """
        Calculate completion percentage by district
        
        Returns:
            pd.DataFrame: District-wise completion statistics
        """
        if 'district' not in self.df.columns:
            return pd.DataFrame()
        
        district_stats = self.df.groupby('district').agg({
            'site_id': 'count',
            'installation_date': lambda x: x.notna().sum()
        }).rename(columns={
            'site_id': 'total_sites',
            'installation_date': 'completed_sites'
        })
        
        district_stats['pending_sites'] = district_stats['total_sites'] - district_stats['completed_sites']
        district_stats['completion_pct'] = (
            district_stats['completed_sites'] / district_stats['total_sites'] * 100
        ).round(2)
        
        return district_stats.reset_index().sort_values('completion_pct', ascending=False)
    
    def get_installation_trend(self):
        """
        Get installation trend over time
        
        Returns:
            pd.DataFrame: Daily installation counts
        """
        if 'installation_date' not in self.df.columns:
            return pd.DataFrame()
        
        installed = self.df[self.df['installation_date'].notna()].copy()
        
        if len(installed) == 0:
            return pd.DataFrame()
        
        # Group by date
        trend = installed.groupby(installed['installation_date'].dt.date).size().reset_index()
        trend.columns = ['date', 'installations']
        
        # Add cumulative
        trend['cumulative_installations'] = trend['installations'].cumsum()
        
        return trend
    
    def get_top_delayed_sites(self, n=10):
        """
        Get top N delayed sites
        
        Args:
            n (int): Number of sites to return
            
        Returns:
            pd.DataFrame: Top delayed sites
        """
        delayed = self.df[self.df['delay_days'] > 0].copy()
        
        if len(delayed) == 0:
            return pd.DataFrame()
        
        cols = ['district', 'site_name', 'delivery_date', 'installation_date', 'delay_days', 'delay_risk']
        available_cols = [c for c in cols if c in delayed.columns]
        
        top_delayed = delayed.nlargest(n, 'delay_days')[available_cols]
        
        return top_delayed.reset_index(drop=True)
    
    def get_at_risk_sites(self, delay_threshold=0):
        """
        Get sites at risk (delivered but not installed, or delayed beyond threshold)
        
        Args:
            delay_threshold (int): Delay threshold in days
            
        Returns:
            pd.DataFrame: At-risk sites
        """
        # Sites delivered but not installed
        not_installed = self.df[
            (self.df['delivery_date'].notna()) & 
            (self.df['installation_date'].isna())
        ].copy()
        
        # Sites delayed beyond threshold
        delayed_beyond = self.df[
            (self.df['delay_days'] > delay_threshold) & 
            (self.df['delay_days'].notna())
        ].copy()
        
        # Combine and remove duplicates
        at_risk = pd.concat([not_installed, delayed_beyond]).drop_duplicates()
        
        cols = ['district', 'site_name', 'delivery_date', 'installation_date', 'delay_days', 'delay_risk']
        available_cols = [c for c in cols if c in at_risk.columns]
        
        return at_risk[available_cols].reset_index(drop=True)


class MaterialMetrics:
    """
    Class for calculating material consumption metrics
    """
    
    def __init__(self, df):
        """
        Initialize with project dataframe
        
        Args:
            df (pd.DataFrame): Project data
        """
        self.df = df.copy()
        self._calculate_material_metrics()
    
    def _calculate_material_metrics(self):
        """Calculate material-related metrics"""
        # Cable per node
        if 'cable_meters' in self.df.columns and 'lan_nodes' in self.df.columns:
            self.df['cable_per_node'] = self.df['cable_meters'] / self.df['lan_nodes']
            self.df['cable_per_node'] = self.df['cable_per_node'].replace([np.inf, -np.inf], np.nan)
        
        # Total switches
        if 'switch_8port' in self.df.columns and 'switch_24port' in self.df.columns:
            self.df['total_switches'] = self.df['switch_8port'].fillna(0) + self.df['switch_24port'].fillna(0)
    
    def get_material_summary(self):
        """
        Get overall material consumption summary
        
        Returns:
            dict: Material summary statistics
        """
        summary = {}
        
        if 'lan_nodes' in self.df.columns:
            summary['total_lan_nodes'] = int(self.df['lan_nodes'].sum())
        
        if 'cable_meters' in self.df.columns:
            summary['total_cable_meters'] = int(self.df['cable_meters'].sum())
        
        if 'cable_per_node' in self.df.columns:
            summary['avg_cable_per_node'] = round(self.df['cable_per_node'].mean(), 2)
        
        if 'switch_8port' in self.df.columns and 'switch_24port' in self.df.columns:
            total_switches = self.df['switch_8port'].sum() + self.df['switch_24port'].sum()
            summary['total_switches'] = int(total_switches)
            
            if 'lan_nodes' in self.df.columns:
                total_nodes = self.df['lan_nodes'].sum()
                summary['switch_per_node_ratio'] = round(total_switches / total_nodes, 3) if total_nodes > 0 else 0
        
        if 'rack_6u' in self.df.columns:
            summary['total_racks'] = int(self.df['rack_6u'].sum())
            summary['rack_per_site_ratio'] = round(self.df['rack_6u'].mean(), 2)
        
        return summary
    
    def detect_cable_outliers(self, threshold=2):
        """
        Detect sites with unusual cable consumption
        
        Args:
            threshold (float): Z-score threshold
            
        Returns:
            pd.DataFrame: Sites with outlier cable consumption
        """
        if 'cable_per_node' not in self.df.columns:
            return pd.DataFrame()
        
        # Detect outliers
        outliers = detect_outliers_zscore(self.df['cable_per_node'], threshold)
        
        outlier_sites = self.df[outliers].copy()
        
        if len(outlier_sites) == 0:
            return pd.DataFrame()
        
        # Calculate Z-scores for display
        mean_val = self.df['cable_per_node'].mean()
        std_val = self.df['cable_per_node'].std()
        outlier_sites['z_score'] = ((outlier_sites['cable_per_node'] - mean_val) / std_val).round(2)
        
        cols = ['district', 'site_name', 'lan_nodes', 'cable_meters', 'cable_per_node', 'z_score']
        available_cols = [c for c in cols if c in outlier_sites.columns]
        
        return outlier_sites[available_cols].sort_values('z_score', ascending=False).reset_index(drop=True)
    
    def get_district_material_summary(self):
        """
        Get material summary by district
        
        Returns:
            pd.DataFrame: District-wise material statistics
        """
        if 'district' not in self.df.columns:
            return pd.DataFrame()
        
        agg_dict = {}
        
        if 'lan_nodes' in self.df.columns:
            agg_dict['lan_nodes'] = 'sum'
        if 'cable_meters' in self.df.columns:
            agg_dict['cable_meters'] = 'sum'
        if 'cable_per_node' in self.df.columns:
            agg_dict['cable_per_node'] = 'mean'
        
        if not agg_dict:
            return pd.DataFrame()
        
        district_summary = self.df.groupby('district').agg(agg_dict).round(2)
        
        return district_summary.reset_index()


class DelayRiskAnalyzer:
    """
    Class for analyzing delay risks
    """
    
    def __init__(self, df):
        """
        Initialize with project dataframe
        
        Args:
            df (pd.DataFrame): Project data with delay information
        """
        self.df = df.copy()
        if 'delay_days' not in self.df.columns:
            self.df['delay_days'] = calculate_delay_days(self.df)
        if 'delay_risk' not in self.df.columns:
            self.df['delay_risk'] = self.df['delay_days'].apply(categorize_delay_risk)
    
    def get_risk_distribution(self):
        """
        Get distribution of sites by risk category
        
        Returns:
            pd.DataFrame: Risk category distribution
        """
        risk_dist = self.df['delay_risk'].value_counts().reset_index()
        risk_dist.columns = ['risk_category', 'count']
        
        # Calculate percentage
        risk_dist['percentage'] = (risk_dist['count'] / len(self.df) * 100).round(2)
        
        return risk_dist
    
    def get_district_delay_heatmap_data(self):
        """
        Get average delay by district for heatmap
        
        Returns:
            pd.DataFrame: District-wise average delay
        """
        if 'district' not in self.df.columns:
            return pd.DataFrame()
        
        # Filter only sites with delay data
        with_delay = self.df[self.df['delay_days'].notna()].copy()
        
        if len(with_delay) == 0:
            return pd.DataFrame()
        
        district_delay = with_delay.groupby('district').agg({
            'delay_days': ['mean', 'median', 'max', 'count']
        }).round(2)
        
        district_delay.columns = ['avg_delay', 'median_delay', 'max_delay', 'site_count']
        
        return district_delay.reset_index()
    
    def get_sites_by_delay_threshold(self, min_delay):
        """
        Get sites delayed more than specified days
        
        Args:
            min_delay (int): Minimum delay threshold
            
        Returns:
            pd.DataFrame: Sites exceeding delay threshold
        """
        filtered = self.df[
            (self.df['delay_days'] > min_delay) & 
            (self.df['delay_days'].notna())
        ].copy()
        
        cols = ['district', 'site_name', 'delivery_date', 'installation_date', 'delay_days', 'delay_risk']
        available_cols = [c for c in cols if c in filtered.columns]
        
        return filtered[available_cols].sort_values('delay_days', ascending=False).reset_index(drop=True)
