"""
Command Line Interface for Manual Labeling module.
Starts the Flask web server for manual data labeling or converts JSON to Excel.
"""
import argparse
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent))

from server import app, set_excel_file
from converter import Converter
from core.config import RESOURCES_DIR

def get_file_name(target, type_filter):
    """Get the Excel file name based on target and type."""
    return f"{type_filter}_{target}_filtered.xlsx"

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Manual Labeling CLI for E2E Testing Framework Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start labeling server for adoption commits
  python -m 02_manual_labeling.cli --task server --target commits --type adoption

  # Start labeling server for migration commits
  python -m 02_manual_labeling.cli --task server --target commits --type migration

  # Start labeling server for adoption issues
  python -m 02_manual_labeling.cli --task server --target issues --type adoption

  # Start labeling server for migration issues
  python -m 02_manual_labeling.cli --task server --target issues --type migration
  
  # Convert adoption commits JSON to Excel
  python -m 02_manual_labeling.cli --task convert --target commits --type adoption

  # Convert migration commits JSON to Excel
  python -m 02_manual_labeling.cli --task convert --target commits --type migration

  # Convert adoption issues JSON to Excel
  python -m 02_manual_labeling.cli --task convert --target issues --type adoption

  # Convert migration issues JSON to Excel
  python -m 02_manual_labeling.cli --task convert --target issues --type migration
        """
    )
    
    parser.add_argument(
        '--task',
        choices=['server', 'convert'],
        required=True,
        help='Task to perform: start labeling server or convert JSON to Excel'
    )
    
    parser.add_argument(
        '--target',
        choices=['commits', 'issues'],
        help='Choose to label/convert commits or issues (required for both tasks)'
    )
    
    parser.add_argument(
        '--type',
        choices=['adoption', 'migration'],
        help='Choose adoption or migration data (required for both tasks)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to run the server on (default: 5000, only for server task)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments based on task
    if args.task == 'server':
        if not args.target:
            parser.error("--target is required for server task")
        if not args.type:
            parser.error("--type is required for server task")
        
        # Get the Excel file path
        file_name = get_file_name(args.target, args.type)
        file_path = RESOURCES_DIR / file_name
        
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            print(f"Please ensure the file exists in the resources directory.")
            sys.exit(1)
        
        set_excel_file(file_path, args.target)
        
        print(f"Starting Manual Labeling Web Interface...")
        print(f"Target: {args.target}")
        print(f"Type: {args.type}")
        print(f"File: {file_name}")
        print(f"Access the interface at: http://127.0.0.1:{args.port}")
        print(f"Press Ctrl+C to stop the server\n")
        
        app.run(debug=True, port=args.port)
    
    elif args.task == 'convert':
        if not args.target:
            parser.error("--target is required for convert task")
        if not args.type:
            parser.error("--type is required for convert task")
        
        print(f"Converting {args.type} {args.target} JSON to Excel...")
        
        method_name = f"{args.target}_{args.type}"
        converter_method = getattr(Converter, method_name, None)
        
        if converter_method:
            converter_method()
            print(f"✓ {args.type.capitalize()} {args.target} converted successfully to {args.type}_{args.target}_filtered.xlsx")
        else:
            print(f"✗ Error: Converter method '{method_name}' not found")
            sys.exit(1)

if __name__ == '__main__':
    main()
