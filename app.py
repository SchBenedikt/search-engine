from flask import Flask, request, render_template, jsonify, redirect, url_for
from pymongo import MongoClient
import time

app = Flask(__name__)

# Dictionary, um die Zeit zu speichern, zu der ein Like für eine bestimmte URL vergeben wurde
like_times = {}

def get_db_connection():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['search_engine']
        return db
    except Exception as e:
        print(f'Error: {e}')
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
        return redirect(url_for('search', query=query, page=1))
    else:
        query = request.args.get('query', '').strip()

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
                search_query = {"$or": [{"title": {"$regex": query, "$options": "i"}}, {"url": {"$regex": query, "$options": "i"}}]}
                total_results = collection.count_documents(search_query)

                if total_results > 0:
                    results = list(collection.find(search_query).sort("likes", -1).skip((page - 1) * per_page).limit(per_page))
                else:
                    message = "No results found."
            else:
                results = list(collection.aggregate([{"$sample": {"size": 10}}]))

    except Exception as e:
        print(f'Error: {e}')

    query_time = time.time() - start_time
    return render_template('search.html', results=results, query_time=query_time, message=message, total_results=total_results, page=page, per_page=per_page, query=query)

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
    if term:
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

if __name__ == '__main__':
    app.run(debug=True)
