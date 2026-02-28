"""
Data loading module for LAN Project Dashboard
Handles Excel file loading, sheet selection, and initial preprocessing
"""

import pandas as pd
import numpy as np
from utils import clean_column_names, validate_and_clean_data


class DataLoader:
    """
    Data loader class for handling Excel file operations
    """
    
    def __init__(self, file_path):
        """
        Initialize DataLoader with file path
        
        Args:
            file_path (str): Path to Excel file
        """
        self.file_path = file_path
        self.raw_data = None
        self.processed_data = None
        self.available_sheets = None
        
    def get_available_sheets(self):
        """
        Get list of available sheets in the Excel file
        
        Returns:
            list: List of sheet names
        """
        try:
            xls = pd.ExcelFile(self.file_path)
            self.available_sheets = xls.sheet_names
            return self.available_sheets
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def load_data(self, sheet_name='PHASE II Location List Working', skiprows=2):
        """
        Load data from specified sheet
        
        Args:
            sheet_name (str): Name of the sheet to load
            skiprows (int): Number of rows to skip
            
        Returns:
            pd.DataFrame: Loaded raw data
        """
        try:
            self.raw_data = pd.read_excel(
                self.file_path, 
                sheet_name=sheet_name, 
                skiprows=skiprows
            )
            return self.raw_data
        except Exception as e:
            raise Exception(f"Error loading sheet '{sheet_name}': {str(e)}")
    
    def preprocess_data(self):
        """
        Preprocess the loaded data
        
        Returns:
            pd.DataFrame: Cleaned and processed data
        """
        if self.raw_data is None:
            raise Exception("No data loaded. Call load_data() first.")
        
        # Clean column names
        df = clean_column_names(self.raw_data.copy())
        
        # Validate and clean data
        df = validate_and_clean_data(df)
        
        self.processed_data = df
        return self.processed_data
    
    def load_and_process(self, sheet_name='PHASE II Location List Working', skiprows=2):
        """
        Load and process data in one step
        
        Args:
            sheet_name (str): Name of the sheet to load
            skiprows (int): Number of rows to skip
            
        Returns:
            pd.DataFrame: Processed data
        """
        self.load_data(sheet_name=sheet_name, skiprows=skiprows)
        return self.preprocess_data()
    
    def get_data_summary(self):
        """
        Get summary statistics of the processed data
        
        Returns:
            dict: Summary statistics
        """
        if self.processed_data is None:
            raise Exception("No processed data available. Call preprocess_data() first.")
        
        df = self.processed_data
        
        summary = {
            'total_records': len(df),
            'total_sites': df['site_id'].nunique() if 'site_id' in df.columns else 0,
            'total_districts': df['district'].nunique() if 'district' in df.columns else 0,
            'date_range': {
                'earliest_delivery': df['delivery_date'].min() if 'delivery_date' in df.columns else None,
                'latest_delivery': df['delivery_date'].max() if 'delivery_date' in df.columns else None,
                'earliest_installation': df['installation_date'].min() if 'installation_date' in df.columns else None,
                'latest_installation': df['installation_date'].max() if 'installation_date' in df.columns else None,
            },
            'columns': df.columns.tolist(),
            'missing_values': df.isnull().sum().to_dict()
        }
        
        return summary
    
    def get_column_info(self):
        """
        Get information about columns and their data types
        
        Returns:
            pd.DataFrame: Column information
        """
        if self.processed_data is None:
            raise Exception("No processed data available.")
        
        df = self.processed_data
        
        info_df = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes,
            'Non-Null Count': df.count(),
            'Null Count': df.isnull().sum(),
            'Null %': (df.isnull().sum() / len(df) * 100).round(2)
        })
        
        return info_df


def load_project_data(file_path):
    """
    Convenience function to load project data
    
    Args:
        file_path (str): Path to Excel file
        
    Returns:
        tuple: (DataLoader instance, processed DataFrame)
    """
    loader = DataLoader(file_path)
    df = loader.load_and_process()
    return loader, df


def get_sample_data_path():
    """
    Get the expected data file path
    
    Returns:
        str: Expected file path
    """
    return '/mnt/project/Lan_Nodes_1424_Phase__2_3_1.xlsx'
