import os
import time
import json
import logging
import requests  # Import requests library
import re  # Import für reguläre Ausdrücke
import wikipedia  # Import Wikipedia library for knowledge panel
from urllib.parse import urlparse, urlunparse  # Import für URL-Parsing
import idna  # Für die Verarbeitung von internationalisierten Domainnamen
from bs4 import BeautifulSoup  # Für besseres HTML-Parsing und Extraktion von <p>-Tags
from flask import Flask, request, render_template, jsonify, redirect, url_for, render_template_string, session
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
        lang = request.args.get('lang', 'de-DE')  # Default to German if not specified
        default_system_instruction = f"Bitte antworte in {lang}. Zeige Quellen, wenn du im Internet suchst. Du bist ein Assitant für eine Suchmaschine und zeigst bei einer Anfrage so viele Informationen wie möglich"
        
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
app.secret_key = os.environ.get('SECRET_KEY', 'defaultsecretkey_change_this_in_production')  # Sitzungsschlüssel hinzufügen

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

# New functions for the .env file
def get_env_variables():
    """Reads values from the .env file"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    env_vars = {}
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    return env_vars

def update_env_file(updates):
    """Updates the .env file with new values"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Read current environment variables from the file
    current_env = []
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            current_env = f.readlines()
    
    # Create a map for easy access to current values
    updated_lines = []
    updated_keys = set()
    
    # Update existing lines
    for line in current_env:
        line = line.rstrip('\n')
        # Keep comments and empty lines
        if not line or line.startswith('#'):
            updated_lines.append(line)
            continue
            
        if '=' in line:
            key = line.split('=', 1)[0].strip()
            if key in updates:
                updated_lines.append(f"{key}={updates[key]}")
                updated_keys.add(key)
            else:
                updated_lines.append(line)
    
    # Add new values that are not already in the file
    for key, value in updates.items():
        if key not in updated_keys:
            updated_lines.append(f"{key}={value}")
    
    # Write the file back with updated values
    with open(env_path, 'w') as f:
        for line in updated_lines:
            f.write(line + '\n')

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
    # Get API key and CX from environment variables
    api_key = os.environ.get('GOOGLE_API_KEY')
    cx = os.environ.get('GOOGLE_CX')
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
        
        # Generate related search terms if we have an original query
        related_search_terms = generate_related_search_terms(original_query)
    
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
        # Generate a hash of the query to use as an identifier
        query_hash = hashlib.md5(original_query.encode()).hexdigest()
        # Create the URL for fetching the AI response
        ai_response_url = f"/get_ai_response?query={original_query}&hash={query_hash}"
    # Default empty list for related search terms
    related_search_terms = [] if 'related_search_terms' not in locals() else related_search_terms
    
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
                          knowledge_panel=knowledge_panel,  # Pass knowledge panel data to template
                          related_search_terms=related_search_terms)  # Pass related search terms for display

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
    # API-Konfigurationen aus der .env-Datei lesen
    env_vars = get_env_variables()
    
    # Übergibt die Synonyme und API-Konfigurationen an das Template
    return render_template('settings.html', 
                           type_synonyms=json.dumps(type_synonyms, indent=2),
                           google_api_key=env_vars.get('GOOGLE_API_KEY', ''),
                           google_cx=env_vars.get('GOOGLE_CX', ''),
                           gemini_api_key=env_vars.get('GEMINI_API_KEY', ''),
                           results_per_page=os.environ.get('RESULTS_PER_PAGE', '10'))

@app.route('/save-settings', methods=['POST'])
def save_settings():
    data = request.get_json()
    db_url = data.get('db_url')
    db_name = data.get('db_name', 'search_engine')
    db_username = data.get('db_username')
    db_password = data.get('db_password')
    
    # Extract API configurations from form data
    google_api_key = data.get('google_api_key', '')
    google_cx = data.get('google_cx', '')
    gemini_api_key = data.get('gemini_api_key', '')
    results_per_page = data.get('results_per_page', '10')
    
    # Save type synonyms if provided
    type_synonyms = data.get('type_synonyms')
    if type_synonyms:
        try:
            # Expects a valid JSON string
            parsed = json.loads(type_synonyms)
            with open('type_synonyms.json', 'w') as f:
                json.dump(parsed, f)
        except Exception as e:
            print(f"Error saving type synonyms: {e}")
            return jsonify({'success': False, 'message': 'Error saving type synonyms'})
    
    # Save API configurations to .env file
    try:
        env_updates = {}
        if google_api_key:
            env_updates['GOOGLE_API_KEY'] = google_api_key
        if google_cx:
            env_updates['GOOGLE_CX'] = google_cx
        if gemini_api_key:
            env_updates['GEMINI_API_KEY'] = gemini_api_key
        if results_per_page:
            env_updates['RESULTS_PER_PAGE'] = results_per_page
        
        # Update .env file
        if env_updates:
            update_env_file(env_updates)
            # Update current environment variables
            for key, value in env_updates.items():
                os.environ[key] = value
    except Exception as e:
        print(f"Error saving .env file: {e}")
        return jsonify({'success': False, 'message': f'Error saving .env file: {str(e)}'})
            
    if db_url:
        connections = get_db_config()
        connections.append({'url': db_url, 'name': db_name, 'username': db_username, 'password': db_password})
        save_db_config(connections)
        return jsonify({'success': True})
    return jsonify({'success': True})

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

# Function to fetch website content
@app.route('/fetch-website-content', methods=['POST'])
def fetch_website_content():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL nicht angegeben'})
    
    try:
        # Fetch website content without saving to database
        website_content = fetch_and_extract_content(url)
        
        # Store content in session for later use
        if 'website_contents' not in session:
            session['website_contents'] = {}
        
        session['website_contents'][url] = {
            'content': website_content,
            'timestamp': time.time()
        }
        
        # Return the extracted content to display in the UI
        return jsonify({
            'success': True, 
            'extracted_content': website_content[:10000]  # Limit to first 10000 chars for UI display
        })
    except Exception as e:
        logging.error(f"Error fetching website content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Function to chat with AI about website content
@app.route('/chat-with-website', methods=['POST'])
def chat_with_website():
    data = request.get_json()
    url = data.get('url')
    user_message = data.get('message')
    
    if not url or not user_message:
        return jsonify({'success': False, 'error': 'URL oder Nachricht nicht angegeben'})
    
    try:
        # Check if content is in session, otherwise fetch it
        website_content = None
        if 'website_contents' in session and url in session['website_contents']:
            stored_data = session['website_contents'][url]
            # Use cached content if it's less than 1 hour old
            if time.time() - stored_data.get('timestamp', 0) < 3600:
                website_content = stored_data.get('content', '')
        
        # If content is not in session or too old, fetch it again
        if not website_content:
            website_content = fetch_and_extract_content(url)
        
        # Generate AI response based on website content and user message
        ai_response = chat_with_ai_about_website(website_content, user_message, url)
        
        return jsonify({
            'success': True,
            'response': ai_response
        })
    except Exception as e:
        logging.error(f"Error chatting with AI: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

# Helper function to fetch and extract content from a website
def fetch_and_extract_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Use BeautifulSoup to extract content from <p> tags
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from all paragraph tags
        paragraphs = soup.find_all('p')
        
        # If no paragraphs found, use basic extraction as fallback
        if not paragraphs:
            # Basic HTML content extraction as fallback
            content = response.text
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content).strip()
        else:
            # Extract and join text from all paragraph tags
            p_contents = [p.get_text().strip() for p in paragraphs]
            content = "\n\n".join(p_contents)
            
        # Remove extra whitespace
        content = re.sub(r'\s{3,}', '\n\n', content).strip()
        
        # Truncate if too large
        max_length = 50000  # Approximate token limit for AI context
        if len(content) > max_length:
            content = content[:max_length] + "... [Content truncated due to length]"
        
        return content
    except Exception as e:
        logging.error(f"Error fetching content from {url}: {str(e)}")
        raise Exception(f"Fehler beim Abrufen des Website-Inhalts: {str(e)}")

# Helper function to generate an AI response about the website content
def chat_with_ai_about_website(website_content, user_message, url):
    try:
        # Create a client with API key
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
        )
        
        model = "gemini-2.0-flash"  # Using a more capable model for content analysis
        
        # Parse the domain for context
        domain = urlparse(url).netloc
        
        # Create a prompt that provides the website content and sets context
        system_prompt = f"""Sie sind ein hilfreicher KI-Assistent, der Fragen über den Inhalt einer Website beantwortet.
        
        Die Frage des Benutzers bezieht sich auf den Inhalt der Website: {domain}
        
        Bitte beantworten Sie die Frage basierend auf diesen Website-Inhalten. Wenn die Antwort nicht in den Website-Inhalten zu finden ist, sagen Sie ehrlich, dass Sie die Information dort nicht finden können.
        
        Website-Inhalte:
        {website_content[:50000]}
        """
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=system_prompt),
                ],
            ),
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=user_message),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
            system_instruction=system_prompt
        )
        
        response = client.models.generate_content(
            model=model,
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=user_message),
                    ],
                ),
            ],
            config=generate_content_config,
        )
        
        # Extract and return the text response
        ai_response = response.text
        
        return ai_response
    except Exception as e:
        logging.error(f"Error generating AI response for website content: {str(e)}")
        raise Exception(f"Fehler bei der KI-Antwort: {str(e)}")

# Function to generate related search terms using AI or fallback to predefined suggestions
def generate_related_search_terms(query):
    """
    Generates related search terms for a given query using the Gemini AI.
    Falls back to rule-based suggestions if the API key is missing.
    Returns a list of related search terms.
    """
    if not query or query == "#all":
        return []
    
    # Check if Gemini API key is available
    api_key = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
    if not api_key:
        # Fallback to rule-based related terms when API key is missing
        return generate_fallback_search_terms(query)
    
    try:
        # Create a client with API key
        client = genai.Client(api_key=api_key)
        
        model = "gemini-2.0-flash"  # Using a faster model for quick responses
        
        # Create a prompt that asks for related search terms
        prompt = f"""Based on the search query "{query}", provide exactly 6 related search terms that users might be interested in.
        These should be highly relevant to the original query but add useful variations or specifications.
        Format your response as a simple list of terms only, one per line, with no explanations or numbering.
        Do not repeat the exact original query in your suggestions."""
        
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]
        
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )
        
        # Generate content using the model
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        # Parse the response into a list of search terms
        related_terms = []
        if response.text:
            # Split by newlines and clean up
            related_terms = [term.strip() for term in response.text.split('\n') if term.strip()]
            # Limit to 6 terms
            related_terms = related_terms[:6]
            
        return related_terms
    except Exception as e:
        logging.error(f"Error generating related search terms: {e}")
        return generate_fallback_search_terms(query)

# Function to generate fallback search term suggestions without requiring API access
def generate_fallback_search_terms(query):
    """
    Generates related search terms using simple pattern matching when AI API is not available.
    """
    query = query.lower().strip()
    
    # Common suffixes to add to search queries
    common_suffixes = [
        "installation", "tutorial", "guide", "download", "alternatives", "vs", 
        "how to use", "setup", "configuration", "examples", "pricing"
    ]
    
    # Common prefixes to add to search queries
    common_prefixes = [
        "best", "how to", "what is", "why use", "compare", "install"
    ]
    
    results = []
    
    # Add some suffixes
    for suffix in common_suffixes[:3]:
        if f"{query} {suffix}" != query:
            results.append(f"{query} {suffix}")
    
    # Add some prefixes
    for prefix in common_prefixes[:3]:
        if f"{prefix} {query}" != query:
            results.append(f"{prefix} {query}")
    
    # If we don't have enough suggestions, add more generic ones
    if len(results) < 6:
        if "open source" not in query and len(results) < 6:
            results.append(f"{query} open source")
        if "alternative" not in query and len(results) < 6:
            results.append(f"{query} alternatives")
        if "review" not in query and len(results) < 6:
            results.append(f"{query} review")
    
    # Return up to 6 suggestions
    return results[:6]

@app.route('/get_page_summary', methods=['GET'])
def get_page_summary():
    """
    Fetches and summarizes the content of a webpage.
    Returns a JSON response with summary and metadata.
    """
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400

    try:
        # Fetch the webpage content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(['script', 'style', 'meta', 'link', 'header', 'footer', 'nav']):
            script_or_style.decompose()
        
        # Get the page title
        title = soup.title.string if soup.title else "No title found"
        
        # Extract text from paragraphs, prioritizing main content
        paragraphs = []
        
        # Try to find main content area (common containers for main content)
        main_content = soup.find('main') or soup.find('article') or soup.find(id='content') or soup.find(class_='content')
        
        if main_content:
            paragraphs = [p.get_text().strip() for p in main_content.find_all('p') if p.get_text().strip()]
        
        # If no paragraphs found in main content, look in the whole document
        if not paragraphs:
            paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
        
        # Limit to first few paragraphs for summary
        content = " ".join(paragraphs[:5])
        
        # Ensure content isn't too long
        if len(content) > 1000:
            content = content[:997] + "..."
        
        # If content is still short, add more text from headers
        if len(content) < 200:
            headers_text = [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3']) if h.get_text().strip()]
            content = " ".join(headers_text + [content])
        
        # If we have a Gemini API key, generate a summary
        api_key = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_GENAI_API_KEY"))
        summary = ""
        
        if api_key and content:
            try:
                # Create a client with API key
                client = genai.Client(api_key=api_key)
                
                # Create a prompt for summarizing
                prompt = f"Summarize this webpage content in 2-3 sentences: {content}"
                
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt),
                        ],
                    ),
                ]
                
                generate_content_config = types.GenerateContentConfig(
                    response_mime_type="text/plain",
                )
                
                # Generate content using the model
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=generate_content_config,
                )
                
                summary = response.text
            except Exception as e:
                logging.error(f"Error generating AI summary: {e}")
                summary = ""
        
        # If AI summary failed or no API key, use the first paragraph as summary
        if not summary and paragraphs:
            summary = paragraphs[0]
            if len(summary) > 200:
                summary = summary[:197] + "..."
        
        # Get favicon if available
        favicon_url = get_favicon_url(url)
        
        return jsonify({
            'success': True,
            'title': title,
            'summary': summary or "No summary available.",
            'favicon': favicon_url,
            'url': url
        })
    
    except Exception as e:
        logging.error(f"Error fetching page summary for {url}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5560)
if __name__ != '__main__':
    app = app
