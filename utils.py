"""
Utility functions for the LAN Project Dashboard
Handles data cleaning, validation, and helper functions
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re


def clean_column_names(df):
    """
    Clean and standardize column names
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        pd.DataFrame: Dataframe with cleaned column names
    """
    # Create a mapping for known columns
    column_mapping = {
        'Sr. No.': 'site_id',
        ' Name of the Judicia1\nDistrict': 'district',
        'Name of Court Complex': 'site_name',
        'ICT\xa0Newlv\nSetup\xa0Courts\nafter Dec  2019': 'ict_courts',
        'Lan Nodes to be provided': 'lan_nodes',
        '8 Port Switch': 'switch_8port',
        '24 Port Switch': 'switch_24port',
        'Cat-6 Cable (mtr)': 'cable_meters',
        'Patch Panel (24 Port)': 'patch_panel',
        'I/O             (Box,Face plate)': 'io_boxes',
        '1 mtr Patch Cord': 'patch_cord_1m',
        '3 mtr Patch Cord': 'patch_cord_3m',
        '6U Rack': 'rack_6u',
        'Date of Delivery': 'delivery_date',
        'Date of Installation': 'installation_date',
        'Survey Cable Qty': 'survey_cable_qty',
        'On site use cable ': 'onsite_cable_qty',
        'Cabling rate for labour': 'cabling_rate'
    }
    
    # Rename columns
    df = df.rename(columns=column_mapping)
    
    # Clean any remaining column names (generic approach)
    df.columns = [col.strip().lower().replace(' ', '_').replace('\n', '_') 
                  if col not in column_mapping.values() else col 
                  for col in df.columns]
    
    return df


def validate_and_clean_data(df):
    """
    Validate and clean the dataset
    
    Args:
        df (pd.DataFrame): Raw dataframe
        
    Returns:
        pd.DataFrame: Cleaned and validated dataframe
    """
    # Remove completely empty rows
    df = df.dropna(how='all')
    
    # Remove rows where site_id is NaN (invalid data rows)
    df = df[df['site_id'].notna()]
    
    # Convert numeric columns
    numeric_cols = ['site_id', 'ict_courts', 'lan_nodes', 'switch_8port', 
                    'switch_24port', 'cable_meters', 'patch_panel', 'io_boxes',
                    'patch_cord_1m', 'patch_cord_3m', 'rack_6u']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Convert date columns
    date_cols = ['delivery_date', 'installation_date']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Clean text columns
    text_cols = ['district', 'site_name']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df


def calculate_delay_days(df):
    """
    Calculate delay in days between delivery and installation
    
    Args:
        df (pd.DataFrame): Dataframe with delivery_date and installation_date
        
    Returns:
        pd.Series: Delay in days
    """
    if 'delivery_date' in df.columns and 'installation_date' in df.columns:
        delay = (df['installation_date'] - df['delivery_date']).dt.days
        return delay
    return pd.Series([np.nan] * len(df))


def categorize_delay_risk(delay_days):
    """
    Categorize delay risk based on number of days
    
    Args:
        delay_days (float): Number of days delayed
        
    Returns:
        str: Risk category (Low, Medium, High)
    """
    if pd.isna(delay_days):
        return 'Unknown'
    elif delay_days < 0:
        return 'Early'
    elif delay_days <= 3:
        return 'Low'
    elif delay_days <= 7:
        return 'Medium'
    else:
        return 'High'


def detect_outliers_zscore(series, threshold=2):
    """
    Detect outliers using Z-score method
    
    Args:
        series (pd.Series): Data series
        threshold (float): Z-score threshold (default: 2)
        
    Returns:
        pd.Series: Boolean series indicating outliers
    """
    # Remove NaN values for calculation
    clean_series = series.dropna()
    
    if len(clean_series) == 0:
        return pd.Series([False] * len(series), index=series.index)
    
    # Calculate Z-scores
    mean = clean_series.mean()
    std = clean_series.std()
    
    if std == 0:
        return pd.Series([False] * len(series), index=series.index)
    
    z_scores = np.abs((series - mean) / std)
    return z_scores > threshold


def format_number(num):
    """
    Format numbers with proper separators
    
    Args:
        num: Number to format
        
    Returns:
        str: Formatted number string
    """
    if pd.isna(num):
        return "N/A"
    
    if isinstance(num, (int, float)):
        if num >= 1000000:
            return f"{num/1000000:.2f}M"
        elif num >= 1000:
            return f"{num/1000:.2f}K"
        else:
            return f"{num:,.2f}"
    
    return str(num)


def calculate_completion_percentage(total, completed):
    """
    Calculate completion percentage
    
    Args:
        total (int): Total count
        completed (int): Completed count
        
    Returns:
        float: Completion percentage
    """
    if total == 0:
        return 0.0
    return (completed / total) * 100


def get_status_color(value, thresholds):
    """
    Get color based on value and thresholds
    
    Args:
        value (float): Value to check
        thresholds (dict): Dictionary with 'good' and 'warning' thresholds
        
    Returns:
        str: Color string for status
    """
    if value >= thresholds.get('good', 80):
        return 'green'
    elif value >= thresholds.get('warning', 50):
        return 'orange'
    else:
        return 'red'


def estimate_completion_date(df, current_date=None):
    """
    Estimate project completion date based on current installation rate
    
    Args:
        df (pd.DataFrame): Project dataframe
        current_date (datetime): Current date (default: today)
        
    Returns:
        dict: Dictionary with estimation details
    """
    if current_date is None:
        current_date = pd.Timestamp.now()
    
    # Get completed and pending sites
    completed = df['installation_date'].notna().sum()
    total = len(df)
    pending = total - completed
    
    if pending == 0:
        return {
            'estimated_date': None,
            'days_remaining': 0,
            'sites_per_week': 0,
            'message': 'Project completed!'
        }
    
    # Calculate installation rate (sites per week)
    installed_sites = df[df['installation_date'].notna()].copy()
    
    if len(installed_sites) < 2:
        return {
            'estimated_date': None,
            'days_remaining': None,
            'sites_per_week': 0,
            'message': 'Insufficient data for estimation'
        }
    
    # Get date range of installations
    min_date = installed_sites['installation_date'].min()
    max_date = installed_sites['installation_date'].max()
    days_elapsed = (max_date - min_date).days
    
    if days_elapsed == 0:
        return {
            'estimated_date': None,
            'days_remaining': None,
            'sites_per_week': 0,
            'message': 'All installations on same day'
        }
    
    # Calculate rate
    sites_per_day = len(installed_sites) / days_elapsed
    sites_per_week = sites_per_day * 7
    
    # Estimate completion
    days_to_complete = pending / sites_per_day if sites_per_day > 0 else 0
    estimated_completion = current_date + pd.Timedelta(days=days_to_complete)
    
    return {
        'estimated_date': estimated_completion,
        'days_remaining': int(days_to_complete),
        'sites_per_week': round(sites_per_week, 2),
        'message': f'Estimated completion in {int(days_to_complete)} days'
    }


def export_to_excel(dataframes_dict, filename):
    """
    Export multiple dataframes to Excel with different sheets
    
    Args:
        dataframes_dict (dict): Dictionary of {sheet_name: dataframe}
        filename (str): Output filename
    """
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
