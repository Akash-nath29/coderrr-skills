#!/usr/bin/env python3
"""
Analyze Word document structure and metadata.

Usage:
    python analyze_docx.py --file document.docx
"""

import argparse
import sys
import json
from pathlib import Path
from collections import Counter

try:
    from docx import Document
except ImportError:
    print(json.dumps({
        "status": "error",
        "error": "'python-docx' package is required. Install with: pip install python-docx",
        "message": "Missing dependency"
    }))
    sys.exit(1)


def analyze_docx(file_path: str) -> dict:
    """Analyze document structure and provide metadata."""
    doc = Document(file_path)
    
    # Count words and paragraphs
    word_count = 0
    paragraph_count = 0
    heading_count = 0
    styles_used = Counter()
    headings = []
    
    for para in doc.paragraphs:
        if para.text.strip():
            paragraph_count += 1
            word_count += len(para.text.split())
            
            style_name = para.style.name if para.style else "Normal"
            styles_used[style_name] += 1
            
            if 'Heading' in style_name:
                heading_count += 1
                headings.append({
                    "text": para.text[:100],  # Truncate long headings
                    "style": style_name
                })
    
    # Count tables
    table_count = len(doc.tables)
    
    # Get document properties
    core_props = doc.core_properties
    
    return {
        "file": str(file_path),
        "statistics": {
            "word_count": word_count,
            "paragraph_count": paragraph_count,
            "heading_count": heading_count,
            "table_count": table_count,
            "section_count": len(doc.sections)
        },
        "structure": {
            "headings": headings[:20],  # Limit to first 20
            "styles_used": dict(styles_used.most_common(10))
        },
        "properties": {
            "title": core_props.title or "",
            "author": core_props.author or "",
            "created": str(core_props.created) if core_props.created else "",
            "modified": str(core_props.modified) if core_props.modified else ""
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Analyze Word documents')
    parser.add_argument('--file', required=True, help='Path to Word document')
    
    args = parser.parse_args()
    
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = analyze_docx(args.file)
        
        output = {
            "status": "success",
            "data": result,
            "message": "Successfully analyzed document"
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
