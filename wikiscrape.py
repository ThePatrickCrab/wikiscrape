import argparse
import requests
import sys
import traceback

from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

def get_page(page_url: str, use_cache: bool = True) -> Optional[bytes]:
    try:
        url_parse_result = urlparse(page_url)
    except ValueError:
        print(f'[ERROR] Could not parse {page_url}:')
        traceback.print_exc()
        return None

    cache_path = Path(url_parse_result.netloc + url_parse_result.path)
    if use_cache and cache_path.exists():
        print(f'[INFO] Loading cached page: {str(cache_path)}')
        with cache_path.open('rb') as f_hndl:
            return f_hndl.read()

    print(f'[INFO] Performing HTTP GET on: {page_url}')
    try:
        page = requests.get(page_url, timeout=3)
    except Exception:
        print(f'[ERROR] Exception while attempting to GET {page_url}')
        traceback.print_exc()
        return None

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open('wb') as f_hndl:
        f_hndl.write(page.content)

    return page.content

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', help='Determines if cached pages will be loaded in place of HTTP GET requests')
    parser.add_argument('url')

    args = parser.parse_args()

    with open('dummy', 'wb') as f_hndl:
        f_hndl.write(get_page(args.url, args.c))
