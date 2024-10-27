from flask import Flask, request, render_template, jsonify, redirect, url_for
import psycopg2
from psycopg2 import Error
import time

app = Flask(__name__)

# Dictionary, um die Zeit zu speichern, zu der ein Like für eine bestimmte URL vergeben wurde
like_times = {}

def get_db_connection():
    connection = psycopg2.connect(
        host='localhost',
        database='browser_engine',
        user='your_username',
        password='your_password'
    )
    return connection

@app.route('/', methods=['GET', 'POST'])
def search():
    results = []
    query_time = 0
    message = None
    total_results = 0
    per_page = 10  # Number of results per page
    page = request.args.get('page', 1, type=int)
    query = ""

    if request.method == 'POST':
        query = request.form['query'].strip()
        return redirect(url_for('search', query=query, page=1))
    else:
        query = request.args.get('query', '').strip()

    start_time = time.time()
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        if query == "#all":
            cursor.execute("SELECT COUNT(*) FROM meta_data")
            total_results = cursor.fetchone()[0]
            cursor.execute("""
                SELECT url, title, description, likes, image
                FROM meta_data
                ORDER BY likes DESC
                LIMIT %s OFFSET %s
            """, (per_page, (page - 1) * per_page))
        elif query:
            search_query = ' & '.join(query.split())
            cursor.execute("""
                SELECT COUNT(*) FROM meta_data
                WHERE to_tsvector(title || ' ' || url) @@ to_tsquery(%s)
            """, (search_query,))
            total_results = cursor.fetchone()[0]

            if total_results == 0:
                total_results = 0
                all_results = []
                for word in query.split():
                    word_pattern = f"%{word}%"
                    cursor.execute("""
                        SELECT url, title, description, likes, image
                        FROM meta_data
                        WHERE title LIKE %s OR url LIKE %s
                        ORDER BY likes DESC
                        LIMIT %s OFFSET %s
                    """, (word_pattern, word_pattern, per_page, (page - 1) * per_page))
                    results = cursor.fetchall()
                    all_results.extend(results)
                results = all_results
                total_results = len(results)
            else:
                cursor.execute("""
                    SELECT url, title, description, likes, image
                    FROM meta_data
                    WHERE to_tsvector(title || ' ' || url) @@ to_tsquery(%s)
                    ORDER BY likes DESC
                    LIMIT %s OFFSET %s
                """, (search_query, per_page, (page - 1) * per_page))
                results = cursor.fetchall()
        else:
            cursor.execute("""
                SELECT url, title, description, image
                FROM meta_data
                ORDER BY random()
                LIMIT 10
            """)
            results = cursor.fetchall()
        cursor.close()
        connection.close()
    except Error as e:
        print(f'Error: {e}')
    query_time = time.time() - start_time
    return render_template('search.html', results=results, query_time=query_time, message=message, total_results=total_results, page=page, per_page=per_page, query=query)

@app.route('/suggest', methods=['POST'])
def suggest():
    try:
        data = request.get_json()
        query = data['query'].strip()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT url, title
            FROM meta_data
            WHERE title LIKE %s
            LIMIT 5
        """, ('%' + query + '%',))
        
        suggestions = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({'suggestions': suggestions})
    
    except Error as e:
        print(f'Error: {e}')
        return jsonify({'suggestions': []})

@app.route('/like', methods=['POST'])
def like():
    data = request.json
    url = data.get('url')
    current_time = time.time()
    if url:
        try:
            if url in like_times and current_time - like_times[url] < 60:
                return jsonify({'success': False, 'message': 'You can only like once per minute.'}), 400
            like_times[url] = current_time
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE meta_data
                SET likes = likes + 1
                WHERE url = %s
            """, (url,))
            connection.commit()
            cursor.close()
            connection.close()
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
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT DISTINCT title
                FROM meta_data
                WHERE title LIKE %s
                LIMIT 10
            """, (f"%{term}%",))
            results = [row[0] for row in cursor.fetchall()]
            cursor.close()
            connection.close()
            return jsonify(results)
        except Error as e:
            print(f'Error: {e}')
    return jsonify([])

@app.route('/check_single_result', methods=['GET'])
def check_single_result():
    term = request.args.get('term')
    if term:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM meta_data
                WHERE title = %s
            """, (term,))
            count = cursor.fetchone()[0]
            if count == 1:
                cursor.execute("""
                    SELECT url FROM meta_data
                    WHERE title = %s
                """, (term,))
                single_result_url = cursor.fetchone()[0]
                cursor.close()
                connection.close()
                return jsonify({'has_single_result': True, 'single_result_url': single_result_url})
            else:
                cursor.close()
                connection.close()
                return jsonify({'has_single_result': False})
        except Error as e:
            print(f'Error: {e}')
    return jsonify({'has_single_result': False})

if __name__ == '__main__':
    app.run(debug=True)
