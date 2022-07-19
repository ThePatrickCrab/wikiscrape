import argparse
import bs4
import json
import requests
import sys
import traceback

from pathlib import Path
from typing import Iterator, Optional
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

    print(f'[INFO] HTTP GET on: {page_url}')
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

def interesting_links(soup: bs4.BeautifulSoup) -> Iterator[str]:
    '''Generator which provides links that reside within <li> tags
    '''
    for li_tags in soup.find_all('li'):
        a_tags = li_tags.find_all('a', href=True)
        for a_tag in a_tags:
            if a_tag['href'].startswith('#'):
                continue
            yield a_tag['href']

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', help='Determines if cached pages will be loaded in place of HTTP GET requests')

    args = parser.parse_args()

    output_dict = {}
    output_index = Path('index.json')

    prog_lang_url = 'https://en.wikipedia.org/wiki/List_of_programming_languages'
    wiki_netloc = urlparse(prog_lang_url).netloc
    
    base_soup = bs4.BeautifulSoup(get_page(prog_lang_url, args.c), 'html.parser')

    for link in interesting_links(base_soup):
        output_dict[link] = {}

    with output_index.open('w') as f_hndl:
        json.dump(output_dict, f_hndl, indent=4)
