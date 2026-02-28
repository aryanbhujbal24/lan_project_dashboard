"""
Test script to verify the LAN Project Dashboard installation and setup
Run this script to check if all components are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    packages = {
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'numpy': 'NumPy',
        'plotly': 'Plotly',
        'scipy': 'SciPy',
        'openpyxl': 'OpenPyXL'
    }
    
    failed = []
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name} imported successfully")
        except ImportError as e:
            print(f"  ✗ {name} import failed: {e}")
            failed.append(name)
    
    return len(failed) == 0


def test_modules():
    """Test if all custom modules can be imported"""
    print("\nTesting custom modules...")
    
    modules = [
        'data_loader',
        'calculations',
        'visualizations',
        'utils'
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}.py imported successfully")
        except ImportError as e:
            print(f"  ✗ {module}.py import failed: {e}")
            failed.append(module)
    
    return len(failed) == 0


def test_data_file():
    """Test if the data file exists"""
    print("\nTesting data file...")
    
    data_path = '/mnt/project/Lan_Nodes_1424_Phase__2_3_1.xlsx'
    
    if os.path.exists(data_path):
        print(f"  ✓ Data file found at {data_path}")
        return True
    else:
        print(f"  ✗ Data file not found at {data_path}")
        print(f"    Please ensure the Excel file is in the correct location")
        return False


def test_data_loading():
    """Test if data can be loaded successfully"""
    print("\nTesting data loading...")
    
    try:
        from data_loader import DataLoader
        
        data_path = '/mnt/project/Lan_Nodes_1424_Phase__2_3_1.xlsx'
        
        if not os.path.exists(data_path):
            print(f"  ⚠ Skipping data loading test (file not found)")
            return True
        
        loader = DataLoader(data_path)
        df = loader.load_and_process()
        
        print(f"  ✓ Data loaded successfully")
        print(f"    - Shape: {df.shape}")
        print(f"    - Columns: {len(df.columns)}")
        print(f"    - Districts: {df['district'].nunique() if 'district' in df.columns else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Data loading failed: {e}")
        return False


def test_calculations():
    """Test if calculations work correctly"""
    print("\nTesting calculations...")
    
    try:
        from calculations import ProjectMetrics, MaterialMetrics, DelayRiskAnalyzer
        from data_loader import DataLoader
        import pandas as pd
        
        # Create sample data
        sample_data = pd.DataFrame({
            'site_id': [1, 2, 3],
            'district': ['District A', 'District B', 'District A'],
            'site_name': ['Site 1', 'Site 2', 'Site 3'],
            'lan_nodes': [10, 20, 15],
            'cable_meters': [150, 300, 225],
            'delivery_date': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
            'installation_date': pd.to_datetime(['2024-01-05', '2024-01-10', None])
        })
        
        pm = ProjectMetrics(sample_data)
        kpis = pm.get_kpis()
        
        print(f"  ✓ ProjectMetrics working")
        print(f"    - Total sites: {kpis['total_sites']}")
        print(f"    - Completed: {kpis['completed_sites']}")
        
        mm = MaterialMetrics(sample_data)
        material_summary = mm.get_material_summary()
        
        print(f"  ✓ MaterialMetrics working")
        print(f"    - Total nodes: {material_summary.get('total_lan_nodes', 0)}")
        
        dra = DelayRiskAnalyzer(sample_data)
        risk_dist = dra.get_risk_distribution()
        
        print(f"  ✓ DelayRiskAnalyzer working")
        print(f"    - Risk categories: {len(risk_dist)}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Calculations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualizations():
    """Test if visualizations can be created"""
    print("\nTesting visualizations...")
    
    try:
        from visualizations import (
            create_completion_gauge,
            create_district_completion_bar,
            create_risk_category_pie
        )
        import pandas as pd
        
        # Test gauge
        fig = create_completion_gauge(75.5)
        print(f"  ✓ Completion gauge created")
        
        # Test bar chart
        district_df = pd.DataFrame({
            'district': ['District A', 'District B'],
            'completion_pct': [80, 60],
            'total_sites': [10, 8],
            'completed_sites': [8, 5]
        })
        fig = create_district_completion_bar(district_df)
        print(f"  ✓ District completion bar created")
        
        # Test pie chart
        risk_df = pd.DataFrame({
            'risk_category': ['Low', 'Medium', 'High'],
            'count': [10, 5, 3],
            'percentage': [55.6, 27.8, 16.7]
        })
        fig = create_risk_category_pie(risk_df)
        print(f"  ✓ Risk category pie created")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and provide summary"""
    print("="*70)
    print("LAN PROJECT DASHBOARD - INSTALLATION TEST")
    print("="*70)
    
    results = {
        'Package Imports': test_imports(),
        'Custom Modules': test_modules(),
        'Data File': test_data_file(),
        'Data Loading': test_data_loading(),
        'Calculations': test_calculations(),
        'Visualizations': test_visualizations()
    }
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<50} {status}")
    
    print("="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! The dashboard is ready to run.")
        print("\nTo start the dashboard, run:")
        print("  streamlit run app.py")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Check file paths and permissions")
        print("  - Verify data file location")
    
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
