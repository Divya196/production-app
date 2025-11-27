"""
Facilities Asset Data Export Script
Purpose: Export SQLite database to CSV files for Power BI Dashboard
Author: Technical Lead
Version: 1.0
Date: 2024-11-27
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

# Configuration
DB_PATH = 'facilities_asset_data.db'
EXPORT_DIR = 'powerbi_exports'
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')

def create_export_directory():
    """Create export directory if it doesn't exist"""
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        print(f"✓ Created export directory: {EXPORT_DIR}")
    return EXPORT_DIR

def export_submissions(conn):
    """Export main submissions data"""
    query = """
    SELECT 
        id as submission_id,
        employee_id,
        employee_name,
        reporting_manager,
        business_unit,
        project_name,
        project_code,
        office_store_gh_together,
        office_store_together,
        office_gh_together,
        num_guesthouses,
        submission_datetime,
        is_complete,
        CASE 
            WHEN is_complete = 1 THEN 'Completed'
            ELSE 'In Progress'
        END as status
    FROM submissions
    ORDER BY submission_datetime DESC
    """
    
    df = pd.read_sql_query(query, conn)
    filename = f'{EXPORT_DIR}/submissions_{TIMESTAMP}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ Exported {len(df)} submissions to: {filename}")
    return df

def export_guesthouses(conn):
    """Export guesthouse data"""
    query = """
    SELECT 
        g.id as guesthouse_id,
        g.submission_id,
        s.employee_id,
        s.employee_name,
        s.project_name,
        s.project_code,
        g.guesthouse_number,
        g.number_of_persons,
        g.gmap_link
    FROM guesthouses g
    LEFT JOIN submissions s ON g.submission_id = s.id
    WHERE s.is_complete = 1
    ORDER BY s.submission_datetime DESC, g.guesthouse_number
    """
    
    df = pd.read_sql_query(query, conn)
    filename = f'{EXPORT_DIR}/guesthouses_{TIMESTAMP}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ Exported {len(df)} guesthouse records to: {filename}")
    return df

def export_assets(conn):
    """Export assets data"""
    query = """
    SELECT 
        a.id as asset_id,
        a.submission_id,
        s.employee_id,
        s.employee_name,
        s.reporting_manager,
        s.business_unit,
        s.project_name,
        s.project_code,
        a.asset_location,
        a.asset_name,
        a.asset_count,
        a.asset_group,
        a.asset_category,
        a.asset_subcategory,
        a.guesthouse_id,
        CASE 
            WHEN a.guesthouse_id IS NOT NULL THEN g.guesthouse_number
            ELSE NULL
        END as guesthouse_number,
        s.submission_datetime
    FROM assets a
    LEFT JOIN submissions s ON a.submission_id = s.id
    LEFT JOIN guesthouses g ON a.guesthouse_id = g.id
    WHERE s.is_complete = 1
    ORDER BY s.submission_datetime DESC, a.asset_location, a.asset_name
    """
    
    df = pd.read_sql_query(query, conn)
    filename = f'{EXPORT_DIR}/assets_{TIMESTAMP}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ Exported {len(df)} asset records to: {filename}")
    return df

def export_asset_summary(conn):
    """Export asset summary by location"""
    query = """
    SELECT 
        s.business_unit,
        s.project_name,
        s.project_code,
        a.asset_location,
        a.asset_name,
        a.asset_group,
        a.asset_category,
        SUM(a.asset_count) as total_count,
        COUNT(DISTINCT a.submission_id) as num_projects
    FROM assets a
    LEFT JOIN submissions s ON a.submission_id = s.id
    WHERE s.is_complete = 1
    GROUP BY s.business_unit, s.project_name, s.project_code, 
             a.asset_location, a.asset_name, a.asset_group, a.asset_category
    ORDER BY s.business_unit, s.project_name, a.asset_location, total_count DESC
    """
    
    df = pd.read_sql_query(query, conn)
    filename = f'{EXPORT_DIR}/asset_summary_{TIMESTAMP}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ Exported {len(df)} summary records to: {filename}")
    return df

def export_business_unit_summary(conn):
    """Export summary by business unit"""
    query = """
    SELECT 
        s.business_unit,
        COUNT(DISTINCT s.id) as total_submissions,
        COUNT(DISTINCT s.project_code) as total_projects,
        SUM(s.num_guesthouses) as total_guesthouses,
        COUNT(DISTINCT a.id) as total_asset_entries,
        SUM(a.asset_count) as total_asset_count
    FROM submissions s
    LEFT JOIN assets a ON s.id = a.submission_id
    WHERE s.is_complete = 1
    GROUP BY s.business_unit
    ORDER BY s.business_unit
    """
    
    df = pd.read_sql_query(query, conn)
    filename = f'{EXPORT_DIR}/business_unit_summary_{TIMESTAMP}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ Exported business unit summary to: {filename}")
    return df

def export_asset_category_analysis(conn):
    """Export asset category analysis"""
    query = """
    SELECT 
        a.asset_group,
        a.asset_category,
        a.asset_location,
        COUNT(DISTINCT s.project_code) as num_projects,
        COUNT(DISTINCT a.asset_name) as num_asset_types,
        SUM(a.asset_count) as total_quantity
    FROM assets a
    LEFT JOIN submissions s ON a.submission_id = s.id
    WHERE s.is_complete = 1
    GROUP BY a.asset_group, a.asset_category, a.asset_location
    ORDER BY a.asset_group, a.asset_category, total_quantity DESC
    """
    
    df = pd.read_sql_query(query, conn)
    filename = f'{EXPORT_DIR}/asset_category_analysis_{TIMESTAMP}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ Exported category analysis to: {filename}")
    return df

def export_master_data(conn):
    """Export comprehensive master dataset for Power BI relationships"""
    query = """
    SELECT 
        s.id as submission_id,
        s.employee_id,
        s.employee_name,
        s.reporting_manager,
        s.business_unit,
        s.project_name,
        s.project_code,
        s.office_store_gh_together,
        s.office_store_together,
        s.office_gh_together,
        s.num_guesthouses,
        s.submission_datetime,
        s.is_complete,
        a.id as asset_id,
        a.asset_location,
        a.asset_name,
        a.asset_count,
        a.asset_group,
        a.asset_category,
        a.asset_subcategory,
        g.guesthouse_number,
        g.number_of_persons as gh_capacity,
        g.gmap_link
    FROM submissions s
    LEFT JOIN assets a ON s.id = a.submission_id
    LEFT JOIN guesthouses g ON a.guesthouse_id = g.id
    WHERE s.is_complete = 1
    ORDER BY s.submission_datetime DESC
    """
    
    df = pd.read_sql_query(query, conn)
    filename = f'{EXPORT_DIR}/master_data_{TIMESTAMP}.csv'
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✓ Exported {len(df)} master records to: {filename}")
    return df

def generate_export_manifest():
    """Generate a manifest file with export details"""
    manifest = {
        'export_timestamp': TIMESTAMP,
        'export_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'files_generated': [
            'submissions_{}.csv',
            'guesthouses_{}.csv',
            'assets_{}.csv',
            'asset_summary_{}.csv',
            'business_unit_summary_{}.csv',
            'asset_category_analysis_{}.csv',
            'master_data_{}.csv'
        ]
    }
    
    filename = f'{EXPORT_DIR}/export_manifest_{TIMESTAMP}.txt'
    with open(filename, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("FACILITIES ASSET DATA EXPORT MANIFEST\n")
        f.write("=" * 60 + "\n")
        f.write(f"Export Date: {manifest['export_datetime']}\n")
        f.write(f"Export Directory: {EXPORT_DIR}\n")
        f.write("\nFiles Generated:\n")
        for file in manifest['files_generated']:
            f.write(f"  - {file.format(TIMESTAMP)}\n")
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"✓ Generated export manifest: {filename}")

def main():
    """Main execution function"""
    print("\n" + "=" * 60)
    print("FACILITIES ASSET DATA EXPORT TO POWER BI")
    print("=" * 60 + "\n")
    
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Database file '{DB_PATH}' not found!")
        print("   Please ensure the database file is in the same directory.")
        return
    
    try:
        # Create export directory
        create_export_directory()
        
        # Connect to database
        print(f"Connecting to database: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        
        print("\nStarting export process...\n")
        
        # Execute all exports
        export_submissions(conn)
        export_guesthouses(conn)
        export_assets(conn)
        export_asset_summary(conn)
        export_business_unit_summary(conn)
        export_asset_category_analysis(conn)
        export_master_data(conn)
        
        # Generate manifest
        generate_export_manifest()
        
        # Close connection
        conn.close()
        
        print("\n" + "=" * 60)
        print("✓ EXPORT COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"\nAll files exported to: ./{EXPORT_DIR}/")
        print(f"Timestamp: {TIMESTAMP}")
        print("\nYou can now import these CSV files into Power BI.")
        print("\n" + "=" * 60 + "\n")
        
    except sqlite3.Error as e:
        print(f"\n❌ DATABASE ERROR: {str(e)}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
