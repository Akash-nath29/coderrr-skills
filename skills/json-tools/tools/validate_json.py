#!/usr/bin/env python3
"""
Validate JSON syntax.

This tool checks if a JSON file has valid syntax and reports
specific error locations if invalid.

Usage:
    python validate_json.py --file data.json

Exit Codes:
    0 - Success (valid JSON)
    1 - Invalid file path
    2 - Invalid JSON (with error details)
"""

import argparse
import sys
import json
from pathlib import Path


def validate_json(file_path: str) -> dict:
    """
    Validate JSON file syntax.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary with validation result
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except IOError as e:
        raise IOError(f"Could not read file: {e}")
    
    try:
        json.loads(content)
        return {
            'valid': True,
            'file': str(path)
        }
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'file': str(path),
            'error': {
                'message': e.msg,
                'line': e.lineno,
                'column': e.colno
            }
        }


def main():
    parser = argparse.ArgumentParser(
        description='Validate JSON syntax',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python validate_json.py --file data.json
    python validate_json.py --file config.json
        '''
    )
    parser.add_argument(
        '--file',
        required=True,
        help='Path to JSON file to validate'
    )
    
    args = parser.parse_args()
    
    try:
        result = validate_json(args.file)
        
        output = {
            "status": "success",
            "data": result,
            "message": "JSON is valid" if result['valid'] else "JSON is invalid"
        }
        
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print(json.dumps(output, indent=2))
        
        # Exit with code 0 as the tool successfully ran (validity is in data)
            
    except Exception as e:
        print_json_error(str(e))

def print_json_error(message, exit_code=1):
    result = {
        "status": "error",
        "error": message,
        "message": message
    }
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
