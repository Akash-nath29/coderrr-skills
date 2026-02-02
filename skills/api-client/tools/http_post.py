#!/usr/bin/env python3
"""
Make HTTP POST requests with JSON body.

This tool makes POST requests to URLs with JSON data and outputs
the response body.

Usage:
    python http_post.py --url https://api.example.com/users --data '{"name": "John"}'

Exit Codes:
    0 - Success
    1 - Invalid arguments or URL
    2 - Network/connection error
    3 - HTTP error (4xx, 5xx)
    4 - Invalid JSON data
"""

import argparse
import sys
import json

try:
    import requests
except ImportError:
    print("Error: 'requests' package is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)


def http_post(url: str, data: dict, headers: dict = None, timeout: int = 30) -> str:
    """
    Make an HTTP POST request with JSON body.
    
    Args:
        url: The URL to request
        data: Dictionary to send as JSON
        headers: Optional additional headers
        timeout: Request timeout in seconds
        
    Returns:
        Response body as string
    """
    default_headers = {
        'User-Agent': 'Coderrr-API-Client/1.0',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    if headers:
        default_headers.update(headers)
    
    response = requests.post(
        url,
        json=data,
        headers=default_headers,
        timeout=timeout
    )
    response.raise_for_status()
    
    return response.text


def main():
    parser = argparse.ArgumentParser(
        description='Make HTTP POST requests with JSON body',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
    python http_post.py --url https://api.example.com/users --data '{"name": "John"}'
    python http_post.py --url https://api.example.com/auth --data '{"user": "admin", "pass": "123"}' --headers '{"X-API-Key": "secret"}'
        '''
    )
    parser.add_argument(
        '--url',
        required=True,
        help='The URL to request'
    )
    parser.add_argument(
        '--data',
        required=True,
        help='JSON string of request body'
    )
    parser.add_argument(
        '--headers',
        help='JSON string of additional headers'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Parse data
    try:
        data = json.loads(args.data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid data JSON - {e}", file=sys.stderr)
        sys.exit(4)
    
    # Parse headers if provided
    headers = None
    if args.headers:
        try:
            headers = json.loads(args.headers)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid headers JSON - {e}", file=sys.stderr)
            sys.exit(1)
    
    try:
        response = http_post(args.url, data, headers, args.timeout)
        
        try:
            # Try to parse response as JSON for the data field
            resp_data = json.loads(response)
        except json.JSONDecodeError:
            resp_data = response

        output = {
            "status": "success",
            "data": resp_data,
            "message": "POST request successful"
        }
        
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        print(json.dumps(output, indent=2))
            
    except Exception as e:
        # Handle HTTP errors specifically if needed, but generic error wrapper works
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
