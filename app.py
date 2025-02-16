from flask import Flask, request, render_template, jsonify, redirect, url_for
from pymongo import MongoClient, TEXT
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import favicon  # P08ea
import os

app = Flask(__name__)

# Dictionary, um die Zeit zu speichern, zu der ein Like für eine bestimmte URL vergeben wurde
like_times = {}

# Lade die Stop-Wörter für Englisch und Deutsch
nltk.download('stopwords')
stop_words = set(stopwords.words('english')).union(set(stopwords.words('german')))
stemmer = PorterStemmer()

def get_db_config():
    try:
        with open('db_config.txt', 'r') as f:
            lines = f.readlines()
            connections = []
            for i in range(0, len(lines), 2):
                db_url = lines[i].strip()
                db_name = lines[i + 1].strip() if i + 1 < len(lines) else 'search_engine'
                connections.append({'url': db_url, 'name': db_name})
            return connections
    except FileNotFoundError:
        return []

def save_db_config(connections):
    with open('db_config.txt', 'w') as f:
        for conn in connections:
            f.write(f"{conn['url']}\n{conn['name']}\n")

def get_db_connection():
    connections = get_db_config()
    if not connections:
        return None
    try:
        client = MongoClient(connections[0]['url'])
        db = client[connections[0]['name']]
        # Stelle sicher, dass der Textindex erstellt wurde
        db['meta_data'].create_index([("title", TEXT), ("url", TEXT)])
        return db
    except Exception as e:
        print(f'Error: {e}')
        return None

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

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    message = None
    total_results = 0
    per_page = 10  # Anzahl der Ergebnisse pro Seite
    page = request.args.get('page', 1, type=int)
    query = ""

    if request.method == 'POST':
        query = request.form['query'].strip()
        query = preprocess_query(query)  # Preprocess the query
        return redirect(url_for('search', query=query, page=1))
    else:
        query = request.args.get('query', '').strip()
        query = preprocess_query(query)  # Preprocess the query

    start_time = time.time()
    try:
        db = get_db_connection()
        if db is not None:
            collection = db['meta_data']
            if query == "#all":
                results = list(collection.find(
                    {"$or": [{"title": {"$regex": query, "$options": "i"}}, {"url": {"$regex": query, "$options": "i"}}]}
                ).sort("likes", -1).skip((page - 1) * per_page).limit(per_page))

            elif query:
                search_query = {"$text": {"$search": query}}
                total_results = collection.count_documents(search_query)

                if total_results > 0:
                    results = list(collection.find(search_query, {"score": {"$meta": "textScore"}})
                                   .sort([("score", {"$meta": "textScore"})])
                                   .skip((page - 1) * per_page).limit(per_page))
                    # Entferne synchrone Favicons: 
                    # for result in results:
                    #     result['favicon'] = get_favicon_url(result['url'])
                else:
                    message = "No results found."
            else:
                results = list(collection.aggregate([{"$sample": {"size": 10}}]))

    except Exception as e:
        print(f'Error: {e}')

    query_time = time.time() - start_time
    return render_template('search.html', results=results, query_time=query_time, message=message, total_results=total_results, page=page, per_page=per_page, query=query)

# Neue API-Route zum asynchronen Abruf des Favicons
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

@app.route('/like', methods=['POST'])
def like():
    if request.method == 'POST':
        data = request.json
        url = data.get('url')
        current_time = time.time()
        if url:
            try:
                if url in like_times and current_time - like_times[url] < 60:
                    return jsonify({'success': False, 'message': 'You can only like once per minute.'}), 400
                like_times[url] = current_time
                
                db = get_db_connection()
                if db is not None:
                    collection = db['meta_data']
                    collection.update_one({"url": url}, {"$inc": {"likes": 1}})
                
                return jsonify({'success': True, 'message': 'Liked successfully'}), 200
            except Exception as e:
                print(f'Error: {e}')
                return jsonify({'success': False, 'message': 'Error liking the link'}), 500
    return jsonify({'success': False, 'message': 'Invalid request'}), 400

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
    return render_template('settings.html')

@app.route('/save-settings', methods=['POST'])
def save_settings():
    data = request.get_json()
    db_url = data.get('db_url')
    db_name = data.get('db_name', 'search_engine')
    if db_url:
        connections = get_db_config()
        connections.append({'url': db_url, 'name': db_name})
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
        os.remove('db_config.txt')
        print('Deleted db_config.txt file')  # Logging
        return jsonify({'success': True})
    except FileNotFoundError:
        print('db_config.txt file not found')  # Logging
        return jsonify({'success': False, 'message': 'File not found'})
    except Exception as e:
        print(f'Error deleting db_config.txt file: {e}')  # Logging
        return jsonify({'success': False, 'message': 'Error deleting file'})

if __name__ == '__main__':
    app.run(debug=True)

if __name__ != '__main__':
    app = app