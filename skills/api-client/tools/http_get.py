#!/usr/bin/env python3
"""
Make HTTP GET requests.

This tool makes GET requests to URLs and outputs the response body.
JSON responses are automatically pretty-printed.

Usage:
    python http_get.py --url https://api.example.com/users
    python http_get.py --url https://api.example.com/users --headers '{"Auth": "token"}'

Exit Codes:
    0 - Success
    1 - Invalid arguments or URL
    2 - Network/connection error
    3 - HTTP error (4xx, 5xx)
"""

import argparse
import sys
import json

try:
    import requests
except ImportError:
    print("Error: 'requests' package is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


def http_get(url: str, headers: dict = None, timeout: int = 30) -> str:
    """
    Make an HTTP GET request.
    
    Args:
        url: The URL to request
        headers: Optional headers dictionary
        timeout: Request timeout in seconds
        
    Returns:
        Response body as string
    """
    default_headers = {
        'User-Agent': 'Coderrr-API-Client/1.0',
        'Accept': 'application/json'
    }
    
    if headers:
        default_headers.update(headers)
    
    response = requests.get(url, headers=default_headers, timeout=timeout)
    response.raise_for_status()
    
    return response.text


def main():
    parser = argparse.ArgumentParser(
        description='Make HTTP GET requests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python http_get.py --url https://api.example.com/users
    python http_get.py --url https://api.example.com/data --headers '{"Authorization": "Bearer token"}'
        '''
    )
    parser.add_argument(
        '--url',
        required=True,
        help='The URL to request'
    )
    parser.add_argument(
        '--headers',
        help='JSON string of headers'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Parse headers if provided
    headers = None
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid headers JSON - {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        response = http_get(args.url, headers, args.timeout)
        
        try:
            # Try to parse response as JSON for the data field
            resp_data = json.loads(response)
        except json.JSONDecodeError:
            resp_data = response

        output = {
            "status": "success",
            "data": resp_data,
            "message": "GET request successful"
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
