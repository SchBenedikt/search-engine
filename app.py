import os
import time
import json
import logging
import requests  # Import requests library
import re  # Import für reguläre Ausdrücke
import wikipedia  # Import Wikipedia library for knowledge panel
from urllib.parse import urlparse, urlunparse  # Import für URL-Parsing
import idna  # Für die Verarbeitung von internationalisierten Domainnamen
from flask import Flask, request, render_template, jsonify, redirect, url_for, render_template_string
from pymongo import MongoClient, TEXT
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import favicon  # P08ea
from dotenv import load_dotenv  # Importiere dotenv
# Updated import for Google Generative AI
from google import genai
from google.genai import types

# .env-Datei laden
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to generate AI response using Google's Gemini model with the correct API
def generate_ai_response(query):
    if not query or query == "#all":
        return "", []
    
    try:
        # Create a client with API key
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
        )
        
        model = "gemini-2.0-flash"  # Using a faster model for quick responses
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=f"Please answer to this: {query}. Please show your sources."),
                ],
            ),
        ]
        
        # Enable Google Search tool
        tools = [
            types.Tool(google_search=types.GoogleSearch())
        ]
        
        # Define default system instruction for the AI
        default_system_instruction = f"Bitte antworte in {request.args.get('lang')}. Zeige Quellen, wenn du im Internet suchst. Du bist ein Assitant für eine Suchmaschine und zeigst bei einer Anfrage so viele Informationen wie möglich"
        
        # Get custom system instruction from query if present (format: #system:instruction)
        system_instruction = default_system_instruction
        if "#system:" in query:
            parts = query.split("#system:", 1)
            if len(parts) > 1:
                query = parts[0].strip()
                # Override default with custom system instruction
                system_instruction = parts[1].strip()
                # Update the user content with the modified query (without the system instruction)
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=f"Please answer this question: {query}. Please show your sources."),
                        ],
                    ),
                ]
        
        generate_content_config = types.GenerateContentConfig(
            tools=tools,
            response_mime_type="text/plain",  # Use supported MIME type
            system_instruction=system_instruction,  # Always add system instruction
        )
        
        # Generate content using the model
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # Extract citation sources from response if available
        sources = []
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'citation_metadata') and candidate.citation_metadata:
                if hasattr(candidate.citation_metadata, 'citations'):
                    for citation in candidate.citation_metadata.citations:
                        if hasattr(citation, 'uri') and citation.uri:
                            source = {
                                'uri': citation.uri,
                                'title': citation.title if hasattr(citation, 'title') else "Source"
                            }
                            sources.append(source)
        
        return response.text, sources  # Return both the text and sources
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        return "Sorry, I couldn't generate a response at this time.", []

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

# Function to preprocess the search query
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

# Function to preprocess the search query returning both versions
def preprocess_query_for_search(query):
    original_query = query  # Keep the original query
    processed_query = preprocess_query(query)  # Process for search
    return original_query, processed_query

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
    # Explicitly set the correct values to ensure they're not swapped
    api_key = 'AIzaSyAHrHt3Zc3YXof5R8kkx3xun9CAkwqM_jY'  # Correct API key from .env
    cx = 'c01b5677e81ae4f00'  # Correct CX from .env
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

def combine_results(local_results, google_results):
    combined_results = []
    seen_urls = set()

    # Add local results first
    for item in local_results:
        url = item.get('url')
        if url:
            normalized_url = normalize_url(url)
            if normalized_url and normalized_url not in seen_urls:
                combined_results.append(item)
                seen_urls.add(normalized_url)

    # Add Google results next
    for idx, item in enumerate(google_results):
        url = item.get('link')
        if url:
            normalized_url = normalize_url(url)
            if normalized_url and normalized_url not in seen_urls:
                score_boost = 1000 - (idx * 10)
                combined_results.append({
                    'title': item.get('title'),
                    'url': url,
                    'description': item.get('snippet'),
                    'source': 'google',
                    'score': score_boost
                })
                seen_urls.add(normalized_url)

    # Sort combined results by score
    combined_results.sort(key=lambda x: x.get('score', 0), reverse=True)
    return combined_results

@app.route('/')
def index():
    """Display the modern landing page"""
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    message = None
    total_results = 0
    per_page = 10  # Number of results per page
    page = request.args.get('page', 1, type=int)
    query = ""
    original_query = ""  # For display
    selected_type = ""
    selected_lang = ""  # Language filter
    knowledge_panel = None  # Initialize knowledge panel variable
    
    # Get browser's preferred language from Accept-Language header
    browser_lang = request.accept_languages.best_match(['en', 'de', 'fr', 'es', 'it']) or 'en'
    # Map short language codes to full codes if needed
    lang_map = {
        'en': 'en-US',
        'de': 'de-DE',
        'fr': 'fr-FR',
        'es': 'es-ES',
        'it': 'it-IT'
    }
    default_lang = lang_map.get(browser_lang, browser_lang)

    if request.method == 'POST':
        original_query = request.form['query'].strip()
        selected_type = request.form.get('type', '').strip()  # --> Filter value from form
        selected_lang = request.form.get('lang', default_lang).strip()  # Use browser lang if not specified
        processed_query = preprocess_query(original_query)  # Keep original and process for search
        return redirect(url_for('search', query=processed_query, original_query=original_query, type=selected_type, lang=selected_lang, page=1))
    else:
        query = request.args.get('query', '').strip()
        original_query = request.args.get('original_query', query).strip()  # Fall back to query if original not provided
        selected_type = request.args.get('type', '').strip()
        selected_lang = request.args.get('lang', default_lang).strip()  # Use browser lang if not specified
        # Don't process the query again - it's already processed from POST request
        # We'll use the query parameter as-is for searching

    start_time = time.time()
    categories = []
    
    # Get knowledge panel information for the original query
    if original_query:
        knowledge_panel = get_knowledge_panel(original_query, selected_lang)
    
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
            
            # Fetch Google search results - but only when search is active
            google_items = []
            if query and query != "#all":
                google_results = fetch_google_results(query)
                
                # Prepare Google results
                for idx, item in enumerate(google_results):
                    url = item.get('link')
                    if url:
                        normalized_url = normalize_url(url)
                        if normalized_url and normalized_url not in seen_urls:
                            # Less steep scaling of the score for better mixing
                            score_boost = 1000 - (idx * 10)  # Linear decrease from 1000
                            google_items.append({
                                'title': item.get('title'),
                                'url': url,
                                'description': item.get('snippet'),
                                'source': 'google',  # Markierung für Google-Ergebnisse
                                'score': score_boost
                            })
                            seen_urls.add(normalized_url)
            
            # Collect local results with their scores - with normalized URL check
            local_items = []
            
            for item in unique_results:
                url = item.get('url')
                if url:
                    # URL was already normalized during the first deduplication
                    # and is already included in seen_urls
                    # Keep the original score but multiply by a factor
                    score = item.get('score', 0) * 8
                    local_items.append({
                        'title': item.get('title'),
                        'url': url,
                        'description': item.get('description', ''),
                        'source': 'local',
                        'score': score
                    })
            
            # IMPROVED MIXING: Interleave Google and local results
            # But respect the scores - alternate top Google with top local results
            combined_results = []
            
            # Sort both lists by score
            google_items.sort(key=lambda x: x.get('score', 0), reverse=True)
            local_items.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            # Initial values for mixing
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
    
    # Instead of generating AI response here, we'll create a resource URL that the frontend can request
    ai_response_url = None
    if original_query and original_query != "#all":
        # Create a unique identifier for this query that can be used to fetch the response later
        import hashlib
        query_hash = hashlib.md5(original_query.encode()).hexdigest()
        ai_response_url = url_for('get_ai_response', query=original_query, hash=query_hash)
    
    return render_template('search.html', 
                          results=results, 
                          query_time=query_time, 
                          message=message, 
                          total_results=total_results, 
                          page=page, 
                          per_page=per_page, 
                          original_query=original_query,  # Pass the original query to display in the search box
                          query=query,  # This is the processed query for search functionality
                          categories=categories, 
                          lang=selected_lang,
                          ai_response_url=ai_response_url,  # Pass URL to fetch AI response instead of the response itself
                          knowledge_panel=knowledge_panel)  # Pass knowledge panel data to template

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

# Function to fetch Wikipedia knowledge panel information for entities
def get_knowledge_panel(query, lang=None):
    """
    Attempts to fetch Wikipedia information for a query to display in a knowledge panel.
    Returns a dictionary with information or None if no suitable information is found.
    
    Parameters:
    - query: The search term
    - lang: Language code for Wikipedia (e.g. 'en', 'de', 'fr')
    """
    if not query or query.startswith('#'):
        return None
    
    # Set default language to English
    wikipedia_lang = 'en'
    
    # Set language based on the user's selected language
    if lang:
        if lang.startswith('de'):
            wikipedia_lang = 'de'
        elif lang.startswith('fr'):
            wikipedia_lang = 'fr'
        elif lang.startswith('es'):
            wikipedia_lang = 'es'
        elif lang.startswith('it'):
            wikipedia_lang = 'it'
        # Add more languages as needed
    
    # Set Wikipedia language
    wikipedia.set_lang(wikipedia_lang)
    
    try:
        # Clean up the query - remove special characters and focus on key terms
        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        
        # Skip short or common queries that are unlikely to be entities
        if len(clean_query.split()) <= 1 and len(clean_query) < 4:
            return None
            
        # Try to search Wikipedia for the term
        search_results = wikipedia.search(clean_query, results=1)
        if not search_results:
            return None
            
        # Get the first result
        page_title = search_results[0]
        
        try:
            # Get the Wikipedia page
            page = wikipedia.page(page_title, auto_suggest=False)
            
            # Extract relevant information
            summary = page.summary
            # Trim summary to a reasonable length if needed
            if len(summary) > 500:
                summary = summary[:500] + "..."
                
            # Create knowledge panel data
            knowledge_panel = {
                'title': page.title,
                'summary': summary,
                'url': page.url,
                'image_url': None,  # Default to None, we'll try to find an image
                'wiki_lang': wikipedia_lang  # Store the language used
            }
            
            # Try to get an image if available
            if page.images:
                for img in page.images:
                    # Look for images that might be relevant (avoid small icons, etc.)
                    if ('logo' in img.lower() or 
                        'photo' in img.lower() or 
                        'image' in img.lower() or 
                        'picture' in img.lower() or
                        page.title.lower() in img.lower()):
                        if not img.endswith('.svg') and not img.endswith('.gif'):
                            knowledge_panel['image_url'] = img
                            break
            
            return knowledge_panel
            
        except wikipedia.exceptions.DisambiguationError as e:
            # If we hit a disambiguation page, try the first option
            if e.options:
                try:
                    page = wikipedia.page(e.options[0], auto_suggest=False)
                    summary = page.summary
                    if len(summary) > 500:
                        summary = summary[:500] + "..."
                    
                    knowledge_panel = {
                        'title': page.title,
                        'summary': summary,
                        'url': page.url,
                        'image_url': None
                    }
                    
                    if page.images:
                        for img in page.images:
                            if ('logo' in img.lower() or 
                                'photo' in img.lower() or 
                                'image' in img.lower() or 
                                'picture' in img.lower() or
                                page.title.lower() in img.lower()):
                                if not img.endswith('.svg') and not img.endswith('.gif'):
                                    knowledge_panel['image_url'] = img
                                    break
                    
                    return knowledge_panel
                except:
                    return None
    except Exception as e:
        logging.error(f"Knowledge panel error: {e}")
        return None
    
    return None

# New endpoint to get AI response asynchronously
@app.route('/get_ai_response', methods=['GET'])
def get_ai_response():
    query = request.args.get('query', '')
    query_hash = request.args.get('hash', '')
    
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    
    # We'll make the hash optional to avoid blocking valid requests
    # Generate AI response
    try:
        ai_response, sources = generate_ai_response(query)
        
        # Create a shortened preview (first 150 characters)
        short_response = ai_response
        if len(ai_response) > 150:
            # Find the last space before the 150 character cut-off to avoid cutting words
            last_space = short_response[:150].rfind(' ')
            if last_space > 0:
                short_response = short_response[:last_space] + '...'
            else:
                short_response = short_response[:150] + '...'
        
        # Create HTML for the response with sources
        ai_response_html = f'<div class="alert alert-primary mb-4 ai-response">'
        ai_response_html += f'<h5 class="alert-heading">AI Response:</h5>'
        ai_response_html += f'<div class="ai-response-preview markdown-body mb-2">{short_response}</div>'
        ai_response_html += f'<div class="ai-response-full markdown-body mb-2" style="display:none;">{ai_response}</div>'
        ai_response_html += f'<button class="btn btn-sm btn-outline-primary ai-expand-btn" onclick="toggleAIResponse(this)">Show more</button>'
        
        # Add sources if available
        if sources:
            ai_response_html += f'<hr><p class="mb-0"><strong>Sources:</strong></p><ul class="mb-0">'
            for source in sources:
                title = source.get('title', 'Source')
                uri = source.get('uri', '#')
                ai_response_html += f'<li><a href="{uri}" target="_blank">{title}</a></li>'
            ai_response_html += '</ul>'
        
        ai_response_html += '</div>'
        
        return jsonify({
            'ai_response': ai_response,
            'sources': sources,
            'ai_response_html': ai_response_html
        })
    except Exception as e:
        logging.error(f"Error generating AI response: {e}")
        return jsonify({
            'ai_response': "Sorry, I couldn't generate a response at this time.",
            'sources': [],
            'ai_response_html': '<div class="alert alert-danger mb-4">Error generating AI response. Please try again.</div>'
        })

# Endpoint for generating webpage summaries
@app.route('/get_page_summary', methods=['GET'])
def get_page_summary():
    from bs4 import BeautifulSoup
    import re
    
    url = request.args.get('url', '')
    
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400
    
    try:
        # Try to fetch content from the URL with more realistic browser headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Cache-Control': 'max-age=0',
        }
        
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
            
        # Get page title
        title = soup.title.string if soup.title else "Keine Überschrift"
        
        # Extract main content (focusing on paragraphs, headings, and lists)
        text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        
        # Get text from each element, remove extra whitespace
        content_text = []
        for element in text_elements:
            text = element.get_text().strip()
            if text and len(text) > 15:  # Filter out very short fragments
                content_text.append(text)
        
        # Limit the amount of text we process (first 5000 chars should be enough for a summary)
        main_content = " ".join(content_text)[:5000]
        
        # Create a clear prompt using the actual page content
        prompt = f"""
        Erstelle eine kurze Zusammenfassung der folgenden Webseite in maximal 100 Wörtern. Wichtig: Schreibe NUR die Zusammenfassung selbst, ohne IRGENDEINE Einleitung wie 'Hier ist eine Zusammenfassung' oder 'Diese Webseite...' oder 'Gerne, hier ist...' oder Ähnliches.
        
        Titel: {title}
        URL: {url}
        Inhalt: {main_content}
        
        Antworten Sie auf {request.args.get('lang')}. Falls der Inhalt zu kurz oder nicht informativ ist, fassen Sie zusammen, was Sie sehen können.
        Beginne sofort mit dem Inhalt der Zusammenfassung. Verzichte auf jegliche Meta-Referenzen zur Aufgabe selbst.
        """
        
        # Generate summary using Gemini AI with the extracted content
        summary, sources = generate_ai_response(prompt)
        
        # Check if we got a "not enough information" type response
        if re.search(r"(I don't have enough information|I'm a large language model|don't have access)", summary, re.IGNORECASE):
            # Try a fallback approach with just the URL and a more specific instruction
            fallback_prompt = f"""
            Du erhältst eine URL: {url}
            
            Bitte analysiere den URL-Pfad und die Domain, um eine kurze Zusammenfassung zu erstellen, worum es auf dieser Webseite gehen könnte.
            Verwende dein Wissen über verschiedene Domains und Website-Strukturen.
            Gib an, dass dies eine Vermutung basierend auf der URL-Struktur ist, nicht auf dem tatsächlichen Inhalt.
            Antworten Sie auf Deutsch in maximal 2-3 Sätzen. Du kannst die Antwort im Markdown-Format gestalten.
            """
            
            summary, sources = generate_ai_response(fallback_prompt)
            
            # Add a disclaimer that this is URL-based only
            summary = f"Basierend auf der URL: {summary}"
        
        # Ergänze Anweisungen für Markdown-Formatierung
        prompt_addendum = f"""
        Formatiere die obige Zusammenfassung in Markdown. Stelle sicher, dass wichtige Begriffe **fett** hervorgehoben sind.
        Die Zusammenfassung sollte prägnant, informativ und gut formatiert sein.
        """
        
        # Diese Zeile auskommentiert, um doppelte API-Anfragen zu vermeiden
        # summary_markdown, _ = generate_ai_response(f"{summary}\n\n{prompt_addendum}")
        # summary = summary_markdown if not re.search(r"(I don't have enough information|I'm a large language model)", summary_markdown, re.IGNORECASE) else summary
            
        return jsonify({
            'success': True,
            'summary': summary,
            'sources': sources
        })
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching URL {url}: {e}")
        return jsonify({
            'success': False,
            'error': 'Die Webseite konnte nicht geladen werden.'
        })
    except Exception as e:
        logging.error(f"Error generating summary for {url}: {e}")
        return jsonify({
            'success': False,
            'error': 'Zusammenfassung konnte nicht erstellt werden.'
        })

if __name__ == '__main__':
    app.run(port=5555)
if __name__ != '__main__':
    app = app
