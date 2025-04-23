from flask import render_template, request, redirect, url_for, jsonify, session
import logging
import time
import hashlib
from config import Config
from database import get_db_connection, get_all_db_connections, get_type_synonyms
from utils.text_utils import preprocess_query
from services.search_service import search_databases
from services.web_service import get_knowledge_panel, get_github_organization
from services.ai_service import generate_related_search_terms
from services.crypto_service import get_crypto_panel
from services.weather_service import WeatherService
from services.stackoverflow_service import get_stackoverflow_panel

def init_main_routes(app):
    @app.route('/')
    def index():
        """Display the modern landing page"""
        return render_template('index.html')
    
    @app.route('/search', methods=['GET', 'POST'])
    def search():
        results = []
        message = None
        total_results = 0
        per_page = Config.RESULTS_PER_PAGE
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
        
        # Get knowledge panel information for the original query
        if original_query:
            knowledge_panel = get_knowledge_panel(original_query, selected_lang)
            # Get GitHub organization information
            github_panel = get_github_organization(original_query)
            # Get cryptocurrency information if the query is related to crypto
            crypto_panel = get_crypto_panel(original_query)
            # Get Stack Overflow questions related to the query
            stackoverflow_panel = get_stackoverflow_panel(original_query)
            
            # Get weather information if the query is related to weather
            weather_service = WeatherService()
            weather_panel = None
            if weather_service.is_weather_query(original_query):
                location = weather_service.extract_location(original_query)
                if location:
                    weather_panel = weather_service.get_weather(location)
            
            # Generate related search terms if we have an original query
            related_search_terms = generate_related_search_terms(original_query)
        
        # Perform the search
        results, total_results, query_time, message = search_databases(
            query, selected_type, selected_lang, page, per_page)
        
        # Get all available categories/types
        categories = []
        try:
            dbs = get_all_db_connections()
            if dbs:
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
        except Exception as e:
            logging.error(f"Error getting categories: {e}")
        
        # Instead of generating AI response here, we'll create a resource URL that the frontend can request
        ai_response_url = None
        if original_query and original_query != "#all":
            # Create a unique identifier for this query that can be used to fetch the response later
            query_hash = hashlib.md5(original_query.encode()).hexdigest()
            # Create the URL for fetching the AI response
            ai_response_url = f"/get_ai_response?query={original_query}&hash={query_hash}"
        
        # Default empty list for related search terms
        related_search_terms = [] if 'related_search_terms' not in locals() else related_search_terms
        
        # Setze crypto_panel auf None, falls es nicht existiert
        if 'crypto_panel' not in locals():
            crypto_panel = None
            
        # Set default values for panels that might not exist
        if 'weather_panel' not in locals():
            weather_panel = None
        if 'stackoverflow_panel' not in locals():
            stackoverflow_panel = None
        
        return render_template('search.html', 
                              results=results, 
                              query_time=query_time if 'query_time' in locals() else 0, 
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
                              github_panel=github_panel if 'github_panel' in locals() else None,  # Pass GitHub organization data
                              crypto_panel=crypto_panel,  # Pass cryptocurrency data to template
                              weather_panel=weather_panel,  # Pass weather data to template
                              stackoverflow_panel=stackoverflow_panel,  # Pass Stack Overflow questions
                              related_search_terms=related_search_terms)  # Pass related search terms for display
