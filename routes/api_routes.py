from flask import request, jsonify, session
import logging
import hashlib
import time
from database import get_db_connection, get_type_synonyms
from utils.url_utils import get_favicon_url
from utils.text_utils import preprocess_query
from services.ai_service import generate_ai_response, chat_with_ai_about_website
from services.web_service import fetch_and_extract_content, get_page_summary

def init_api_routes(app):
    """
    Initialisiert alle API-Routen für die Anwendung.
    """
    
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
            logging.error(f'Error retrieving types: {e}')
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
            logging.error(f'Error: {e}')
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
                logging.error(f'Error: {e}')
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
                logging.error(f'Error: {e}')
        return jsonify({'has_single_result': False})
    
    @app.route('/test_preprocess', methods=['GET'])
    def test_preprocess():
        query = request.args.get('query', '')
        processed_query = preprocess_query(query)
        return jsonify({'original_query': query, 'processed_query': processed_query})
    
    @app.route('/get_ai_response', methods=['GET'])
    def get_ai_response():
        query = request.args.get('query', '')
        query_hash = request.args.get('hash', '')
        
        if not query:
            return jsonify({'error': 'Missing query parameter'}), 400
        
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

    @app.route('/get_page_summary', methods=['GET'])
    def get_page_summary_route():
        """
        Fetches and summarizes the content of a webpage.
        Returns a JSON response with summary and metadata.
        """
        url = request.args.get('url')
        if not url:
            return jsonify({'error': 'URL parameter is required'}), 400

        try:
            # Get page summary
            page_data = get_page_summary(url)
            
            # Get favicon if available
            favicon_url = get_favicon_url(url)
            
            # Return combined data
            return jsonify({
                'success': True,
                'title': page_data['title'],
                'summary': page_data['summary'],
                'favicon': favicon_url,
                'url': url
            })
        
        except Exception as e:
            logging.error(f"Error fetching page summary for {url}: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
