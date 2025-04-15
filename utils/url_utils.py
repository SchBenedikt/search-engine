import logging
import idna
from urllib.parse import urlparse, urlunparse
import favicon

# Favicon-Cache
favicon_cache = {}

def normalize_url(url):
    """
    Normalisiert eine URL, um Duplikate zu erkennen.
    - Entfernt Trailing-Slashes
    - Konvertiert IDN-Domains zu ASCII
    - Normalisiert das Schema (http/https)
    """
    if not url:
        return ''
    
    # URL parsen
    try:
        parsed_url = urlparse(url)
        
        # Wenn kein Schema vorhanden ist, füge http:// hinzu
        if not parsed_url.scheme:
            url = 'http://' + url
            parsed_url = urlparse(url)
            
        # Hostname zu ASCII konvertieren (für IDN-Domains)
        hostname = parsed_url.netloc
        try:
            # Wenn es sich um einen internationalisierten Domainnamen handelt
            if any(ord(c) > 127 for c in hostname):
                hostname = hostname.encode('idna').decode('ascii')
        except Exception as e:
            logging.error(f"IDN conversion error for {hostname}: {e}")
        
        # Path normalisieren - Trailing-Slashes entfernen, außer wenn der Pfad nur aus / besteht
        path = parsed_url.path
        if path.endswith('/') and len(path) > 1:
            path = path[:-1]
            
        # URL neu zusammensetzen
        normalized = urlunparse((
            parsed_url.scheme,
            hostname,
            path,
            parsed_url.params,
            parsed_url.query,
            ''  # Fragment entfernen
        ))
        
        return normalized
    except Exception as e:
        logging.error(f"URL normalization error for {url}: {e}")
        return url  # Im Fehlerfall Original-URL zurückgeben

def get_favicon_url(url):
    if url in favicon_cache:
        return favicon_cache[url]
    try:
        icons = favicon.get(url)
        if icons:
            favicon_cache[url] = icons[0].url
            return icons[0].url
    except Exception as e:
        logging.error(f'Error fetching favicon for {url}: {e}')
    return None
