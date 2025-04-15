"""
Service zum Abrufen von Kryptowährungsdaten für die Suchmaschine.
Verwendet die CoinGecko API, um aktuelle Preisdaten und Charts zu erhalten.
"""
import requests
import logging
from datetime import datetime, timedelta
import time

# Cache für die API-Anfragen (einfach, um API-Limits zu vermeiden)
_cache = {}
_cache_expiry = {}
CACHE_DURATION = 300  # 5 Minuten Cache-Dauer

# Liste der bekannten Kryptowährungen und ihrer IDs
CRYPTO_KEYWORDS = {
    'bitcoin': 'bitcoin',
    'btc': 'bitcoin',
    'ethereum': 'ethereum',
    'eth': 'ethereum',
    'cardano': 'cardano',
    'ada': 'cardano',
    'solana': 'solana',
    'sol': 'solana',
    'binance coin': 'binancecoin',
    'bnb': 'binancecoin',
    'ripple': 'ripple', 
    'xrp': 'ripple',
    'dogecoin': 'dogecoin',
    'doge': 'dogecoin',
    'polkadot': 'polkadot',
    'dot': 'polkadot',
    'tether': 'tether',
    'usdt': 'tether',
    'litecoin': 'litecoin',
    'ltc': 'litecoin',
    'chainlink': 'chainlink',
    'link': 'chainlink',
    'uniswap': 'uniswap',
    'uni': 'uniswap',
    'bitcoin cash': 'bitcoin-cash',
    'bch': 'bitcoin-cash',
    'stellar': 'stellar',
    'xlm': 'stellar',
    'polygon': 'matic-network',
    'matic': 'matic-network',
    'avalanche': 'avalanche-2',
    'avax': 'avalanche-2'
}

# Farben für verschiedene Kryptowährungen
CRYPTO_COLORS = {
    'bitcoin': '#F7931A',
    'ethereum': '#627EEA',
    'cardano': '#0033AD',
    'solana': '#00FFA3',
    'binancecoin': '#F3BA2F',
    'ripple': '#23292F',
    'dogecoin': '#C3A634',
    'polkadot': '#E6007A',
    'tether': '#26A17B',
    'litecoin': '#345D9D',
    'chainlink': '#2A5ADA',
    'uniswap': '#FF007A',
    'bitcoin-cash': '#8DC351',
    'stellar': '#7D00FF',
    'matic-network': '#8247E5',
    'avalanche-2': '#E84142'
}

def _get_crypto_id(query):
    """
    Erkennt, ob eine Suchanfrage sich auf eine Kryptowährung bezieht und gibt die ID zurück.
    
    Args:
        query (str): Die Suchanfrage des Benutzers.
        
    Returns:
        str: Die CoinGecko-ID der Kryptowährung oder None, falls nicht erkannt.
    """
    query_lower = query.lower().strip()
    
    # Direkte Übereinstimmung
    if query_lower in CRYPTO_KEYWORDS:
        return CRYPTO_KEYWORDS[query_lower]
    
    # Teilweise Übereinstimmung (z.B. "Bitcoin Preis" sollte Bitcoin erkennen)
    for keyword in CRYPTO_KEYWORDS:
        if keyword in query_lower:
            return CRYPTO_KEYWORDS[keyword]
    
    return None

def _api_request(endpoint, params=None):
    """
    Führt eine gecachte API-Anfrage an CoinGecko durch.
    
    Args:
        endpoint (str): Der API-Endpunkt.
        params (dict): Die Abfrageparameter.
        
    Returns:
        dict: Die API-Antwort als Dictionary oder None bei Fehler.
    """
    base_url = "https://api.coingecko.com/api/v3"
    url = f"{base_url}/{endpoint}"
    cache_key = f"{url}:{str(params)}"
    
    # Prüfen, ob im Cache und noch gültig
    now = time.time()
    if cache_key in _cache and _cache_expiry.get(cache_key, 0) > now:
        return _cache[cache_key]
    
    try:
        response = requests.get(url, params=params, timeout=5)
        # API-Limit berücksichtigen (max. 10-30 Anfragen pro Minute)
        time.sleep(0.3)
        
        if response.status_code == 200:
            data = response.json()
            # Im Cache speichern
            _cache[cache_key] = data
            _cache_expiry[cache_key] = now + CACHE_DURATION
            return data
        else:
            logging.error(f"API error: {response.status_code} for {url}")
            return None
    except Exception as e:
        logging.error(f"Error fetching crypto data: {e}")
        return None

def get_crypto_panel(query, currency='usd'):
    """
    Erstellt ein Crypto-Panel für eine Suchanfrage, wenn die Anfrage eine Kryptowährung betrifft.
    
    Args:
        query (str): Die Suchanfrage des Benutzers.
        currency (str): Die Währung für die Preisangabe (Standard: USD).
        
    Returns:
        dict: Ein Dictionary mit den Panel-Daten oder None, wenn keine Kryptowährung erkannt wurde.
    """
    crypto_id = _get_crypto_id(query)
    if not crypto_id:
        return None
    
    # Kryptowährungsdaten abrufen
    coin_data = _api_request(f"coins/{crypto_id}", {
        'localization': 'false',
        'tickers': 'false', 
        'market_data': 'true',
        'community_data': 'false', 
        'developer_data': 'false'
    })
    
    if not coin_data or 'market_data' not in coin_data:
        return None
    
    # Historische Daten für den Chart (7 Tage)
    market_chart = _api_request(f"coins/{crypto_id}/market_chart", {
        'vs_currency': currency,
        'days': '7'
    })
    
    # Währungssymbol basierend auf der gewählten Währung
    currency_symbols = {
        'usd': '$', 
        'eur': '€', 
        'gbp': '£', 
        'jpy': '¥',
        'cny': '¥',
        'krw': '₩',
        'inr': '₹'
    }
    
    # Chart-Daten vorbereiten
    chart_data = None
    if market_chart and 'prices' in market_chart and len(market_chart['prices']) > 0:
        timestamp_data = [entry[0] for entry in market_chart['prices']]
        price_data = [entry[1] for entry in market_chart['prices']]
        
        # Zeitstempel in lesbare Daten konvertieren
        date_labels = []
        for ts in timestamp_data:
            dt = datetime.fromtimestamp(ts/1000)  # Millisekunden in Sekunden
            date_labels.append(dt.strftime('%d.%m %H:%M'))
        
        chart_data = {
            'labels': date_labels,
            'prices': price_data
        }
    
    # Panel-Daten zusammenstellen
    market_data = coin_data['market_data']
    panel = {
        'name': coin_data['name'],
        'symbol': coin_data['symbol'].upper(),
        'icon_url': coin_data.get('image', {}).get('small'),
        'price': market_data['current_price'].get(currency, 0),
        'currency_symbol': currency_symbols.get(currency, '$'),
        'price_change_24h': market_data.get('price_change_percentage_24h', 0),
        'market_cap': market_data.get('market_cap', {}).get(currency, 0),
        'volume_24h': market_data.get('total_volume', {}).get(currency, 0),
        'circulating_supply': market_data.get('circulating_supply', 0),
        'ath': market_data.get('ath', {}).get(currency, 0),
        'description': coin_data.get('description', {}).get('en', ''),
        'website': coin_data.get('links', {}).get('homepage', [''])[0] if coin_data.get('links', {}).get('homepage') else '',
        'explorer': coin_data.get('links', {}).get('blockchain_site', [''])[0] if coin_data.get('links', {}).get('blockchain_site') else '',
        'chart_data': chart_data,
        'color': CRYPTO_COLORS.get(crypto_id, '#F7931A'),
        'source': 'CoinGecko'
    }
    
    return panel
