#!/usr/bin/env python3
"""
Merge multiple PDF files into one.

Usage:
    python merge_pdf.py --files doc1.pdf doc2.pdf --output merged.pdf
"""

import argparse
import sys
import json
from pathlib import Path

try:
    from PyPDF2 import PdfMerger
except ImportError:
    print(json.dumps({
        "status": "error",
        "error": "'PyPDF2' package is required. Install with: pip install PyPDF2",
        "message": "Missing dependency"
    }))
    sys.exit(1)


def merge_pdfs(file_paths: list, output_path: str):
    """Merge multiple PDF files."""
    merger = PdfMerger()
    
    for file_path in file_paths:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        merger.append(file_path)
    
    merger.write(output_path)
    merger.close()
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Merge PDF files')
    parser.add_argument('--files', nargs='+', required=True, help='PDF files to merge')
    parser.add_argument('--output', required=True, help='Output merged PDF path')
    
    args = parser.parse_args()
    
    try:
        result = merge_pdfs(args.files, args.output)
        
        output = {
            "status": "success",
            "data": {
                "file": result,
                "merged_count": len(args.files)
            },
            "message": f"Successfully merged {len(args.files)} files"
        }
        
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print(json.dumps(output, indent=2))
        
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
