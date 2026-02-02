#!/usr/bin/env python3
"""
Fetch HTML content from a URL.

This tool makes an HTTP GET request to the specified URL.
WARNING: ONLY use this tool if the user has provided a specific, real URL.
DO NOT hallucinate or make up URLs (like example.com or placeholders).
If the user asks to "build a website" without a URL, do NOT use this tool.

Usage:
    python fetch_page.py --url https://example.com

Exit Codes:
    0 - Success
    1 - Network error or invalid URL
"""

import argparse
import sys

import json

try:
    import requests
except ImportError:
    print(json.dumps({
        "status": "error", 
        "error": "'requests' package is required. Install with: pip install requests",
        "message": "Missing dependency"
    }))
    sys.exit(1)


def fetch_page(url: str, timeout: int = 30) -> str:
    """
    Fetch the HTML content from a URL.
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        The HTML content as a string
        
    Raises:
        requests.RequestException: If the request fails
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    return response.text


def main():
    parser = argparse.ArgumentParser(
        description='Fetch HTML content from a URL',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python fetch_page.py --url https://example.com
    python fetch_page.py --url https://example.com --timeout 60
        '''
    )
    parser.add_argument(
        '--url',
        required=True,
        help='The URL to fetch'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--output',
        help='Optional path to save the HTML content to a file'
    )
    
    args = parser.parse_args()
    
    try:
        html = fetch_page(args.url, args.timeout)
        
        result = {
            "status": "success",
            "data": html,
            "message": "Successfully fetched page"
        }

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html)
            result["data"] = args.output
            result["message"] = f"Successfully saved content to {args.output}"
            
        # Reconfigure stdout to use UTF-8 to handle non-ASCII characters on Windows
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print(json.dumps(result, ensure_ascii=False))
            
    except requests.exceptions.MissingSchema:
        print_json_error("Invalid URL format. Make sure to include http:// or https://", 1)
    except requests.exceptions.ConnectionError:
        print_json_error(f"Failed to connect to {args.url}", 1)
    except requests.exceptions.Timeout:
        print_json_error(f"Request timed out after {args.timeout} seconds", 1)
    except requests.exceptions.HTTPError as e:
        print_json_error(f"HTTP {e.response.status_code} - {e.response.reason}", 1)
    except requests.exceptions.RequestException as e:
        print_json_error(f"{e}", 1)
    except Exception as e:
        print_json_error(f"Unexpected error: {e}", 1)

def print_json_error(message, exit_code):
    result = {
        "status": "error",
        "error": message,
        "message": message
    }
    # Use utf-8 encoding for stdout
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
