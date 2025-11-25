"""
Command Line Interface for Database Integration module.
Imports labeled data from Excel files into the SQLite database.
"""
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

from excel_to_db import ExcelToDBConverter
from core.config import RESOURCES_DIR

def check_required_files():
    """Check if all required Excel files exist."""
    required_files = [
        'taxonomy.xlsx',
        'adoption_commits_filtered.xlsx',
        'migration_commits_filtered.xlsx',
        'adoption_issues_filtered.xlsx',
        'migration_issues_filtered.xlsx',
        'issues_missed_in_filter.xlsx',
        'transitions.xlsx'
    ]
    
    missing_files = []
    for file_name in required_files:
        file_path = RESOURCES_DIR / file_name
        if not file_path.exists():
            missing_files.append(file_name)
    
    return missing_files

def main():
    """Import data from Excel files to database."""
    print("Starting Database Integration...")
    print("Checking for required files...\n")
    
    missing_files = check_required_files()
    if missing_files:
        print("Error: The following required files are missing in resources directory:")
        for file_name in missing_files:
            print(f"  - {file_name}")
        print(f"\nPlease ensure all files exist in: {RESOURCES_DIR}")
        sys.exit(1)
    
    print("✓ All required files found.")
    print("This will import data from Excel files into the database.\n")
    
    converter = ExcelToDBConverter()

    print("\n[1/4] Inserting taxonomy data...")
    converter.insert_taxonomy_data()
    print("✓ Taxonomy data inserted successfully.")
    
    print("\n[2/4] Inserting commits...")
    converter.insert_commits("adoption_commits_filtered.xlsx")
    converter.insert_commits("migration_commits_filtered.xlsx")
    print("✓ Commits inserted successfully.")

    print("\n[3/4] Inserting issues...")
    converter.insert_issues("adoption_issues_filtered.xlsx")
    converter.insert_issues("migration_issues_filtered.xlsx")
    converter.insert_issues("issues_missed_in_filter.xlsx")
    print("✓ Issues inserted successfully.")

    print("\n[4/4] Inserting transitions...")
    converter.insert_transitions("adoption")
    converter.insert_transitions("migration")
    print("✓ Transitions inserted successfully.")
    
    print("\n✓ Database integration completed successfully!")

if __name__ == '__main__':
    main()
