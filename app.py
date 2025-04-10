import os
import time
import json
import logging
import requests  # Import requests library
import re  # Import für reguläre Ausdrücke
from urllib.parse import urlparse, urlunparse  # Import für URL-Parsing
import idna  # Für die Verarbeitung von internationalisierten Domainnamen
from flask import Flask, request, render_template, jsonify, redirect, url_for
from pymongo import MongoClient, TEXT
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import favicon  # P08ea
from dotenv import load_dotenv  # Importiere dotenv

# .env-Datei laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'

# Download all necessary NLTK resources
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# Initialize stopwords and stemmer
try:
    stop_words = set(stopwords.words('english')).union(set(stopwords.words('german')))
    stemmer = PorterStemmer()
except LookupError as e:
    logging.error(f"NLTK resource error: {e}")
    # Attempt to download missing resources again
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english')).union(set(stopwords.words('german')))
    stemmer = PorterStemmer()

def get_db_config():
    try:
        with open('db_config.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_db_config(connections):
    with open('db_config.json', 'w') as f:
        json.dump(connections, f)

def get_db_connection():
    connections = get_db_config()
    if not connections:
        return None
    try:
        client = MongoClient(connections[0]['url'], username=connections[0].get('username'), password=connections[0].get('password'))
        db = client[connections[0]['name']]
        db['meta_data'].create_index([("title", TEXT), ("url", TEXT)])
        return db
    except Exception as e:
        logging.error(f'Error: {e}')
        return None

# NEW: Helper function to return all DB connections
def get_all_db_connections():
    connections = get_db_config()
    dbs = []
    for conn in connections:
        try:
            client = MongoClient(conn['url'], username=conn.get('username'), password=conn.get('password'))
            db = client[conn['name']]
            db['meta_data'].create_index([("title", TEXT), ("url", TEXT)])
            dbs.append(db)
        except Exception as e:
            logging.error(f"Error connecting to {conn}: {e}")
    return dbs

# Funktion zur Vorverarbeitung der Suchanfrage
def preprocess_query(query):
    words = nltk.word_tokenize(query)
    if not words:
        return ''
    if len(words) > 1:
        processed_words = [stemmer.stem(word) for word in words[:-1] if word.lower() not in stop_words]
        processed_words.append(words[-1])  # Add the last word without stemming
    else:
        processed_words = [words[0]] if words[0].lower() not in stop_words else []
    return ' '.join(processed_words)

favicon_cache = {}  # P7111

def get_favicon_url(url):  # P4019
    if url in favicon_cache:  # P7111
        return favicon_cache[url]  # P7111
    try:
        icons = favicon.get(url)
        if icons:
            favicon_cache[url] = icons[0].url  # P7111
            return icons[0].url
    except Exception as e:
        print(f'Error fetching favicon for {url}: {e}')
    return None

# Neue Hilfsfunktion für Type-Synonyme
def get_type_synonyms():
    try:
        with open('type_synonyms.json', 'r') as f:
            return json.load(f)
    except Exception:
        return {}

# Neue Funktion zur URL-Normalisierung
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

# Function to fetch search results from Google Custom Search API
def fetch_google_results(query):
    api_key = os.getenv('GOOGLE_API_KEY')
    cx = os.getenv('GOOGLE_CX')
    if not api_key or not cx:
        logging.error('Google API key or CX is not set.')
        return []
    
    url = f'https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get('items', [])
    except requests.RequestException as e:
        logging.error(f'Error fetching Google search results: {e}')
        return []

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    message = None
    total_results = 0
    per_page = 10  # Anzahl der Ergebnisse pro Seite
    page = request.args.get('page', 1, type=int)
    query = ""
    selected_type = ""
    selected_lang = ""  # NEW: language filter

    if request.method == 'POST':
        query = request.form['query'].strip()
        selected_type = request.form.get('type', '').strip()  # --> Filterwert aus dem Formular
        selected_lang = request.form.get('lang', '').strip()  # NEW
        query = preprocess_query(query)  # Preprocess the query
        return redirect(url_for('search', query=query, type=selected_type, lang=selected_lang, page=1))
    else:
        query = request.args.get('query', '').strip()
        selected_type = request.args.get('type', '').strip()
        selected_lang = request.args.get('lang', '').strip()  # NEW
        query = preprocess_query(query)  # Preprocess the query

    start_time = time.time()
    categories = []
    try:
        dbs = get_all_db_connections()
        if not dbs:
            message = "No database connections available."
        else:
            # Merge categories from all DBs
            synonyms = get_type_synonyms()
            consolidated = {}
            for db in dbs:
                all_types = db['meta_data'].distinct('type')
                for t in all_types:
                    if t and t.strip() != '' and t.lower() != 'alle':
                        found = False
                        for canon, group in synonyms.items():
                            if t in group:
                                consolidated[canon] = group
                                found = True
                                break
                        if not found:
                            consolidated[t] = [t]
            categories = list(consolidated.keys())

            temp_results = []
            # Query each DB and merge results with total count
            for db in dbs:
                collection = db['meta_data']
                if query == "#all":
                    base_filter = {"$or": [
                        {"title": {"$regex": query, "$options": "i"}},
                        {"url": {"$regex": query, "$options": "i"}}
                    ]}
                    if selected_type:
                        for canon, group in synonyms.items():
                            if selected_type in group:
                                selected_group = group
                                break
                        else:
                            selected_group = [selected_type]
                        base_filter = {"$and": [{"type": {"$in": selected_group}}, base_filter]}
                    if selected_lang:
                        base_filter = {"$and": [{"page_language": selected_lang}, base_filter]}  # NEW
                    db_results = list(collection.find(base_filter))
                    count = collection.count_documents(base_filter)
                elif query:
                    search_query = {"$text": {"$search": query}}
                    if selected_type:
                        for canon, group in synonyms.items():
                            if selected_type in group:
                                selected_group = group
                                break
                        else:
                            selected_group = [selected_type]
                        search_query = {"$and": [search_query, {"type": {"$in": selected_group}}]}
                    if selected_lang:
                        search_query = {"$and": [search_query, {"page_language": selected_lang}]}  # NEW
                    count = collection.count_documents(search_query)
                    db_results = list(collection.find(search_query, {"score": {"$meta": "textScore"}})
                                       .sort([("score", {"$meta": "textScore"})]))
                elif selected_type:
                    for canon, group in synonyms.items():
                        if selected_type in group:
                            selected_group = group
                            break
                    else:
                        selected_group = [selected_type]
                    search_query = {"type": {"$in": selected_group}}
                    if selected_lang:
                        search_query = {"$and": [search_query, {"page_language": selected_lang}]}  # NEW
                    count = collection.count_documents(search_query)
                    db_results = list(collection.find(search_query))
                else:
                    if selected_lang:
                        db_results = list(collection.aggregate([
                            {"$match": {"page_language": selected_lang}},
                            {"$sample": {"size": 10}}
                        ]))  # NEW
                    else:
                        db_results = list(collection.aggregate([{"$sample": {"size": 10}}]))
                    count = len(db_results)

                total_results += count
                temp_results.extend(db_results)
            
            # NEW: Deduplicate results by URL - mit normalisierter URL
            unique_results = []
            seen_urls = set()
            for item in temp_results:
                url = item.get("url")
                if url:
                    normalized_url = normalize_url(url)
                    if normalized_url and normalized_url not in seen_urls:
                        unique_results.append(item)
                        seen_urls.add(normalized_url)
            
            # If using text search, sort merged results by score
            if query:
                unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            # Fetch Google search results - aber nur wenn Suche aktiv ist
            google_items = []
            if query and query != "#all":
                google_results = fetch_google_results(query)
                
                # Bereite Google-Ergebnisse vor
                for idx, item in enumerate(google_results):
                    url = item.get('link')
                    if url:
                        normalized_url = normalize_url(url)
                        if normalized_url and normalized_url not in seen_urls:
                            # Weniger steile Skalierung des Scores für bessere Durchmischung
                            score_boost = 1000 - (idx * 10)  # Linearer Abfall von 1000
                            google_items.append({
                                'title': item.get('title'),
                                'url': url,
                                'description': item.get('snippet'),
                                'source': 'google',  # Markierung für Google-Ergebnisse
                                'score': score_boost
                            })
                            seen_urls.add(normalized_url)
            
            # Lokale Ergebnisse sammeln mit ihren Scores - mit normalisierter URL-Prüfung
            local_items = []
            
            for item in unique_results:
                url = item.get('url')
                if url:
                    # URL wurde bereits bei der ersten Deduplizierung normalisiert
                    # und ist bereits in seen_urls enthalten
                    # Den Original-Score beibehalten, aber mit Faktor multiplizieren
                    score = item.get('score', 0) * 8
                    local_items.append({
                        'title': item.get('title'),
                        'url': url,
                        'description': item.get('description', ''),
                        'source': 'local',
                        'score': score
                    })
            
            # VERBESSERTE DURCHMISCHUNG: Google und lokale Ergebnisse abwechselnd einsortieren
            # Dabei aber die Scores respektieren - Top Google mit Top Lokal abwechseln
            combined_results = []
            
            # Sortiere beide Listen nach Score
            google_items.sort(key=lambda x: x.get('score', 0), reverse=True)
            local_items.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Initiale Werte für die Durchmischung
            max_results = len(google_items) + len(local_items)
            
            # 3:2 Verhältnis für Google:Lokal (mehr Google-Ergebnisse am Anfang)
            ratio_google = 3
            ratio_local = 2
            google_added = 0
            local_added = 0
            
            # Während wir noch Ergebnisse haben
            while google_items or local_items:
                # Füge Google-Ergebnisse hinzu basierend auf dem Verhältnis
                for _ in range(ratio_google):
                    if google_items:
                        combined_results.append(google_items.pop(0))
                        google_added += 1
                    else:
                        break
                
                # Füge lokale Ergebnisse hinzu basierend auf dem Verhältnis
                for _ in range(ratio_local):
                    if local_items:
                        combined_results.append(local_items.pop(0))
                        local_added += 1
                    else:
                        break
                
            # Füge übrig gebliebene Ergebnisse hinzu
            combined_results.extend(google_items)
            combined_results.extend(local_items)
            
            logging.info(f"Google results: {google_added}, Local results: {local_added}")
            
            # Aktualisiere die Gesamtanzahl der Ergebnisse
            total_results = len(combined_results)
            
            # Wende Paginierung an
            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_results)
            
            # Sichere Indizes verwenden
            if start_idx < total_results:
                results = combined_results[start_idx:end_idx]
            else:
                results = []
                
    except Exception as e:
        print(f'Error: {e}')
        logging.error(f'Search error: {e}')

    query_time = time.time() - start_time
    return render_template('search.html', results=results, query_time=query_time, message=message, total_results=total_results, page=page, per_page=per_page, query=query, categories=categories, lang=selected_lang)  # NEW

# Neue Route zum Abruf der in der Datenbank vorhandenen distinct types
@app.route('/types', methods=['GET'])
def get_types():
    try:
        db = get_db_connection()
        if db is not None:
            all_types = db['meta_data'].distinct('type')
            synonyms = get_type_synonyms()
            consolidated = {}
            for t in all_types:
                if t and t.strip() != '' and t.lower() != 'alle':
                    found = False
                    for canon, group in synonyms.items():
                        if t in group:
                            consolidated[canon] = group
                            found = True
                            break
                    if not found:
                        consolidated[t] = [t]
            # Es werden nur die kanonischen Typen zurückgegeben
            types = list(consolidated.keys())
            return jsonify({'types': types})
    except Exception as e:
        print(f'Error retrieving types: {e}')
    return jsonify({'types': []})

@app.route('/favicon', methods=['GET'])
def favicon_api():
    url = request.args.get('url', '')
    if not url:
        return jsonify({'favicon': None}), 400
    favicon_url = get_favicon_url(url)
    return jsonify({'favicon': favicon_url})

@app.route('/suggest', methods=['POST'])
def suggest():
    try:
        data = request.get_json()
        query = data['query'].strip()
        
        db = get_db_connection()
        if db is not None:
            collection = db['meta_data']
            suggestions = list(collection.find(
                {"title": {"$regex": query, "$options": "i"}},
                {"url": 1, "title": 1}
            ).limit(5))
        
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'suggestions': []})

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term')
    if (term):
        try:
            db = get_db_connection()
            if db is not None:
                collection = db['meta_data']
                results = list(collection.find(
                    {"title": {"$regex": term, "$options": "i"}},
                    {"title": 1}
                ).limit(10))
                return jsonify([result['title'] for result in results])
        except Exception as e:
            print(f'Error: {e}')
    return jsonify([])

@app.route('/check_single_result', methods=['GET'])
def check_single_result():
    term = request.args.get('term')
    if term:
        try:
            db = get_db_connection()
            if db is not None:
                collection = db['meta_data']
                count = collection.count_documents({"title": term})
                if count == 1:
                    single_result_url = collection.find_one({"title": term})['url']
                    return jsonify({'has_single_result': True, 'single_result_url': single_result_url})
                else:
                    return jsonify({'has_single_result': False})
        except Exception as e:
            print(f'Error: {e}')
    return jsonify({'has_single_result': False})

@app.route('/test_preprocess', methods=['GET'])
def test_preprocess():
    query = request.args.get('query', '')
    processed_query = preprocess_query(query)
    return jsonify({'original_query': query, 'processed_query': processed_query})

@app.route('/settings', methods=['GET'])
def settings():
    type_synonyms = get_type_synonyms()
    # Übergibt die Synonyme als formatierten JSON-String an das Template
    return render_template('settings.html', type_synonyms=json.dumps(type_synonyms, indent=2))

@app.route('/save-settings', methods=['POST'])
def save_settings():
    data = request.get_json()
    db_url = data.get('db_url')
    db_name = data.get('db_name', 'search_engine')
    db_username = data.get('db_username')
    db_password = data.get('db_password')
    # Speichern der Typ-Synonyme, wenn vorhanden
    type_synonyms = data.get('type_synonyms')
    if type_synonyms:
        try:
            # Erwartet einen gültigen JSON-String
            parsed = json.loads(type_synonyms)
            with open('type_synonyms.json', 'w') as f:
                json.dump(parsed, f)
        except Exception as e:
            print(f"Error saving type synonyms: {e}")
            return jsonify({'success': False, 'message': 'Fehler beim Speichern der Type Synonyms'})
    if db_url:
        connections = get_db_config()
        connections.append({'url': db_url, 'name': db_name, 'username': db_username, 'password': db_password})
        save_db_config(connections)
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/get-db-connections', methods=['GET'])
def get_db_connections():
    connections = get_db_config()
    return jsonify({'connections': connections})

@app.route('/delete-db-connection', methods=['POST'])
def delete_db_connection():
    try:
        os.remove('db_config.json')
        print('Deleted db_config.json file')  # Logging
        return jsonify({'success': True})
    except FileNotFoundError:
        print('db_config.json file not found')  # Logging
        return jsonify({'success': False, 'message': 'File not found'})
    except Exception as e:
        print(f'Error deleting db_config.json file: {e}')  # Logging
        return jsonify({'success': False, 'message': 'Error deleting file'})

@app.route('/delete-db-connection/<int:index>', methods=['POST'])
def delete_single_db_connection(index):
    try:
        connections = get_db_config()
        if 0 <= index < len(connections):
            removed = connections.pop(index)
            save_db_config(connections)
            logging.info(f"Removed connection: {removed}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Index out of range'})
    except Exception as e:
        logging.error(f'Error deleting connection: {e}')
        return jsonify({'success': False, 'message': 'Internal error'})

if __name__ == '__main__':
    app.run()
if __name__ != '__main__':
    app = app
