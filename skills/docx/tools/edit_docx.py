#!/usr/bin/env python3
"""
Edit existing Word documents.

Usage:
    python edit_docx.py --file input.docx --output output.docx --operations '[...]'
"""

import argparse
import sys
import json
from pathlib import Path

try:
    from docx import Document
except ImportError:
    print(json.dumps({
        "status": "error",
        "error": "'python-docx' package is required. Install with: pip install python-docx",
        "message": "Missing dependency"
    }))
    sys.exit(1)


def apply_operation(doc, operation):
    """Apply a single edit operation to the document."""
    action = operation.get('action')
    
    if action == 'append_paragraph':
        doc.add_paragraph(operation.get('text', ''))
    
    elif action == 'add_heading':
        level = operation.get('level', 1)
        doc.add_heading(operation.get('text', ''), level=level)
    
    elif action == 'replace_text':
        find_text = operation.get('find', '')
        replace_text = operation.get('replace', '')
        for para in doc.paragraphs:
            if find_text in para.text:
                for run in para.runs:
                    if find_text in run.text:
                        run.text = run.text.replace(find_text, replace_text)
    
    elif action == 'insert_table':
        headers = operation.get('headers', [])
        rows = operation.get('rows', [])
        
        if headers:
            table = doc.add_table(rows=1, cols=len(headers))
            table.style = 'Table Grid'
            
            header_cells = table.rows[0].cells
            for i, header in enumerate(headers):
                header_cells[i].text = str(header)
            
            for row_data in rows:
                row_cells = table.add_row().cells
                for i, cell_data in enumerate(row_data):
                    if i < len(row_cells):
                        row_cells[i].text = str(cell_data)
    
    elif action == 'add_page_break':
        doc.add_page_break()
    
    elif action == 'add_list':
        items = operation.get('items', [])
        ordered = operation.get('ordered', False)
        style = 'List Number' if ordered else 'List Bullet'
        for item in items:
            doc.add_paragraph(item, style=style)


def edit_docx(input_path: str, output_path: str, operations: list):
    """Edit a Word document with specified operations."""
    doc = Document(input_path)
    
    for operation in operations:
        apply_operation(doc, operation)
    
    doc.save(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Edit Word documents')
    parser.add_argument('--file', required=True, help='Input Word document')
    parser.add_argument('--output', required=True, help='Output file path')
    parser.add_argument('--operations', required=True, help='JSON array of edit operations')
    
    args = parser.parse_args()
    
    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        operations = json.loads(args.operations)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid operations JSON - {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = edit_docx(args.file, args.output, operations)
        
        output = {
            "status": "success",
            "data": {
                "file": result
            },
            "message": "Successfully edited document"
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
