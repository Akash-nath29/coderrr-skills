#!/usr/bin/env python3
"""
Create PDF documents from content specification.

Usage:
    python create_pdf.py --output report.pdf --content '{"elements": [...]}'
"""

import argparse
import sys
import json
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
except ImportError:
    print(json.dumps({
        "status": "error",
        "error": "'reportlab' package is required. Install with: pip install reportlab", 
        "message": "Missing dependency"
    }))
    sys.exit(1)


def create_pdf(output_path: str, content: dict, title: str = None):
    """Create a PDF document from content specification."""
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Add title if provided
    if title:
        story.append(Paragraph(title, styles['Title']))
        story.append(Spacer(1, 0.5 * inch))
    
    # Validate content structure
    if 'elements' not in content:
        raise ValueError("Content must have an 'elements' array. Example: {\"elements\": [{\"type\": \"paragraph\", \"text\": \"...\"}]}")
    
    # Process elements
    for element in content.get('elements', []):
        elem_type = element.get('type', 'paragraph')
        
        if elem_type == 'heading':
            size = element.get('size', 18)
            style = ParagraphStyle('CustomHeading', parent=styles['Heading1'], fontSize=size)
            story.append(Paragraph(element.get('text', ''), style))
            story.append(Spacer(1, 0.2 * inch))
        
        elif elem_type == 'paragraph':
            story.append(Paragraph(element.get('text', ''), styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
        
        elif elem_type == 'list':
            items = element.get('items', [])
            for item in items:
                bullet = "• " if not element.get('ordered') else f"{items.index(item) + 1}. "
                story.append(Paragraph(f"{bullet}{item}", styles['Normal']))
            story.append(Spacer(1, 0.1 * inch))
        
        elif elem_type == 'table':
            headers = element.get('headers', [])
            rows = element.get('rows', [])
            data = [headers] + rows if headers else rows
            
            if data:
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
                story.append(Spacer(1, 0.2 * inch))
        
        elif elem_type == 'page_break':
            story.append(PageBreak())
        
        elif elem_type == 'spacer':
            height = element.get('height', 0.5)
            story.append(Spacer(1, height * inch))
    
    # Validate that we have content to build
    if not story:
        raise ValueError("No content provided - PDF would be empty. Please provide at least one element in the 'elements' array.")
    
    # Warn about minimal content
    text_content = sum(len(elem.get('text', '')) for elem in content.get('elements', []))
    if text_content < 50:
        print(f"Warning: Very little content ({text_content} chars)", file=sys.stderr)
    
    doc.build(story)
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Create PDF documents')
    parser.add_argument('--output', required=True, help='Output PDF file path')
    parser.add_argument('--content', required=True, help='JSON content specification')
    parser.add_argument('--title', help='Document title')
    
    args = parser.parse_args()
    
    # Debug: Show what we received
    print(f"Debug: Received content length: {len(args.content)}", file=sys.stderr)
    if len(args.content) < 100:
        print(f"Debug: Content value: {repr(args.content)}", file=sys.stderr)
    
    # Handle empty content
    content_str = args.content.strip()
    if not content_str:
        print("Error: Content argument is empty", file=sys.stderr)
        sys.exit(1)
    
    try:
        content = json.loads(content_str)
    except json.JSONDecodeError as e:
        # Check for common placeholder patterns from LLMs
        if '[...]' in content_str or '...' in content_str and 'elements' in content_str:
            print("Error: Content contains placeholder text '[...]' instead of actual content.", file=sys.stderr)
            print("The AI model did not generate real content. Please try again or provide actual content.", file=sys.stderr)
        else:
            print(f"Error: Invalid content JSON - {e}", file=sys.stderr)
            print(f"Debug: First 200 chars: {repr(content_str[:200])}", file=sys.stderr)
        sys.exit(1)
    
    try:
        result = create_pdf(args.output, content, args.title)
        
        output = {
            "status": "success",
            "data": {
                "file": result
            },
            "message": "Successfully created PDF"
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
