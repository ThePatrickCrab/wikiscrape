import argparse
import bs4
import json
import re
import requests
import sys
import traceback

from pathlib import Path
from typing import Iterator, Optional
from urllib.parse import urlparse

def get_page(page_url: str, use_cache: bool = True) -> Optional[bytes]:
    '''Get desired page via HTTP GET request, or from a cached file if
    requested. Caches any pages retrieved via HTTP GET.
    '''
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

def interesting_links(soup: bs4.BeautifulSoup, base_url: str) -> Iterator[str]:
    '''Get the set of internal links which reside within <li> tags.
    '''
    links = []
    for li_tags in soup.find_all('li'):
        a_tags = li_tags.find_all('a', href=True)
        for a_tag in a_tags:
            if a_tag['href'].startswith('/wiki'):
                links.append(base_url + a_tag['href'])
    return set(links)

def get_name(article: bs4.element.Tag) -> Optional[str]:
    tag = article.find('h1')
    if tag is None:
        return None
    return tag.content

def get_paradigm(infobox: bs4.element.Tag) -> Optional[str]:
    try:
        return infobox.find('th', text='Paradigm').next_sibling.text
    except:
        return None

def get_first_appeared(infobox: bs4.element.Tag) -> Optional[str]:
    try:
        return infobox.find('th', text=re.compile(r'First\sappeared')).next_sibling.text
    except:
        return None

def get_file_extensions(infobox: bs4.element.Tag) -> Optional[str]:
    try:
        return infobox.find('th', text=re.compile(r'Filename\sextensions')).next_sibling.text
    except:
        return None

def count_headers(article: bs4.element.Tag) -> int:
    return len(article.find_all('h2'))

def count_internal_links(article: bs4.element.Tag) -> int:
    return len(article.find_all('a', href=re.compile(r'^/wiki/')))

def get_language_data(page_url: str, use_cache: bool = True) -> Optional[dict]:
    '''Return a data dictionary if the page has Paradigm, First
    Appeared, and File Extensions in its infobox.
    '''
    lang_soup = bs4.BeautifulSoup(get_page(page_url, use_cache), 'html.parser')

    infobox = lang_soup.find('table', class_='infobox')
    article = lang_soup.find('div', id='bodyContent')
    if infobox is None or article is None:
        print(f'[INFO] Infobox or article not found for: {page_url}')
        return None

    name = get_name(article)
    if name is None:
        name = page_url.split('/')[-1]

    data = {
        'name': name,
        'url': page_url,
        'paradigm': get_paradigm(infobox),
        'first_appeared': get_first_appeared(infobox),
        'file_extensions': get_file_extensions(infobox),
        'header_sections': count_headers(article),
        'internal_links': count_internal_links(article)
    }
    
    if data['paradigm'] is None or data['first_appeared'] is None or data['file_extensions'] is None:
        print(f'[INFO] Not enough info for: {name}')
        return None
    print(f'[INFO] Appending info for: {name}')
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', action='store_true', help='Determines if cached pages will be loaded in place of HTTP GET requests')

    args = parser.parse_args()

    output_dict = {}
    output_index = Path('index.json')

    lang_url = 'https://en.wikipedia.org/wiki/List_of_programming_languages'
    lang_urlparse = urlparse(lang_url)
    wiki_base_url = lang_urlparse.scheme + '://' + lang_urlparse.netloc
    
    base_soup = bs4.BeautifulSoup(get_page(lang_url, args.c), 'html.parser')

    for link in interesting_links(base_soup, wiki_base_url):
        data = get_language_data(link, args.c)
        if data is not None:
            output_dict[link] = data

    with output_index.open('w') as f_hndl:
        json.dump(output_dict, f_hndl, indent=4)
