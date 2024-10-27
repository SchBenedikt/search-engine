from flask import Flask, request, render_template, jsonify, redirect, url_for
import psycopg2
from psycopg2 import sql, Error
import time

app = Flask(__name__)

# Dictionary, um die Zeit zu speichern, zu der ein Like für eine bestimmte URL vergeben wurde
like_times = {}

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host='localhost',
            database='search_engine',
            user='postgres',
            password='admin'
        )
        return connection
    except Error as e:
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
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                if query == "#all":
                    cursor.execute(sql.SQL("""
                        SELECT url, title, description, likes, image
                        FROM meta_data
                        WHERE title ILIKE %s OR url ILIKE %s
                        ORDER BY likes DESC
                        LIMIT %s OFFSET %s
                    """), (search_query, search_query, per_page, (page - 1) * per_page))
                    results = cursor.fetchall()

                elif query:
                    # Verwende LIKE zur Suche nach Titel oder URL
                    search_query = f"%{query}%"
                    cursor.execute(sql.SQL("""
                        SELECT COUNT(*) FROM meta_data
                        WHERE title ILIKE %s OR url ILIKE %s
                    """), (search_query, search_query))
                    total_results = cursor.fetchone()[0]

                    if total_results > 0:
                        cursor.execute(sql.SQL("""
                            SELECT url, title, description, likes, image
                            FROM meta_data
                            WHERE title ILIKE %s OR url ILIKE %s
                            ORDER BY likes DESC
                            LIMIT %s OFFSET %s
                        """), (search_query, search_query, per_page, (page - 1) * per_page))
                        results = cursor.fetchall()
                    else:
                        message = "No results found."
                else:
                    # Fetch 10 random crawled pages when no search term is entered
                    cursor.execute(sql.SQL("""
                        SELECT url, title, description, image
                        FROM meta_data
                        ORDER BY RANDOM()
                        LIMIT 10
                    """))
                    results = cursor.fetchall()

    except Error as e:
        print(f'Error: {e}')

    query_time = time.time() - start_time
    return render_template('search.html', results=results, query_time=query_time, message=message, total_results=total_results, page=page, per_page=per_page, query=query)

@app.route('/suggest', methods=['POST'])
def suggest():
    try:
        data = request.get_json()
        query = data['query'].strip()
        
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL("""
                    SELECT url, title
                    FROM meta_data
                    WHERE title ILIKE %s
                    LIMIT 5
                """), ('%' + query + '%',))
                
                suggestions = cursor.fetchall()
        
        return jsonify({'suggestions': suggestions})
    
    except Error as e:
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
                # Überprüfen, ob ein Like für diese URL innerhalb der letzten Minute vergeben wurde
                if url in like_times and current_time - like_times[url] < 60:
                    return jsonify({'success': False, 'message': 'You can only like once per minute.'}), 400
                like_times[url] = current_time  # Speichern der aktuellen Zeit für die URL
                
                with get_db_connection() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(sql.SQL("""
                            UPDATE meta_data
                            SET likes = likes + 1
                            WHERE url = %s
                        """), (url,))
                        connection.commit()
                
                return jsonify({'success': True, 'message': 'Liked successfully'}), 200
            except Error as e:
                print(f'Error: {e}')
                return jsonify({'success': False, 'message': 'Error liking the link'}), 500
    return jsonify({'success': False, 'message': 'Invalid request'}), 400

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term')
    if term:
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql.SQL("""
                        SELECT DISTINCT title
                        FROM meta_data
                        WHERE title ILIKE %s
                        LIMIT 10
                    """), (f"%{term}%",))
                    results = [row[0] for row in cursor.fetchall()]
                    return jsonify(results)
        except Error as e:
            print(f'Error: {e}')
    return jsonify([])

@app.route('/check_single_result', methods=['GET'])
def check_single_result():
    term = request.args.get('term')
    if term:
        try:
            with get_db_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql.SQL("""
                        SELECT COUNT(*) FROM meta_data
                        WHERE title = %s
                    """), (term,))
                    count = cursor.fetchone()[0]
                    if count == 1:
                        cursor.execute(sql.SQL("""
                            SELECT url FROM meta_data
                            WHERE title = %s
                        """), (term,))
                        single_result_url = cursor.fetchone()[0]
                        return jsonify({'has_single_result': True, 'single_result_url': single_result_url})
                    else:
                        return jsonify({'has_single_result': False})
        except Error as e:
            print(f'Error: {e}')
    return jsonify({'has_single_result': False})

if __name__ == '__main__':
    app.run(debug=True)
