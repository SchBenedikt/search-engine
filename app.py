from flask import Flask, request, render_template, jsonify, redirect, url_for
import mysql.connector
from mysql.connector import Error
import time
import math

app = Flask(__name__)

# Dictionary, um die Zeit zu speichern, zu der ein Like für eine bestimmte URL vergeben wurde
like_times = {}

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        database='browser_engine',
        user='root',
        password=''
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
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            if query == "#all":
                cursor.execute("SELECT COUNT(*) FROM meta_data")
                total_results = cursor.fetchone()['COUNT(*)']
                cursor.execute("""
                    SELECT url, title, description, likes
                    FROM meta_data
                    ORDER BY likes DESC
                    LIMIT %s OFFSET %s
                """, (per_page, (page - 1) * per_page))
            elif query:
                search_query = f"%{query}%"
                words = query.split()
                regex_pattern = ".*" + ".*".join(words) + ".*"
                cursor.execute("""
                    SELECT COUNT(*) FROM meta_data
                    WHERE title REGEXP %s OR url REGEXP %s
                """, (regex_pattern, regex_pattern))
                total_results = cursor.fetchone()['COUNT(*)']

                if total_results == 0:
                    total_results = 0
                    all_results = []
                    for word in words:
                        word_pattern = f"%{word}%"
                        cursor.execute("""
                            SELECT url, title, description, likes
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
                        SELECT url, title, description, likes
                        FROM meta_data
                        WHERE title REGEXP %s OR url REGEXP %s
                        ORDER BY likes DESC
                        LIMIT %s OFFSET %s
                    """, (regex_pattern, regex_pattern, per_page, (page - 1) * per_page))
                    results = cursor.fetchall()
            else:
                # Fetch the last 10 crawled pages when no search term is entered
                cursor.execute("""
                    SELECT url, title, description
                    FROM meta_data
                    ORDER BY id DESC
                    LIMIT 10
                """)
                results = cursor.fetchall()
            cursor.close()
            connection.close()
    except Error as e:
        print(f'Error: {e}')
    query_time = time.time() - start_time
    return render_template('search.html', results=results, query_time=query_time, message=message, total_results=total_results, page=page, per_page=per_page, query=query)


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
                connection = get_db_connection()
                if connection.is_connected():
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


if __name__ == '__main__':
    app.run(debug=True)
